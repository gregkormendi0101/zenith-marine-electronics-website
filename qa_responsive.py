import os
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE = os.environ.get("ZENITH_QA_URL", "http://127.0.0.1:4173/").rstrip("/") + "/"
HOST_RESOLVER_RULES = os.environ.get("ZENITH_QA_HOST_RESOLVER_RULES")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGES = (
    ("home", "index.html"),
    ("nmea", "nmea-networks.html"),
    ("electronics", "marine-electronics.html"),
    ("radio", "marine-radio-fcc.html"),
)
VIEWPORTS = (
    (320, 740),
    (375, 812),
    (390, 844),
    (430, 932),
    (768, 1024),
    (1024, 768),
    (1440, 1000),
)


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


with sync_playwright() as p:
    browser_args = ["--disable-background-networking", "--disable-component-update", "--disable-sync", "--no-first-run"]
    if HOST_RESOLVER_RULES:
        browser_args.append(f"--host-resolver-rules={HOST_RESOLVER_RULES}")
    browser = p.chromium.launch(headless=True, executable_path=CHROME, args=browser_args)

    for width, height in VIEWPORTS:
        for page_name, path in PAGES:
            errors: list[str] = []
            console_errors: list[str] = []
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1, is_mobile=width <= 430)
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.goto(urljoin(BASE, path), wait_until="networkidle")
            page.eval_on_selector_all("img[loading='lazy']", "nodes => nodes.forEach(node => node.loading = 'eager')")
            page.wait_for_function("Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)", timeout=10000)
            page.wait_for_timeout(180)

            metrics = page.evaluate("""
            () => {
              const rect = (selector) => {
                const node = document.querySelector(selector);
                if (!node) return null;
                const r = node.getBoundingClientRect();
                return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height};
              };
              return {
                width: innerWidth,
                scrollWidth: document.documentElement.scrollWidth,
                header: rect('.header-inner'),
                h1: rect('h1'),
                cta: rect('.header-cta'),
                nav: [...document.querySelectorAll('.primary-nav a')].map((n) => {
                  const r=n.getBoundingClientRect(); return {left:r.left,right:r.right,height:r.height,href:n.getAttribute('href')};
                }),
                images: [...document.images].map((i) => ({src:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0,w:i.naturalWidth,h:i.naturalHeight})),
                blueprintCount: document.querySelectorAll('img[src^="assets/diagrams/"]').length,
                h1Text: document.querySelector('h1')?.textContent.trim() || ''
              };
            }
            """)

            check(metrics["scrollWidth"] == width, f"{page_name} {width}px: horizontal overflow ({metrics['scrollWidth']}px)")
            check(metrics["h1"] is not None and metrics["h1"]["left"] >= -1 and metrics["h1"]["right"] <= width + 1, f"{page_name} {width}px: h1 escapes viewport")
            check(metrics["header"] is not None and metrics["header"]["left"] >= -1 and metrics["header"]["right"] <= width + 1, f"{page_name} {width}px: header escapes viewport")
            check(metrics["cta"] is not None and metrics["cta"]["right"] <= width + 1, f"{page_name} {width}px: header CTA escapes viewport")
            check(len(metrics["nav"]) == 3 and all(n["left"] >= -1 and n["right"] <= width + 1 for n in metrics["nav"]), f"{page_name} {width}px: three-page navigation is not viewport-safe")
            check(all(image["ok"] for image in metrics["images"]), f"{page_name} {width}px: image failed: {metrics['images']}")
            check(metrics["h1Text"], f"{page_name} {width}px: empty h1")

            phones = page.eval_on_selector_all("a[href^='tel:'], a[href^='sms:']", "nodes => nodes.map(n => n.getAttribute('href'))")
            check(phones and all("3053066391" in href and "*" not in href for href in phones), f"{page_name} {width}px: malformed phone link")

            if page_name == "home":
                cards = page.evaluate("""
                () => [...document.querySelectorAll('.focus-card')].map((card) => {
                  const r=card.getBoundingClientRect();
                  const a=card.querySelector('a');
                  return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,href:a.getAttribute('href'),title:card.querySelector('h3').textContent.trim()};
                })
                """)
                check(len(cards) == 3 and metrics["blueprintCount"] == 3, f"home {width}px: three blueprint specialties missing")
                check([c["href"] for c in cards] == ["nmea-networks.html", "marine-electronics.html", "marine-radio-fcc.html"], f"home {width}px: specialty destinations wrong")
                check(all(c["left"] >= -1 and c["right"] <= width + 1 for c in cards), f"home {width}px: specialty card escapes viewport")
                if width >= 1120:
                    check(all(c["top"] < height for c in cards), f"home {width}px: all three specialties are not introduced in first viewport")
                    check(max(c["top"] for c in cards) - min(c["top"] for c in cards) < 2, f"home {width}px: specialty cards are not aligned")
            else:
                check(metrics["blueprintCount"] == 1, f"{page_name} {width}px: service blueprint missing")
                check(page.locator(".scope-grid article").count() == 3, f"{page_name} {width}px: service scope must have three lanes")
                check(page.locator(".process-sheet li").count() == 4, f"{page_name} {width}px: field sequence must have four steps")
                check(page.locator(".service-switcher a").count() == 2, f"{page_name} {width}px: other-specialty links missing")
                page.locator(".hero-blueprint").scroll_into_view_if_needed()
                page.wait_for_timeout(120)
                diagram = page.locator(".hero-blueprint img").evaluate("i => ({w:i.naturalWidth,h:i.naturalHeight,attrW:i.getAttribute('width'),attrH:i.getAttribute('height'),rect:i.getBoundingClientRect().toJSON()})")
                check(diagram["w"] > 0 and diagram["h"] > 0 and diagram["attrW"] == "960" and diagram["attrH"] == "680", f"{page_name} {width}px: blueprint dimensions/load wrong {diagram}")

            check(not errors, f"{page_name} {width}px: JavaScript errors: {errors}")
            check(not console_errors, f"{page_name} {width}px: console errors: {console_errors}")
            print(f"PASS {page_name} {width}x{height}: layout, navigation, assets and content")
            page.close()

    page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
    page.goto(urljoin(BASE, "index.html?utm_source=qa&utm_medium=browser"), wait_until="networkidle")
    stored = page.evaluate("sessionStorage.getItem('zenith_attribution')")
    check(stored is not None and 'qa' in stored and 'browser' in stored, "UTM attribution was not retained")
    internal_href = page.locator(".focus-card a").first.get_attribute("href") or ""
    check("utm_source=qa" in internal_href and "utm_medium=browser" in internal_href, f"UTM attribution not carried to service page: {internal_href}")
    page.locator(".contact-primary").scroll_into_view_if_needed()
    page.evaluate("document.querySelector('.contact-primary').addEventListener('click', event => event.preventDefault(), {once:true})")
    page.locator(".contact-primary").click()
    tracked = page.evaluate("window.dataLayer.at(-1)")
    check(tracked and tracked.get("action") == "contact_text" and tracked.get("page") == "home", f"lead tracking wrong: {tracked}")
    print("PASS analytics: UTM retention across pages and page-specific lead tracking")
    page.close()

    page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, reduced_motion="reduce")
    page.goto(urljoin(BASE, "index.html"), wait_until="networkidle")
    animation = page.locator(".scan-line").evaluate("n => getComputedStyle(n).display")
    check(animation == "none", "reduced-motion preference does not disable decorative scan")
    print("PASS accessibility: reduced-motion mode disables decorative scans")
    page.close()

    browser.close()

print("RESPONSIVE QA PASSED")
