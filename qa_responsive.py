import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
URL = os.environ.get("ZENITH_QA_URL", "http://127.0.0.1:4173/").rstrip("/") + "/"
HOST_RESOLVER_RULES = os.environ.get("ZENITH_QA_HOST_RESOLVER_RULES")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
VIEWPORTS = [
    (320, 740),
    (375, 812),
    (390, 844),
    (430, 932),
    (768, 1024),
    (1024, 768),
    (1440, 1000),
]


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


with sync_playwright() as p:
    browser_args = ["--disable-background-networking", "--disable-component-update", "--disable-sync", "--no-first-run"]
    if HOST_RESOLVER_RULES:
        browser_args.append(f"--host-resolver-rules={HOST_RESOLVER_RULES}")
    browser = p.chromium.launch(headless=True, executable_path=CHROME, args=browser_args)

    for width, height in VIEWPORTS:
        page_errors: list[str] = []
        console_errors: list[str] = []
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1, is_mobile=width <= 430)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(650)

        layout = page.evaluate("""
        () => {
          const rect = (selector) => {
            const node = document.querySelector(selector);
            if (!node) return null;
            const r = node.getBoundingClientRect();
            return {left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height};
          };
          return {
            viewport: [innerWidth, innerHeight],
            scrollWidth: document.documentElement.scrollWidth,
            h1: rect('.hero h1'),
            header: rect('.header-inner'),
            headerContact: rect('.header-contact'),
            heroButton: rect('.hero-actions .button'),
            jumpLinks: [...document.querySelectorAll('.service-jump a')].map((node) => {
              const r = node.getBoundingClientRect();
              return {left: r.left, right: r.right, height: r.height};
            }),
            diagrams: document.querySelectorAll('.system-diagram').length,
            mobileLead: rect('.mobile-lead')
          };
        }
        """)
        check(layout["scrollWidth"] == width, f"{width}px: horizontal overflow ({layout['scrollWidth']}px)")
        check(layout["h1"]["left"] >= 0 and layout["h1"]["right"] <= width, f"{width}px: hero heading escapes viewport")
        check(layout["headerContact"]["right"] <= width, f"{width}px: header contact link escapes viewport")
        check(layout["heroButton"]["height"] >= 48, f"{width}px: hero button below 48px touch size")
        check(all(item["left"] >= -1 and item["right"] <= width + 1 for item in layout["jumpLinks"]), f"{width}px: service jump escapes viewport")
        check(layout["diagrams"] == 3, f"{width}px: all three technical diagrams did not render")

        for selector in ("#nmea", "#installation", "#radio", ".nmea-logo-card"):
            page.locator(selector).scroll_into_view_if_needed()
            page.wait_for_timeout(160)

        image_failures = page.evaluate("""
        () => [...document.images]
          .filter((image) => !image.complete || image.naturalWidth === 0)
          .map((image) => image.getAttribute('src'))
        """)
        check(not image_failures, f"{width}px: images failed to load: {image_failures}")

        phones = page.eval_on_selector_all("a[href^='tel:'], a[href^='sms:']", "nodes => nodes.map(node => node.getAttribute('href'))")
        check(phones and all("3053066391" in href and "*" not in href for href in phones), f"{width}px: malformed phone link")

        for anchor in ("services", "nmea", "installation", "radio", "credentials", "contact"):
            page.goto(URL + f"?anchor={anchor}-{width}#{anchor}", wait_until="networkidle")
            page.wait_for_timeout(180)
            anchor_top = page.locator(f"#{anchor}").evaluate("node => node.getBoundingClientRect().top")
            check(anchor_top >= 66, f"{width}px: #{anchor} hidden by fixed header ({anchor_top})")

        if width <= 720:
            page.goto(URL, wait_until="networkidle")
            page.locator("#services").scroll_into_view_if_needed()
            page.wait_for_timeout(260)
            lead_state = page.evaluate("""
            () => {
              const r = document.querySelector('.mobile-lead').getBoundingClientRect();
              return {bottom: r.bottom, height: r.height, shown: document.body.classList.contains('show-mobile-lead')};
            }
            """)
            check(lead_state["shown"], f"{width}px: mobile lead did not appear after hero")
            check(lead_state["height"] >= 48 and lead_state["bottom"] <= height + 1, f"{width}px: mobile lead is not viewport-safe")
            page.locator("#nmea .service-visual").scroll_into_view_if_needed()
            page.wait_for_timeout(560)
            check(page.evaluate("document.body.classList.contains('visual-in-view')"), f"{width}px: diagram visibility state did not activate")
            hidden_lead_top = page.locator(".mobile-lead").evaluate("node => node.getBoundingClientRect().top")
            check(hidden_lead_top >= height, f"{width}px: mobile lead still obstructs a technical diagram")
            page.locator("#contact").scroll_into_view_if_needed()
            page.wait_for_timeout(220)
            check(page.evaluate("document.body.classList.contains('at-contact')"), f"{width}px: mobile lead did not hide at contact section")

        check(not page_errors, f"{width}px: JavaScript errors: {page_errors}")
        check(not console_errors, f"{width}px: console errors: {console_errors}")
        print(f"PASS {width}x{height}: layout, assets, anchors, diagrams and lead controls")
        page.close()

    page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
    page.goto(URL + "?utm_source=qa&utm_medium=browser", wait_until="networkidle")
    stored = page.evaluate("sessionStorage.getItem('zenith_attribution')")
    check(stored is not None and 'qa' in stored and 'browser' in stored, "UTM attribution was not retained")
    page.evaluate("document.querySelector('.contact-primary').addEventListener('click', event => event.preventDefault(), {once: true})")
    page.locator(".contact-primary").click()
    action = page.evaluate("window.dataLayer.at(-1)?.action")
    check(action == "contact_text", f"Lead tracking event missing or wrong: {action}")

    page.goto(URL, wait_until="networkidle")
    page.locator("#nmea").scroll_into_view_if_needed()
    page.wait_for_timeout(250)
    cx_before = float(page.locator("#nmea [data-route-dot]").get_attribute("cx") or "0")
    page.evaluate("window.scrollBy(0, 280)")
    page.wait_for_timeout(220)
    cx_down = float(page.locator("#nmea [data-route-dot]").get_attribute("cx") or "0")
    page.evaluate("window.scrollBy(0, -280)")
    page.wait_for_timeout(220)
    cx_up = float(page.locator("#nmea [data-route-dot]").get_attribute("cx") or "0")
    check(cx_down > cx_before + 1, f"scrolling down did not advance NMEA route dot ({cx_before} -> {cx_down})")
    check(cx_up < cx_down - 1, f"scrolling up did not reverse NMEA route dot ({cx_down} -> {cx_up})")
    print("PASS motion: route dot follows scroll down and reverses on scroll up")
    print("PASS analytics: UTM retention and lead_action tracking")
    page.close()

    browser.close()

print("RESPONSIVE QA PASSED")
