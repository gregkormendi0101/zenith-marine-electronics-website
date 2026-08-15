from pathlib import Path
import os

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
URL = os.environ.get("ZENITH_QA_URL", "http://127.0.0.1:4173/").rstrip("/") + "/"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CAPTURES = {
    "hero": ".hero",
    "services": ".services-intro",
    "nmea": "#nmea",
    "installation": "#installation",
    "radio": "#radio",
    "credentials": ".credentials",
    "contact": ".contact",
}


def inspect(page, label: str) -> None:
    metrics = page.evaluate("""
    () => {
      const rect = (selector) => {
        const node = document.querySelector(selector);
        if (!node) return null;
        const r = node.getBoundingClientRect();
        return {x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom};
      };
      const offenders = [...document.querySelectorAll('body *')].flatMap((node) => {
        const style = getComputedStyle(node);
        const r = node.getBoundingClientRect();
        if (style.position === 'fixed' || style.position === 'absolute') return [];
        if (r.width > 0 && (r.left < -1 || r.right > innerWidth + 1)) {
          return [{tag: node.tagName, cls: String(node.className || '').slice(0, 80), text: (node.textContent || '').trim().slice(0, 60), left: r.left, right: r.right, width: r.width}];
        }
        return [];
      });
      return {
        viewport: [innerWidth, innerHeight],
        document: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
        horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
        header: rect('.header-inner'),
        brand: rect('.brand'),
        headerContact: rect('.header-contact'),
        eyebrow: rect('.hero .eyebrow'),
        headline: rect('.hero h1'),
        heroActions: rect('.hero-actions'),
        mobileLead: rect('.mobile-lead'),
        diagrams: document.querySelectorAll('.system-diagram').length,
        offenders,
        images: [...document.images].map((i) => ({src: i.currentSrc.split('/').pop(), complete: i.complete, width: i.naturalWidth, height: i.naturalHeight}))
      };
    }
    """)
    print(label, metrics)


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path=CHROME,
        args=["--disable-background-networking", "--disable-component-update", "--disable-sync", "--no-first-run"],
    )

    for label, width, height, mobile in (
        ("desktop", 1440, 1000, False),
        ("mobile", 390, 844, True),
    ):
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1, is_mobile=mobile)
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(700)
        page.eval_on_selector_all("img[loading='lazy']", "images => images.forEach(image => image.loading = 'eager')")
        page.add_style_tag(content=".qa-section-capture .site-header,.qa-section-capture .mobile-lead,.qa-section-capture .skip-link,.qa-section-capture .page-progress{display:none!important}")
        page.wait_for_timeout(350)
        inspect(page, label.upper())

        for name, selector in CAPTURES.items():
            locator = page.locator(selector)
            anchor = "top" if name == "hero" else name
            page.evaluate("hideChrome => document.documentElement.classList.toggle('qa-section-capture', hideChrome)", name != "hero")
            page.evaluate("id => window.scrollTo(0, Math.max(0, document.getElementById(id).offsetTop - 70))", anchor)
            page.wait_for_timeout(320)
            locator.screenshot(path=ROOT / "qa" / f"{label}-{name}.png")

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(450)
        page.screenshot(path=ROOT / "qa" / f"{label}-full.png", full_page=True)
        page.close()

    browser.close()
