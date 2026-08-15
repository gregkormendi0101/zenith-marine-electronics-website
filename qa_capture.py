from pathlib import Path
import os
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
OUT = ROOT / "qa" / "blueprint"
OUT.mkdir(parents=True, exist_ok=True)
BASE = os.environ.get("ZENITH_QA_URL", "http://127.0.0.1:4173/").rstrip("/") + "/"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGES = {
    "home": "index.html",
    "nmea": "nmea-networks.html",
    "electronics": "marine-electronics.html",
    "radio": "marine-radio-fcc.html",
}


def inspect(page, label: str) -> None:
    metrics = page.evaluate("""
    () => ({
      viewport: [innerWidth, innerHeight],
      document: [document.documentElement.scrollWidth, document.documentElement.scrollHeight],
      overflow: document.documentElement.scrollWidth > innerWidth,
      h1: document.querySelector('h1')?.textContent.trim(),
      cards: document.querySelectorAll('.focus-card').length,
      diagrams: document.querySelectorAll('img[src^="assets/diagrams/"]').length,
      imageFailures: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src)
    })
    """)
    print(label, metrics)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME, args=["--disable-background-networking", "--disable-component-update", "--disable-sync", "--no-first-run"])

    for device, width, height, mobile in (("desktop", 1440, 1000, False), ("mobile", 390, 844, True)):
        for page_name, path in PAGES.items():
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1, is_mobile=mobile)
            page.goto(urljoin(BASE, path), wait_until="networkidle")
            page.eval_on_selector_all("img[loading='lazy']", "nodes => nodes.forEach(node => node.loading = 'eager')")
            page.wait_for_function("Array.from(document.images).every(image => image.complete && image.naturalWidth > 0)", timeout=10000)
            page.wait_for_timeout(180)
            inspect(page, f"{device.upper()} {page_name.upper()}")

            page.screenshot(path=OUT / f"{device}-{page_name}-top.png", animations="disabled")
            page.screenshot(path=OUT / f"{device}-{page_name}-full.png", full_page=True, animations="disabled")

            page.add_style_tag(content=".qa-crop .site-header,.qa-crop .scan-line,.qa-crop .skip-link{display:none!important}")
            page.evaluate("document.documentElement.classList.add('qa-crop')")
            selectors = {"home": ".focus-grid", "nmea": ".hero-blueprint", "electronics": ".hero-blueprint", "radio": ".hero-blueprint"}
            locator = page.locator(selectors[page_name])
            locator.scroll_into_view_if_needed()
            page.wait_for_timeout(180)
            locator.screenshot(path=OUT / f"{device}-{page_name}-diagram.png", animations="disabled")
            page.close()

    browser.close()

print(f"CAPTURES WRITTEN: {OUT}")
