from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
URL = "http://100.122.63.73:4173/"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


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
          return [{tag: node.tagName, cls: node.className || '', text: (node.textContent || '').trim().slice(0, 60), left: r.left, right: r.right, width: r.width}];
        }
        return [];
      });
      return {
        viewport: [innerWidth, innerHeight],
        document: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
        horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
        header: rect('.header-inner'),
        brand: rect('.brand'),
        headerCta: rect('.header-cta'),
        eyebrow: rect('.hero .eyebrow'),
        headline: rect('.hero h1'),
        heroActions: rect('.hero-actions'),
        mobileCta: rect('.mobile-cta'),
        sections: {
          hero: rect('.hero'),
          services: rect('.services'),
          precision: rect('.precision'),
          credentials: rect('.credentials'),
          contact: rect('.contact'),
          footer: rect('.site-footer')
        },
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

    desktop = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
    desktop.goto(URL, wait_until="networkidle")
    desktop.wait_for_timeout(1200)
    inspect(desktop, "DESKTOP")
    desktop.screenshot(path=ROOT / "qa" / "desktop-full.png", full_page=True)
    for name in ("services", "precision", "credentials", "contact"):
        locator = desktop.locator(f".{name}")
        locator.scroll_into_view_if_needed()
        desktop.wait_for_timeout(500)
        locator.screenshot(path=ROOT / "qa" / f"desktop-{name}.png")

    mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True)
    mobile.goto(URL, wait_until="networkidle")
    mobile.wait_for_timeout(1200)
    inspect(mobile, "MOBILE")
    mobile.screenshot(path=ROOT / "qa" / "mobile-full.png", full_page=True)
    for name in ("services", "precision", "credentials", "contact"):
        locator = mobile.locator(f".{name}")
        locator.scroll_into_view_if_needed()
        mobile.wait_for_timeout(500)
        locator.screenshot(path=ROOT / "qa" / f"mobile-{name}.png")

    browser.close()
