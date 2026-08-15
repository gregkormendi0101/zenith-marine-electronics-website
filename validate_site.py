from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

ROOT = Path(__file__).parent
HTML = ROOT / "index.html"
CSS = ROOT / "styles.css"
JS = ROOT / "script.js"
SOURCES = ROOT / "ASSET_SOURCES.md"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.ids: set[str] = set()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if "id" in data:
            if data["id"] in self.ids:
                raise AssertionError(f"duplicate id: {data['id']}")
            self.ids.add(data["id"])
        if tag == "img":
            self.images.append(data)
        if tag == "link" and data.get("href"):
            self.refs.append((tag, data["href"]))
        if tag in {"img", "script"} and data.get("src"):
            self.refs.append((tag, data["src"]))
        if tag == "source" and data.get("srcset"):
            for candidate in data["srcset"].split(","):
                ref = candidate.strip().split()[0]
                if ref:
                    self.refs.append((tag, ref))
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])


def local_path(ref: str) -> Path | None:
    parsed = urlparse(ref)
    if parsed.scheme or ref.startswith(("#", "data:")):
        return None
    return ROOT / parsed.path


parser = SiteParser()
html = HTML.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")
js = JS.read_text(encoding="utf-8")
parser.feed(html)

errors: list[str] = []
for tag, ref in parser.refs:
    path = local_path(ref)
    if path and not path.exists():
        errors.append(f"missing {tag} asset: {ref}")

for image in parser.images:
    if "alt" not in image:
        errors.append(f"image missing alt: {image.get('src')}")

for href in parser.links:
    if href.startswith("#") and href[1:] not in parser.ids:
        errors.append(f"anchor target missing: {href}")

for match in re.findall(r'url\(["\']?([^"\')]+)', css):
    if match.startswith(("data:", "%23", "#")):
        continue
    path = local_path(match)
    if path and not path.exists():
        errors.append(f"missing CSS asset: {match}")

if css.count("{") != css.count("}"):
    errors.append("CSS braces are unbalanced")
if js.count("{") != js.count("}"):
    errors.append("JS braces are unbalanced")
if "<meta name=\"viewport\"" not in html:
    errors.append("viewport meta tag missing")
if "application/ld+json" not in html:
    errors.append("structured data missing")
else:
    match = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    try:
        json.loads(match.group(1) if match else "")
    except json.JSONDecodeError as exc:
        errors.append(f"structured data is invalid JSON: {exc}")

required_service_copy = (
    "NMEA networks",
    "Marine electronics installation",
    "Marine radio service",
    "FCC ship-radio inspections",
)
for required in required_service_copy:
    if required.lower() not in html.lower():
        errors.append(f"core service is not explicit in public copy: {required}")

private_values = (
    "8033",
    "6332",
    "0012151111",
    "0031214232",
    "92157 Overseas",
    "3324 Deer Creek",
    "4251 NW",
)
for forbidden in private_values:
    if forbidden in html:
        errors.append(f"private credential/address data exposed: {forbidden}")

stale_copy = (
    "Black Swan",
    "Limited launch",
    "Inquiries now",
    "scope review",
    "Basic NMEA 2000 Installer",
    "Certificate numbers intentionally not published",
    "FCC inspector",
)
for forbidden in stale_copy:
    if forbidden.lower() in html.lower():
        errors.append(f"stale or misleading public copy remains: {forbidden}")

stale_assets = (
    "dock-1440.webp",
    "dock-2560.webp",
    "helm-1440.webp",
    "helm-2560.webp",
    "hero-2560.webp",
    "hero-mobile-900.webp",
    "hero-mobile-1440.webp",
)
for forbidden in stale_assets:
    if forbidden in html:
        errors.append(f"superseded generated image remains referenced: {forbidden}")

if html.count('assets/credentials/nmea.jpg') != 1:
    errors.append("site must use exactly one official NMEA logo")
if any(mark in html for mark in ('assets/credentials/amei', 'assets/credentials/an2k')):
    errors.append("individual credential logos must not be published")
if html.count('class="system-diagram') != 3:
    errors.append("site must contain exactly three technical service diagrams")
if html.count("data-route") < 6:
    errors.append("scroll-driven route paths/dots are missing")
if not SOURCES.exists():
    errors.append("ASSET_SOURCES.md is missing")
else:
    source_text = SOURCES.read_text(encoding="utf-8")
    if "Unsplash License" not in source_text or "None of" not in source_text:
        errors.append("real-photo provenance is incomplete")

asset_summary = []
for path in sorted((ROOT / "assets").rglob("*")):
    if not path.is_file():
        continue
    size_kb = round(path.stat().st_size / 1024)
    dims = ""
    try:
        with Image.open(path) as image:
            dims = f" {image.width}x{image.height}"
    except Exception:
        pass
    if size_kb > 400:
        errors.append(f"production asset is too large: {path.relative_to(ROOT)} ({size_kb} KB)")
    asset_summary.append(f"{path.relative_to(ROOT)}: {size_kb} KB{dims}")

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("VALIDATION PASSED")
print(f"- {len(parser.images)} images have alt attributes")
print(f"- {len(parser.refs)} linked assets resolve")
print(f"- {len(parser.links)} links inspected; internal anchors resolve")
print("- three explicit service lanes and three technical diagrams present")
print("- superseded generated boat/dock images are not referenced")
print("- real-photo provenance is documented")
print("- no certificate numbers, FCC filing IDs, or residential addresses in public HTML")
print("- responsive viewport and valid JSON-LD present")
print("ASSETS")
for item in asset_summary:
    print(f"- {item}")
