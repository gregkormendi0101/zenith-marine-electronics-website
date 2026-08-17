#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import http.server
import json
import os
import re
import socket
import threading
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
PREVIEWS = ROOT / ".qa-artifacts"
VIEWPORTS = {
    "mobile-320": (320, 900),
    "mobile-390": (390, 844),
    "tablet-768": (768, 1024),
    "desktop-1440": (1440, 1100),
}
PHONE = "+13053066391"
MEASUREMENT_ID = "G-H8KGT9K2TM"


class Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()
        self.h1_count = 0
        self.images_without_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("id"):
            self.ids.add(data["id"] or "")
        if tag == "h1":
            self.h1_count += 1
        if tag == "img" and "alt" not in data:
            self.images_without_alt += 1
        for key in ("src", "href", "srcset"):
            if data.get(key):
                self.refs.append(data[key] or "")


def free_port() -> int:
    with contextlib.closing(socket.socket()) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def validate_source() -> list[str]:
    errors: list[str] = []
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = Refs()
    parser.feed(html)

    if parser.h1_count != 1:
        errors.append(f"Source expected one H1, found {parser.h1_count}")
    if parser.images_without_alt:
        errors.append(f"Images missing alt attributes: {parser.images_without_alt}")

    for ref in parser.refs:
        if ref.startswith(("http://", "https://", "tel:", "sms:", "#")):
            if ref.startswith("#") and ref[1:] not in parser.ids:
                errors.append(f"Missing anchor target: {ref}")
            continue
        clean = urlsplit(ref.split()[0]).path
        if clean and not (ROOT / clean).is_file():
            errors.append(f"Missing local reference: {ref}")

    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    for ref in re.findall(r'url\(["\']?([^"\')]+)', css):
        if ref.startswith(("data:", "http://", "https://")):
            continue
        if not (ROOT / ref).is_file():
            errors.append(f"Missing CSS asset: {ref}")

    js = (ROOT / "app.js").read_text(encoding="utf-8")
    if "window.ZenithBooking" not in js:
        errors.append("Booking helper is not exposed for deterministic QA")
    if "window.ZenithMorph" not in js:
        errors.append("Morph helper is not exposed for deterministic QA")
    if "window.ZenithAnalytics" not in js:
        errors.append("Analytics helper is not exposed for deterministic QA")
    for event_name in ("service_select", "sms_open", "call_click"):
        if f'trackEvent("{event_name}"' not in js:
            errors.append(f"Analytics event is missing: {event_name}")
    if "generate_lead" in js:
        errors.append("Click instrumentation must not claim a confirmed lead")
    if f"googletagmanager.com/gtag/js?id={MEASUREMENT_ID}" not in html:
        errors.append("GA4 loader is missing or incorrect")
    if not (ROOT / "privacy.html").is_file() or 'href="privacy.html"' not in html:
        errors.append("Privacy policy is missing or unlinked")

    for blueprint_name in ("hero-blueprint.svg", "hero-blueprint-mobile.svg"):
        blueprint = (ROOT / "assets" / blueprint_name).read_text(encoding="utf-8")
        if "<image" in blueprint:
            errors.append(f"{blueprint_name} embeds a raster image instead of pure vector linework")
        if "<text" in blueprint:
            errors.append(f"{blueprint_name} contains visible text")
        if blueprint.count("<path") < 20:
            errors.append(f"{blueprint_name} does not contain enough drafted linework")
    return errors


def run() -> int:
    PREVIEWS.mkdir(exist_ok=True)
    source_errors = validate_source()
    errors = list(source_errors)
    results: dict[str, object] = {
        "source": "pass" if not source_errors else source_errors,
        "viewports": {},
        "reduced_motion": {},
    }

    target_url = os.environ.get("ZENITH_QA_URL", "").rstrip("/")
    server: http.server.ThreadingHTTPServer | None = None
    if target_url:
        base_url = target_url
    else:
        port = free_port()
        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(ROOT), **kwargs)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base_url = f"http://127.0.0.1:{port}"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            axe = Axe()

            for name, (width, height) in VIEWPORTS.items():
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    reduced_motion="no-preference",
                )
                context.route(
                    "https://www.googletagmanager.com/**",
                    lambda route: route.fulfill(status=204, body=""),
                )
                context.add_init_script(
                    "window.__qaEvents = []; window.gtag = (...args) => window.__qaEvents.push(args);"
                )
                page = context.new_page()
                browser_errors: list[str] = []
                page.on(
                    "console",
                    lambda msg, bucket=browser_errors: bucket.append(f"console:{msg.type}:{msg.text}")
                    if msg.type == "error"
                    else None,
                )
                page.on("pageerror", lambda exc, bucket=browser_errors: bucket.append(f"pageerror:{exc}"))
                response = page.goto(
                    f"{base_url}/?utm_source=qa&utm_medium=test&utm_campaign=launch&ref=qa-partner",
                    wait_until="networkidle",
                )
                page.evaluate("document.fonts.ready")
                page.add_style_tag(content="html{scroll-behavior:auto!important}")
                page.wait_for_timeout(80)

                status = response.status if response else 0
                h1_count = page.locator("h1").count()
                card_count = page.locator(".service-card").count()
                symbol_count = page.locator(".service-symbol").count()
                morph_image_count = page.locator(".morph-layer img").count()
                hero_state_label_count = page.locator(".morph-status, .morph-instruction").count()
                overflow = page.evaluate(
                    "Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - innerWidth"
                )
                images = page.locator("img").evaluate_all(
                    "imgs => imgs.map(i => ({src:i.currentSrc || i.getAttribute('src'), complete:i.complete, width:i.naturalWidth, alt:i.getAttribute('alt')}))"
                )
                broken = [item for item in images if not item["complete"] or item["width"] <= 0]
                unnamed = page.locator("a, button, input, select, textarea").evaluate_all(
                    "els => els.filter(el => { const tag=el.tagName.toLowerCase(); if(['input','select','textarea'].includes(tag)) return !el.labels?.length && !el.getAttribute('aria-label'); return !(el.innerText || el.getAttribute('aria-label') || '').trim(); }).map(el => el.outerHTML)"
                )
                tel_count = page.locator(f'a[href="tel:{PHONE}"]').count()
                sms_count = page.locator(f'a[href="sms:{PHONE}"]').count()
                offer_text = page.locator("h1").inner_text()
                canonical_href = page.locator('link[rel="canonical"]').get_attribute("href")
                social_image = page.locator('meta[property="og:image"]').get_attribute("content")
                booking_href = page.evaluate(
                    "window.ZenithBooking.buildHref({service:'NMEA 2000 networks',location:'Tavernier',vessel:'Test vessel / test equipment',date:'',details:'Intermittent data'})"
                )
                attribution = page.evaluate("window.ZenithBooking.attribution()")

                morph_states = page.evaluate(
                    """() => {
                      const stage = document.querySelector('[data-morph-stage]');
                      const snap = () => ({
                        reveal: stage.style.getPropertyValue('--reveal'),
                        turn: stage.style.getPropertyValue('--turn'),
                        state: stage.dataset.morphState,
                        progress: window.ZenithMorph.progress()
                      });
                      window.ZenithMorph.render(0); const blueprint = snap();
                      window.ZenithMorph.render(0.5); const middle = snap();
                      window.ZenithMorph.render(1); const vessel = snap();
                      window.ZenithMorph.render(0); const reversed = snap();
                      return {blueprint, middle, vessel, reversed};
                    }"""
                )

                if width > 820:
                    travel = page.evaluate(
                        "document.querySelector('[data-morph-hero]').offsetHeight - document.querySelector('[data-morph-sticky]').offsetHeight"
                    )
                    scroll_positions = (0, travel * 0.5, travel, 0)
                else:
                    stage_top = page.evaluate(
                        "document.querySelector('[data-morph-stage]').getBoundingClientRect().top + scrollY"
                    )
                    scroll_positions = (
                        max(0, stage_top - height * 0.78),
                        max(0, stage_top - height * 0.48),
                        max(0, stage_top - height * 0.18),
                        0,
                    )

                scroll_progress: list[float] = []
                for position in scroll_positions:
                    page.evaluate("y => window.scrollTo(0, y)", position)
                    page.wait_for_timeout(80)
                    page.evaluate("window.ZenithMorph.update()")
                    scroll_progress.append(float(page.evaluate("window.ZenithMorph.progress()")))

                first_service_button = page.locator('[data-service="NMEA 2000 networks"]')
                first_service_button.click()
                page.wait_for_timeout(30)
                selected_service = page.locator("#service").input_value()
                page.locator('a[href^="tel:"]').first.evaluate(
                    """el => {
                      el.addEventListener('click', event => event.preventDefault(), {once: true});
                      el.click();
                    }"""
                )
                page.locator('a[href^="sms:"]').first.evaluate(
                    """el => {
                      el.addEventListener('click', event => event.preventDefault(), {once: true});
                      el.click();
                    }"""
                )
                analytics_events = page.evaluate(
                    "window.__qaEvents.filter(event => event[0] === 'event')"
                )
                analytics_by_name = {
                    event[1]: event[2]
                    for event in analytics_events
                    if len(event) >= 3
                }
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(80)

                axe_results = axe.run(page)
                axe_violations = [
                    {
                        "id": violation["id"],
                        "impact": violation["impact"],
                        "nodes": len(violation["nodes"]),
                        "targets": [node["target"] for node in violation["nodes"]],
                    }
                    for violation in axe_results.response["violations"]
                ]

                if status != 200:
                    browser_errors.append(f"HTTP status {status}")
                if h1_count != 1:
                    browser_errors.append(f"Expected one H1, found {h1_count}")
                if card_count != 3 or symbol_count != 3:
                    browser_errors.append(f"Expected 3 service cards/symbols, found {card_count}/{symbol_count}")
                if morph_image_count != 2:
                    browser_errors.append(f"Expected aligned blueprint/photo layers, found {morph_image_count}")
                if hero_state_label_count:
                    browser_errors.append(f"Hero state labels remain visible in source: {hero_state_label_count}")
                if overflow > 1:
                    browser_errors.append(f"Horizontal overflow {overflow}px")
                if broken:
                    browser_errors.append(f"Broken images: {broken}")
                if unnamed:
                    browser_errors.append(f"Unnamed interactive elements: {unnamed}")
                if tel_count < 3:
                    browser_errors.append(f"Expected repeated telephone actions, found {tel_count}")
                if sms_count < 1:
                    browser_errors.append(f"Expected direct SMS fallback, found {sms_count}")
                if not all(term in offer_text for term in ("NMEA", "Starlink", "VHF", "FCC")):
                    browser_errors.append(f"First-view offer is incomplete: {offer_text!r}")
                if canonical_href != "https://zenithmarineelectronics.com/":
                    browser_errors.append(f"Canonical URL is incorrect: {canonical_href!r}")
                if social_image != "https://zenithmarineelectronics.com/assets/images/social.webp":
                    browser_errors.append(f"Social image URL is incorrect: {social_image!r}")
                if selected_service != "NMEA 2000 networks":
                    browser_errors.append(f"Service preselection failed: {selected_service!r}")
                if not booking_href.startswith(f"sms:{PHONE}?body=") or "NMEA%202000%20networks" not in booking_href:
                    browser_errors.append(f"Booking SMS builder failed: {booking_href!r}")
                booking_text = unquote(booking_href.split("?body=", 1)[1]) if "?body=" in booking_href else ""
                if "Lead source: qa / test / launch / qa-partner" not in booking_text:
                    browser_errors.append(f"Booking attribution failed: {booking_text!r}")
                if attribution != {"source": "qa", "medium": "test", "campaign": "launch", "partner": "qa-partner"}:
                    browser_errors.append(f"URL attribution parse failed: {attribution!r}")
                if analytics_by_name.get("service_select") != {"service_name": "NMEA 2000 networks"}:
                    browser_errors.append(f"service_select analytics failed: {analytics_events!r}")
                if analytics_by_name.get("call_click", {}).get("lead_source") != "qa":
                    browser_errors.append(f"call_click analytics failed: {analytics_events!r}")
                if analytics_by_name.get("sms_open") != {"service_name": "direct_text", "lead_source": "qa"}:
                    browser_errors.append(f"sms_open analytics failed: {analytics_events!r}")
                if morph_states["blueprint"]["reveal"] != "0.00%":
                    browser_errors.append(f"Blueprint state failed: {morph_states}")
                if morph_states["middle"]["reveal"] != "50.00%":
                    browser_errors.append(f"Middle morph state failed: {morph_states}")
                if morph_states["vessel"]["reveal"] != "100.00%":
                    browser_errors.append(f"Vessel state failed: {morph_states}")
                if morph_states["reversed"]["reveal"] != "0.00%":
                    browser_errors.append(f"Reverse morph state failed: {morph_states}")
                if not (
                    scroll_progress[0] < 0.5
                    and scroll_progress[1] > scroll_progress[0] + 0.1
                    and scroll_progress[2] >= 0.85
                    and abs(scroll_progress[3] - scroll_progress[0]) <= 0.05
                ):
                    browser_errors.append(f"Scroll-linked forward/reverse progression failed: {scroll_progress}")
                if axe_violations:
                    browser_errors.append(f"Axe violations: {axe_violations}")

                skip = page.locator(".skip-link")
                skip.focus()
                skip_visible = skip.evaluate(
                    "el => { const r = el.getBoundingClientRect(); return r.top >= 0 && r.left >= 0 && r.width > 0 && r.height > 0; }"
                )
                if not skip_visible:
                    browser_errors.append("Skip link is not visible when focused")

                page.locator("#service").select_option("")
                page.evaluate("document.activeElement?.blur(); window.scrollTo(0, 0)")
                page.wait_for_timeout(80)

                results["viewports"][name] = {
                    "status": status,
                    "h1": h1_count,
                    "service_cards": card_count,
                    "service_symbols": symbol_count,
                    "morph_images": morph_image_count,
                    "hero_state_labels": hero_state_label_count,
                    "morph_states": morph_states,
                    "scroll_progress": scroll_progress,
                    "overflow_px": overflow,
                    "images": len(images),
                    "sms_actions": sms_count,
                    "telephone_actions": tel_count,
                    "service_preselection": selected_service,
                    "booking_sms": booking_href,
                    "analytics_events": analytics_events,
                    "skip_link_focus": skip_visible,
                    "axe_violations": axe_violations,
                    "errors": browser_errors,
                }
                errors.extend(f"{name}: {error}" for error in browser_errors)

                if name == "desktop-1440":
                    page.evaluate("window.ZenithMorph.render(0)")
                    page.screenshot(path=str(PREVIEWS / "desktop-blueprint.png"), full_page=False)
                    page.evaluate("window.ZenithMorph.render(0.5)")
                    page.screenshot(path=str(PREVIEWS / "desktop-transform.png"), full_page=False)
                    page.evaluate("window.ZenithMorph.render(1)")
                    page.screenshot(path=str(PREVIEWS / "desktop-vessel.png"), full_page=False)
                    page.add_style_tag(content="html.qa-static-capture .hero{min-height:auto!important} html.qa-static-capture .hero-sticky{position:relative!important;top:auto!important} html.qa-static-capture .morph-vessel{transform:none!important} html.qa-static-capture .morph-real{clip-path:inset(0)!important} html.qa-static-capture .morph-blueprint,html.qa-static-capture .morph-scan{display:none!important}")
                    page.evaluate("document.documentElement.classList.add('qa-static-capture'); window.ZenithMorph.render(1)")
                    page.screenshot(path=str(PREVIEWS / "desktop-full.png"), full_page=True)
                elif name == "mobile-390":
                    page.screenshot(path=str(PREVIEWS / "mobile-hero.png"), full_page=False)
                    page.locator("[data-morph-stage]").scroll_into_view_if_needed()
                    page.wait_for_timeout(120)
                    page.evaluate("window.ZenithMorph.render(0)")
                    page.wait_for_timeout(20)
                    page.screenshot(path=str(PREVIEWS / "mobile-blueprint.png"), full_page=False)
                    page.evaluate("window.ZenithMorph.render(1)")
                    page.screenshot(path=str(PREVIEWS / "mobile-vessel.png"), full_page=False)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(80)
                    page.evaluate("window.ZenithMorph.render(0)")
                    page.screenshot(path=str(PREVIEWS / "mobile-full.png"), full_page=True)
                context.close()

            for name, (width, height) in {
                "mobile-390": VIEWPORTS["mobile-390"],
                "desktop-1440": VIEWPORTS["desktop-1440"],
            }.items():
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    reduced_motion="reduce",
                )
                context.route(
                    "https://www.googletagmanager.com/**",
                    lambda route: route.fulfill(status=204, body=""),
                )
                page = context.new_page()
                page.goto(f"{base_url}/", wait_until="networkidle")
                page.wait_for_timeout(80)
                reduced_state = page.evaluate(
                    """() => {
                      const stage = document.querySelector('[data-morph-stage]');
                      const real = document.querySelector('.morph-real');
                      const vessel = document.querySelector('.morph-vessel');
                      const blueprint = document.querySelector('.morph-blueprint');
                      const scan = document.querySelector('.morph-scan');
                      const hero = document.querySelector('[data-morph-hero]');
                      const sticky = document.querySelector('[data-morph-sticky]');
                      return {
                        matches: matchMedia('(prefers-reduced-motion: reduce)').matches,
                        reveal: stage.style.getPropertyValue('--reveal'),
                        real_clip: getComputedStyle(real).clipPath,
                        vessel_transform: getComputedStyle(vessel).transform,
                        blueprint_display: getComputedStyle(blueprint).display,
                        scan_display: getComputedStyle(scan).display,
                        hero_height: hero.getBoundingClientRect().height,
                        sticky_height: sticky.getBoundingClientRect().height
                      };
                    }"""
                )
                reduced_errors: list[str] = []
                if not reduced_state["matches"]:
                    reduced_errors.append("Reduced-motion media query did not match")
                if reduced_state["reveal"] != "100.00%":
                    reduced_errors.append(f"Static vessel was not selected: {reduced_state}")
                if reduced_state["real_clip"] not in ("inset(0px)", "inset(0px 0px 0px 0px)"):
                    reduced_errors.append(f"Real vessel remained clipped: {reduced_state}")
                if reduced_state["vessel_transform"] != "none":
                    reduced_errors.append(f"Transform remained active: {reduced_state}")
                if reduced_state["blueprint_display"] != "none" or reduced_state["scan_display"] != "none":
                    reduced_errors.append(f"Motion decoration remained visible: {reduced_state}")
                if abs(reduced_state["hero_height"] - reduced_state["sticky_height"]) > 2:
                    reduced_errors.append(f"Reduced motion retained excess scroll range: {reduced_state}")
                results["reduced_motion"][name] = {"state": reduced_state, "errors": reduced_errors}
                errors.extend(f"reduced-{name}: {error}" for error in reduced_errors)
                if name == "desktop-1440":
                    page.screenshot(path=str(PREVIEWS / "desktop-reduced-motion.png"), full_page=False)
                context.close()

            browser.close()
    finally:
        if server:
            server.shutdown()
            server.server_close()

    results["pass"] = not errors
    results["errors"] = errors
    (PREVIEWS / "qa-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    lines = [
        "# Zenith Service First — QA Report",
        "",
        f"**Result:** {'PASS' if not errors else 'FAIL'}",
        "",
        "## Coverage",
        "",
        "- Local references, in-page anchors, and one H1",
        "- Exactly three service cards and three custom symbols",
        "- Complete first-view offer: NMEA, Starlink, VHF, and FCC",
        "- Pure-vector, text-free blueprint/photo layers and deterministic 0/50/100/reverse states",
        "- Real scroll-linked forward and reverse progression",
        "- Working service preselection, deterministic booking-SMS builder, and GA4 event hooks",
        "- Image loading and interactive accessible names",
        "- Telephone/SMS targets and skip-link focus",
        "- Axe accessibility audit and reduced-motion static fallback",
        "- Console/page errors and horizontal overflow at 320, 390, 768, and 1440 px",
        "- Desktop/mobile blueprint, transition, vessel, and full-page captures",
        "",
        "## Viewports",
        "",
    ]
    for name, data in results["viewports"].items():
        viewport_status = "PASS" if not data["errors"] else "FAIL"
        lines.append(
            f"- **{name}:** {viewport_status} · overflow {data['overflow_px']} px · "
            f"{data['service_cards']} service cards · {data['images']} images · scroll {data['scroll_progress']}"
        )
    if errors:
        lines.extend(["", "## Errors", ""] + [f"- {error}" for error in errors])
    else:
        lines.extend(
            [
                "",
                "No broken assets, invalid local links, horizontal overflow, browser errors, failed interactions, failed morph states, or Axe violations were observed.",
            ]
        )
    (PREVIEWS / "QA-REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(run())
