#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
CANONICAL = "https://zenithmarineelectronics.com/"
PHONE = "+13053066391"
MAX_ASSET_BYTES = 400 * 1024
errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def local_target(raw: str) -> Path | None:
    if not raw or raw.startswith(("#", "tel:", "sms:", "mailto:", "data:", "javascript:")):
        return None
    split = urlsplit(raw)
    if split.scheme or split.netloc:
        return None
    return ROOT / split.path


html_path = ROOT / "index.html"
check(html_path.exists(), "missing index.html")
source = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
soup = BeautifulSoup(source, "html.parser")

check(len(soup.find_all("h1")) == 1, "expected exactly one h1")
check(len(soup.select(".service-card")) == 3, "expected exactly three service cards")
check(len(soup.select(".service-symbol")) == 3, "expected exactly three service symbols")
check(bool(soup.find("meta", attrs={"name": "description", "content": True})), "missing meta description")
canonical = soup.find("link", rel="canonical")
check(bool(canonical and canonical.get("href") == CANONICAL), "incorrect canonical URL")
for prop in ("og:title", "og:description", "og:url", "og:image"):
    check(bool(soup.find("meta", attrs={"property": prop, "content": True})), f"missing {prop}")
for name in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
    check(bool(soup.find("meta", attrs={"name": name, "content": True})), f"missing {name}")

schemas = soup.find_all("script", attrs={"type": "application/ld+json"})
check(len(schemas) == 1, "expected one JSON-LD block")
for block in schemas:
    try:
        data = json.loads(block.string or block.get_text())
        check(data.get("url") == CANONICAL, "JSON-LD canonical URL is wrong")
        check(re.sub(r"\D", "", data.get("telephone", "")) == PHONE.lstrip("+"), "JSON-LD telephone is wrong")
    except Exception as exc:
        errors.append(f"invalid JSON-LD: {exc}")

for tag in soup.find_all(["a", "img", "link", "script", "source"]):
    for attr in ("href", "src", "srcset"):
        raw = tag.get(attr)
        if not raw:
            continue
        candidates = [part.strip().split(" ")[0] for part in raw.split(",")] if attr == "srcset" else [raw]
        for candidate in candidates:
            target = local_target(candidate)
            check(target is None or target.exists(), f"broken local reference: {candidate}")

for image in soup.find_all("img"):
    check(image.has_attr("alt"), f"image missing alt text: {image.get('src')}")
    check(image.has_attr("width") and image.has_attr("height"), f"image missing intrinsic dimensions: {image.get('src')}")

visible = soup.get_text(" ", strip=True)
for phrase in ("NMEA 2000 Networks", "Starlink Systems", "VHF Radio & FCC Inspections", "Key Largo", "Tavernier", "Islamorada"):
    check(phrase in visible, f"missing public offer phrase: {phrase}")
check(all(term in (soup.find("h1").get_text(" ") if soup.find("h1") else "") for term in ("NMEA", "Starlink", "VHF", "FCC")), "first-view offer is incomplete")
check(len(soup.select(f'a[href="tel:{PHONE}"]')) >= 3, "telephone actions are missing or inconsistent")
check(len(soup.select(f'a[href="sms:{PHONE}"]')) >= 1, "SMS fallback is missing or inconsistent")
check(not soup.select(".morph-status, .morph-instruction"), "hero-state labels remain")

lowered = source.lower()
for forbidden in ("black swan marine", "92157 overseas", "3324 deer creek", "4251 nw 5th", "pg00081279", "#8033", "#6332", "fcc inspector", "fully insured"):
    check(forbidden not in lowered, f"private, stale, or unapproved wording found: {forbidden}")
for old_page in ("nmea-networks.html", "marine-electronics.html", "marine-radio-fcc.html"):
    check(not (ROOT / old_page).exists(), f"retired page remains: {old_page}")

css = (ROOT / "styles.css").read_text(encoding="utf-8")
for raw in re.findall(r'url\(["\']?([^"\')]+)', css):
    target = local_target(raw)
    check(target is None or target.exists(), f"missing CSS asset: {raw}")
check("prefers-reduced-motion" in css, "missing reduced-motion support")

script = (ROOT / "app.js").read_text(encoding="utf-8")
for marker in ("window.ZenithBooking", "window.ZenithMorph", "requestAnimationFrame"):
    check(marker in script, f"app.js missing behavior marker: {marker}")

for blueprint_name in ("hero-blueprint.svg", "hero-blueprint-mobile.svg"):
    blueprint = (ROOT / "assets" / blueprint_name).read_text(encoding="utf-8")
    check("<image" not in blueprint, f"{blueprint_name} embeds raster artwork")
    check("<text" not in blueprint, f"{blueprint_name} contains visible text")
    check(blueprint.count("<path") >= 20, f"{blueprint_name} lacks drafted linework")

check((ROOT / "CNAME").read_text(encoding="utf-8").strip() == "zenithmarineelectronics.com", "CNAME is wrong")
check(CANONICAL in (ROOT / "sitemap.xml").read_text(encoding="utf-8"), "sitemap lacks canonical URL")
check("Sitemap: https://zenithmarineelectronics.com/sitemap.xml" in (ROOT / "robots.txt").read_text(encoding="utf-8"), "robots.txt lacks sitemap")
check((ROOT / "assets/images/social.webp").exists(), "social image is missing")

for path in (ROOT / "assets").rglob("*"):
    if path.is_file() and path.name != ".DS_Store":
        check(path.stat().st_size <= MAX_ASSET_BYTES, f"asset exceeds 400KB: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")

if errors:
    print(f"VALIDATION FAILED ({len(errors)} issue(s))")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("VALIDATION PASSED")
print("- one-page Service First production build")
print("- metadata, JSON-LD, canonical, sitemap, robots, and CNAME: pass")
print("- public wording, privacy limits, local references, and asset budget: pass")
print("- vector blueprint, three service lanes, booking actions, and reduced motion: pass")
