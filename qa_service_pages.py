#!/usr/bin/env python3
"""Responsive, accessibility, attribution, and interaction QA for service pages."""

from __future__ import annotations

import contextlib
import http.server
import json
import os
import socket
import threading
from pathlib import Path

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / ".qa-artifacts" / "service-pages"
PAGES = {
    "nmea-2000-troubleshooting-upper-florida-keys.html": "NMEA 2000 networks",
    "marine-starlink-installation-upper-florida-keys.html": "Starlink systems",
    "vhf-dsc-ais-service-upper-florida-keys.html": "VHF radio service",
}
VIEWPORTS = {"mobile-390": (390, 844), "desktop-1440": (1440, 1000)}


def free_port() -> int:
    with contextlib.closing(socket.socket()) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    configured_base = os.environ.get("ZENITH_QA_URL", "").strip().rstrip("/")
    server: http.server.ThreadingHTTPServer | None = None
    if configured_base:
        base = configured_base
    else:
        port = free_port()
        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(ROOT), **kwargs)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{port}"
    results: dict[str, object] = {}
    errors: list[str] = []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            axe = Axe()
            for filename, expected_service in PAGES.items():
                for viewport_name, (width, height) in VIEWPORTS.items():
                    key = f"{filename}:{viewport_name}"
                    context = browser.new_context(viewport={"width": width, "height": height})
                    context.route("https://www.googletagmanager.com/**", lambda route: route.fulfill(status=204, body=""))
                    context.add_init_script("window.__qaEvents=[]; window.gtag=(...args)=>window.__qaEvents.push(args);")
                    page = context.new_page()
                    console_errors: list[str] = []
                    page.on("console", lambda msg, bucket=console_errors: bucket.append(msg.text) if msg.type == "error" else None)
                    page.on("pageerror", lambda exc, bucket=console_errors: bucket.append(str(exc)))
                    response = page.goto(
                        f"{base}/{filename}?utm_source=service-page-qa&utm_medium=test&utm_campaign=demand-test&ref=qa",
                        wait_until="networkidle",
                    )
                    page.evaluate("document.fonts.ready")
                    page.wait_for_timeout(80)

                    status = response.status if response else 0
                    overflow = page.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - innerWidth")
                    h1_count = page.locator("h1").count()
                    selected = page.locator("#service").input_value()
                    attribution = page.evaluate("window.ZenithBooking.attribution()")
                    sms_href = page.evaluate(
                        "window.ZenithBooking.buildHref({service:document.querySelector('#service').value,location:'Tavernier',vessel:'QA vessel / QA equipment',date:'',details:'Demand-test QA'})"
                    )
                    images = page.locator("img").evaluate_all(
                        "imgs => imgs.map(i => ({src:i.currentSrc||i.src,complete:i.complete,width:i.naturalWidth}))"
                    )
                    broken = [image for image in images if not image["complete"] or image["width"] <= 0]
                    violations = axe.run(page).response.get("violations", [])

                    page.locator('a[href^="tel:"]').first.evaluate(
                        "el => {el.addEventListener('click', event => event.preventDefault(), {once:true}); el.click();}"
                    )
                    analytics_events = page.evaluate("window.__qaEvents.filter(e => e[0] === 'event')")
                    event_names = [event[1] for event in analytics_events if len(event) > 1]

                    checks = {
                        "status": status,
                        "h1_count": h1_count,
                        "overflow_px": overflow,
                        "selected_service": selected,
                        "attribution": attribution,
                        "sms_has_source": "service-page-qa" in sms_href,
                        "broken_images": broken,
                        "axe_violations": [item.get("id") for item in violations],
                        "console_errors": console_errors,
                        "analytics_events": event_names,
                    }
                    results[key] = checks

                    expected = [
                        (status == 200, "HTTP status is not 200"),
                        (h1_count == 1, "page does not have exactly one H1"),
                        (overflow <= 1, f"horizontal overflow is {overflow}px"),
                        (selected == expected_service, f"service preselection is {selected!r}"),
                        (attribution.get("source") == "service-page-qa", f"attribution source is {attribution}"),
                        ("service-page-qa" in sms_href, "prepared SMS lacks attribution"),
                        (not broken, f"broken images: {broken}"),
                        (not violations, f"Axe violations: {[item.get('id') for item in violations]}"),
                        (not console_errors, f"browser errors: {console_errors}"),
                        ("call_click" in event_names, f"call_click not emitted: {event_names}"),
                    ]
                    for passed, message in expected:
                        if not passed:
                            errors.append(f"{key}: {message}")

                    page.screenshot(path=str(OUT / f"{Path(filename).stem}-{viewport_name}.png"), full_page=True)
                    context.close()
            browser.close()
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()

    report = {"status": "pass" if not errors else "fail", "errors": errors, "results": results}
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if errors:
        print(f"SERVICE PAGE QA FAILED ({len(errors)} issue(s))")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"SERVICE PAGE QA PASSED: {len(PAGES)} pages × {len(VIEWPORTS)} viewports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
