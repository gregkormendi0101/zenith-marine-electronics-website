#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE = os.environ.get("SITE_URL", "http://127.0.0.1:4173/")
PAGES = ["", "nmea-networks.html", "marine-electronics.html", "marine-radio-fcc.html"]
WIDTHS = [320, 375, 390, 430, 768, 1024, 1440]
errors: list[str] = []
checks = 0


def fail(message: str) -> None:
    errors.append(message)


with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()

    for path in PAGES:
        for width in WIDTHS:
            checks += 1
            page.set_viewport_size({"width": width, "height": 900})
            console_errors: list[str] = []
            failed_requests: list[str] = []
            page.on("console", lambda msg, bucket=console_errors: bucket.append(msg.text) if msg.type == "error" else None)
            page.on("requestfailed", lambda req, bucket=failed_requests: bucket.append(req.url))
            response = page.goto(urljoin(BASE, path), wait_until="networkidle")
            label = f"{path or 'index.html'} @ {width}px"
            if not response or not response.ok:
                fail(f"{label}: navigation failed")
                continue

            page.locator("body").wait_for(state="visible")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(80)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(80)

            state = page.evaluate("""() => {
              const root = document.documentElement;
              const offenders = [...document.querySelectorAll('body *')].filter((el) => {
                const style = getComputedStyle(el);
                if (style.position === 'fixed' || style.position === 'absolute') return false;
                const r = el.getBoundingClientRect();
                return r.right > innerWidth + 1 || r.left < -1;
              }).slice(0, 8).map((el) => `${el.tagName}.${el.className}`);
              const badImages = [...document.images].filter((img) => !img.complete || img.naturalWidth === 0).map((img) => img.getAttribute('src'));
              const h1 = document.querySelector('h1');
              const phoneCount = (document.body.innerText.match(/305-306-6391/g) || []).length;
              return {
                overflow: root.scrollWidth - root.clientWidth,
                offenders,
                badImages,
                h1Visible: !!h1 && h1.getBoundingClientRect().height > 0,
                navCount: document.querySelectorAll('.primary-nav a').length,
                phoneCount,
                year: document.querySelector('[data-year]')?.textContent || '',
                leadLinks: document.querySelectorAll('.track[data-event]').length
              };
            }""")

            if state["overflow"] > 1:
                fail(f"{label}: horizontal overflow {state['overflow']}px; {state['offenders']}")
            if state["badImages"]:
                fail(f"{label}: failed images {state['badImages']}")
            if not state["h1Visible"]:
                fail(f"{label}: h1 not visible")
            if state["navCount"] != 3:
                fail(f"{label}: expected 3 primary nav links")
            if state["phoneCount"] != 1:
                fail(f"{label}: expected one visible phone number, got {state['phoneCount']}")
            if not state["year"].isdigit():
                fail(f"{label}: dynamic year missing")
            if state["leadLinks"] < 3:
                fail(f"{label}: lead tracking hooks missing")
            if console_errors:
                fail(f"{label}: console errors: {console_errors}")
            if failed_requests:
                fail(f"{label}: failed requests: {failed_requests}")

    for width in (390, 1440):
        page.set_viewport_size({"width": width, "height": 1000})
        page.goto(BASE, wait_until="networkidle")
        for target, href in (
            ("nmea", "nmea-networks.html"),
            ("electronics", "marine-electronics.html"),
            ("radio", "marine-radio-fcc.html"),
        ):
            tab = page.locator(f'[data-system-target="{target}"]')
            tab.click()
            page.wait_for_timeout(60)
            selected = tab.get_attribute("aria-selected")
            panel = page.locator(f'[data-system-panel="{target}"]')
            if selected != "true" or panel.is_hidden():
                fail(f"home tabs @ {width}px: {target} did not activate")
            panel_link = panel.locator(f'a[href="{href}"]')
            if panel_link.count() != 1:
                fail(f"home tabs @ {width}px: {target} missing dedicated page link")
        page.locator('[data-system-target="nmea"]').focus()
        page.keyboard.press("ArrowRight")
        if page.locator('[data-system-target="electronics"]').get_attribute("aria-selected") != "true":
            fail(f"home tabs @ {width}px: keyboard navigation failed")

    page.goto(urljoin(BASE, "?utm_source=qa&utm_campaign=futuristic"), wait_until="networkidle")
    internal = page.locator('a[href*="nmea-networks.html"]').first.get_attribute("href") or ""
    if "utm_source=qa" not in internal or "utm_campaign=futuristic" not in internal:
        fail("UTM retention failed")

    page.evaluate("""() => {
      const el = document.querySelector('.track[data-event]');
      el.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
    }""")
    data_layer = page.evaluate("window.dataLayer")
    if not data_layer or data_layer[-1].get("event") != "lead_action":
        fail("lead-action tracking push failed")

    reduced = browser.new_context(reduced_motion="reduce", viewport={"width": 390, "height": 844})
    reduced_page = reduced.new_page()
    reduced_page.goto(BASE, wait_until="networkidle")
    reduced_state = reduced_page.evaluate("""() => ({
      hiddenReveal: [...document.querySelectorAll('[data-reveal]')].some((el) => getComputedStyle(el).opacity === '0'),
      smoothScroll: getComputedStyle(document.documentElement).scrollBehavior,
      orbitDuration: getComputedStyle(document.querySelector('.orbit-rings i')).animationDuration
    })""")
    if reduced_state["hiddenReveal"]:
        fail("reduced motion: reveal content remained hidden")
    if reduced_state["smoothScroll"] == "smooth":
        fail("reduced motion: smooth scrolling remained active")
    reduced.close()
    browser.close()

if errors:
    print(f"RESPONSIVE QA FAILED ({len(errors)} issue(s), {checks} page/width checks)")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"RESPONSIVE QA PASSED ({checks} page/width checks)")
print("- widths: 320, 375, 390, 430, 768, 1024, 1440")
print("- images, overflow, navigation, tabs, keyboard, UTM, tracking and reduced motion: pass")
