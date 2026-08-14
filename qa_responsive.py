import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
URL = os.environ.get("ZENITH_QA_URL", "http://100.122.63.73:4173/").rstrip("/") + "/"
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
    browser = p.chromium.launch(
        headless=True,
        executable_path=CHROME,
        args=browser_args,
    )

    for width, height in VIEWPORTS:
        page_errors: list[str] = []
        console_errors: list[str] = []
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1, is_mobile=width <= 430)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(500)

        layout = page.evaluate("""
        () => {
          const rect = (selector) => {
            const r = document.querySelector(selector).getBoundingClientRect();
            return {left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height};
          };
          return {
            viewport: [innerWidth, innerHeight],
            scrollWidth: document.documentElement.scrollWidth,
            h1: rect('.hero h1'),
            header: rect('.header-inner'),
            headerCta: rect('.header-cta'),
            heroButtons: [...document.querySelectorAll('.hero-actions .button')].map((node) => node.getBoundingClientRect().height),
            mobileCta: rect('.mobile-cta')
          };
        }
        """)
        check(layout["scrollWidth"] == width, f"{width}px: horizontal overflow ({layout['scrollWidth']}px)")
        check(layout["h1"]["left"] >= 0 and layout["h1"]["right"] <= width, f"{width}px: hero heading escapes viewport")
        check(layout["headerCta"]["right"] <= width, f"{width}px: header CTA escapes viewport")
        check(all(value >= 48 for value in layout["heroButtons"]), f"{width}px: hero button below 48px touch size")
        if width <= 700:
            check(layout["mobileCta"]["left"] >= 0 and layout["mobileCta"]["right"] <= width, f"{width}px: mobile CTA escapes viewport")
            check(layout["mobileCta"]["height"] >= 48, f"{width}px: mobile CTA below 48px")
            for scroll_fraction in (0, 0.5, 1):
                page.evaluate(
                    "fraction => window.scrollTo(0, (document.documentElement.scrollHeight - innerHeight) * fraction)",
                    scroll_fraction,
                )
                page.wait_for_timeout(100)
                mobile_cta_bottom = page.locator(".mobile-cta").evaluate("node => node.getBoundingClientRect().bottom")
                viewport_bottom = page.evaluate("innerHeight")
                check(
                    abs(mobile_cta_bottom - viewport_bottom) <= 1,
                    f"{width}px: mobile CTA detached from viewport bottom at {scroll_fraction:.0%} scroll",
                )

        for selector in (".precision-media", ".nmea-card", ".contact-media"):
            page.locator(selector).scroll_into_view_if_needed()
            page.wait_for_timeout(250)

        image_failures = page.evaluate("""
        () => [...document.images]
          .filter((image) => !image.complete || image.naturalWidth === 0)
          .map((image) => image.getAttribute('src'))
        """)
        check(not image_failures, f"{width}px: images failed to load: {image_failures}")

        phones = page.eval_on_selector_all("a[href^='tel:'], a[href^='sms:']", "nodes => nodes.map(node => node.getAttribute('href'))")
        check(phones and all("3053066391" in href and "*" not in href for href in phones), f"{width}px: malformed phone link")

        page.goto(URL + f"?anchor={width}#services", wait_until="networkidle")
        page.wait_for_timeout(250)
        services_top = page.locator("#services").evaluate("node => node.getBoundingClientRect().top")
        check(services_top >= 70, f"{width}px: services anchor hidden by fixed header ({services_top})")

        check(not page_errors, f"{width}px: JavaScript errors: {page_errors}")
        check(not console_errors, f"{width}px: console errors: {console_errors}")
        print(f"PASS {width}x{height}: no overflow, controls fit, assets loaded, anchor offset {services_top:.0f}px")
        page.close()

    page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
    page.goto(URL + "?utm_source=qa&utm_medium=browser", wait_until="networkidle")
    stored = page.evaluate("sessionStorage.getItem('zenith_attribution')")
    check(stored is not None and 'qa' in stored and 'browser' in stored, "UTM attribution was not retained")
    page.evaluate("document.querySelector('.hero-actions .track').addEventListener('click', event => event.preventDefault(), {once: true})")
    page.locator(".hero-actions .track").first.click()
    action = page.evaluate("window.dataLayer.at(-1)?.action")
    check(action == "hero_text", f"Lead tracking event missing or wrong: {action}")
    print("PASS analytics: UTM retention and lead_action tracking")
    page.close()

    browser.close()

print("RESPONSIVE QA PASSED")
