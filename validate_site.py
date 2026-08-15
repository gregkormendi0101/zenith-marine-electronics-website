from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
PAGES = {
    "index.html": "https://zenithmarineelectronics.com/",
    "nmea-networks.html": "https://zenithmarineelectronics.com/nmea-networks.html",
    "marine-electronics.html": "https://zenithmarineelectronics.com/marine-electronics.html",
    "marine-radio-fcc.html": "https://zenithmarineelectronics.com/marine-radio-fcc.html",
}
DIAGRAMS = {
    "assets/diagrams/nmea-backbone.svg": ("120 Ω", "FUSED 12 VDC", "NMEA 2000 BACKBONE", "END TERMINATOR"),
    "assets/diagrams/helm-panel.svg": ("MULTIFUNCTION DISPLAY", "PROTECTED 12 VDC", "NMEA DATA", "VHF ANTENNA", "TRANSDUCER SIGNAL"),
    "assets/diagrams/vhf-radio.svg": ("VHF / DSC", "50 Ω COAX", "FUSED 12 VDC", "GPS POSITION", "SHIP-RADIO CHECKPOINTS"),
}
CSS = ROOT / "styles.css"
JS = ROOT / "script.js"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.canonicals: list[str] = []
        self.json_ld: list[str] = []
        self._json_buffer: list[str] | None = None

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
            if data.get("rel") == "canonical":
                self.canonicals.append(data["href"])
        if tag in {"img", "script"} and data.get("src"):
            self.refs.append((tag, data["src"]))
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])
        if tag == "script" and data.get("type") == "application/ld+json":
            self._json_buffer = []

    def handle_data(self, data: str) -> None:
        if self._json_buffer is not None:
            self._json_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_buffer is not None:
            self.json_ld.append("".join(self._json_buffer))
            self._json_buffer = None


def local_path(ref: str) -> Path | None:
    parsed = urlparse(ref)
    if parsed.scheme or ref.startswith(("#", "data:", "mailto:", "tel:", "sms:")):
        return None
    return ROOT / parsed.path


errors: list[str] = []
all_html = ""
all_links: list[str] = []
image_count = 0
ref_count = 0

for filename, canonical in PAGES.items():
    path = ROOT / filename
    if not path.exists():
        errors.append(f"missing page: {filename}")
        continue
    html = path.read_text(encoding="utf-8")
    all_html += "\n" + html
    parser = SiteParser()
    try:
        parser.feed(html)
    except AssertionError as exc:
        errors.append(f"{filename}: {exc}")
        continue

    if parser.canonicals != [canonical]:
        errors.append(f"{filename}: canonical mismatch {parser.canonicals}")
    if '<meta name="viewport"' not in html:
        errors.append(f"{filename}: viewport meta missing")
    if not parser.json_ld:
        errors.append(f"{filename}: structured data missing")
    for block in parser.json_ld:
        try:
            json.loads(block)
        except json.JSONDecodeError as exc:
            errors.append(f"{filename}: invalid structured data: {exc}")

    for tag, ref in parser.refs:
        local = local_path(ref)
        if local and not local.exists():
            errors.append(f"{filename}: missing {tag} asset {ref}")
    for image in parser.images:
        if "alt" not in image:
            errors.append(f"{filename}: image missing alt {image.get('src')}")
    for href in parser.links:
        parsed = urlparse(href)
        if href.startswith("#") and href[1:] not in parser.ids:
            errors.append(f"{filename}: anchor target missing {href}")
        elif not parsed.scheme and not href.startswith(("#", "tel:", "sms:")):
            target = parsed.path or filename
            if target.endswith(".html") and not (ROOT / target).exists():
                errors.append(f"{filename}: local page link missing {href}")
    all_links.extend(parser.links)
    image_count += len(parser.images)
    ref_count += len(parser.refs)

css = CSS.read_text(encoding="utf-8")
js = JS.read_text(encoding="utf-8")
if css.count("{") != css.count("}"):
    errors.append("CSS braces are unbalanced")
if js.count("{") != js.count("}"):
    errors.append("JS braces are unbalanced")
for match in re.findall(r'url\(["\']?([^"\')]+)', css):
    if match.startswith(("data:", "%23", "#")):
        continue
    local = local_path(match)
    if local and not local.exists():
        errors.append(f"missing CSS asset: {match}")

for diagram, required_labels in DIAGRAMS.items():
    path = ROOT / diagram
    if not path.exists():
        errors.append(f"missing blueprint diagram: {diagram}")
        continue
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        errors.append(f"invalid SVG {diagram}: {exc}")
    source = path.read_text(encoding="utf-8")
    for label in required_labels:
        if label not in source:
            errors.append(f"{diagram}: required technical label missing: {label}")

home = (ROOT / "index.html").read_text(encoding="utf-8")
for page in PAGES:
    if page != "index.html" and f'href="{page}"' not in home:
        errors.append(f"home page does not link to {page}")
for diagram in DIAGRAMS:
    if home.count(diagram) != 1:
        errors.append(f"home must show blueprint once: {diagram}")
if all_html.count("assets/credentials/nmea.jpg") != 1:
    errors.append("site must use exactly one official NMEA logo")

required_home_copy = (
    "NMEA Networks",
    "Marine Electronics",
    "Marine Radio + FCC",
    "FCC ship-radio inspections",
)
for phrase in required_home_copy:
    if phrase.lower() not in home.lower():
        errors.append(f"home page does not state core specialty: {phrase}")

for forbidden in (
    "Black Swan",
    "Limited launch",
    "Inquiries now",
    "Basic NMEA 2000 Installer",
    "Certificate numbers intentionally not published",
    "FCC inspector",
    "dock-1440.webp",
    "helm-1440.webp",
    "hero-2400.webp",
    "navigation-display",
    "radio-console",
):
    if forbidden.lower() in all_html.lower():
        errors.append(f"stale or misleading public content remains: {forbidden}")

for private in ("8033", "6332", "0012151111", "0031214232", "92157 Overseas", "3324 Deer Creek", "4251 NW"):
    if private in all_html:
        errors.append(f"private credential/address data exposed: {private}")

phone_links = re.findall(r'href="(?:tel|sms):([^"?]+)', all_html)
if not phone_links or any("3053066391" not in value or "*" in value for value in phone_links):
    errors.append("phone or SMS link is missing/malformed")

sitemap_text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
for canonical in PAGES.values():
    if f"<loc>{canonical}</loc>" not in sitemap_text:
        errors.append(f"sitemap missing {canonical}")

asset_summary: list[str] = []
for path in sorted((ROOT / "assets").rglob("*")):
    if not path.is_file():
        continue
    size_kb = round(path.stat().st_size / 1024)
    if size_kb > 400:
        errors.append(f"production asset is too large: {path.relative_to(ROOT)} ({size_kb} KB)")
    asset_summary.append(f"{path.relative_to(ROOT)}: {size_kb} KB")

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("VALIDATION PASSED")
print(f"- {len(PAGES)} pages have canonical URLs, viewport metadata and valid JSON-LD")
print(f"- {image_count} images have alt attributes; {ref_count} local references resolve")
print("- home page leads with all three specialties and links to each dedicated page")
print("- three blueprint SVGs parse and include required technical labels")
print("- one NMEA logo; no stock-photo references, stale branding, private IDs or addresses")
print("- sitemap contains all four public URLs; phone/SMS links are valid")
print("ASSETS")
for item in asset_summary:
    print(f"- {item}")
