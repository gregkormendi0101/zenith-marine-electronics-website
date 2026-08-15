#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE = os.environ.get("SITE_URL", "http://127.0.0.1:4173/")
OUT = Path(__file__).resolve().parent / "qa" / "futuristic"
OUT.mkdir(parents=True, exist_ok=True)
PAGES = {
    "home": "",
    "nmea": "nmea-networks.html",
    "electronics": "marine-electronics.html",
    "radio": "marine-radio-fcc.html",
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    for label, viewport in (("desktop", {"width": 1440, "height": 1000}), ("mobile", {"width": 390, "height": 844})):
        context = browser.new_context(viewport=viewport, device_scale_factor=1)
        page = context.new_page()
        for name, path in PAGES.items():
            page.goto(urljoin(BASE, path), wait_until="networkidle")
            page.evaluate("""async () => {
              const step = Math.max(500, Math.floor(innerHeight * .75));
              for (let y = 0; y < document.body.scrollHeight; y += step) {
                window.scrollTo(0, y);
                await new Promise((resolve) => setTimeout(resolve, 35));
              }
              window.scrollTo(0, 0);
              await new Promise((resolve) => setTimeout(resolve, 800));
            }""")
            page.screenshot(path=str(OUT / f"{label}-{name}-top.png"), full_page=False)
            page.screenshot(path=str(OUT / f"{label}-{name}-full.png"), full_page=True)
        page.goto(BASE, wait_until="networkidle")
        page.locator("#systems").scroll_into_view_if_needed()
        page.wait_for_timeout(800)
        for target in ("nmea", "electronics", "radio"):
            page.locator(f'[data-system-target="{target}"]').click()
            page.wait_for_timeout(180)
            page.locator(".system-console").screenshot(path=str(OUT / f"{label}-console-{target}.png"))
        context.close()
    browser.close()

print(f"CAPTURE QA PASSED: {OUT}")
print("- 8 viewport captures + 6 interactive console captures")
