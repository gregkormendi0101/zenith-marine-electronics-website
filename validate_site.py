#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
PAGES = {
    "index.html": "https://zenithmarineelectronics.com/",
    "nmea-networks.html": "https://zenithmarineelectronics.com/nmea-networks.html",
    "marine-electronics.html": "https://zenithmarineelectronics.com/marine-electronics.html",
    "marine-radio-fcc.html": "https://zenithmarineelectronics.com/marine-radio-fcc.html",
}
SERVICE_PAGES = [name for name in PAGES if name != "index.html"]
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
    path = split.path
    if not path:
        return None
    return ROOT / path


soups: dict[str, BeautifulSoup] = {}
all_html = ""
for filename, canonical in PAGES.items():
    path = ROOT / filename
    check(path.exists(), f"missing page: {filename}")
    if not path.exists():
        continue
    source = path.read_text(encoding="utf-8")
    all_html += source + "\n"
    soup = BeautifulSoup(source, "html.parser")
    soups[filename] = soup

    check(len(soup.find_all("h1")) == 1, f"{filename}: expected exactly one h1")
    canonical_tag = soup.find("link", rel="canonical")
    check(bool(canonical_tag and canonical_tag.get("href") == canonical), f"{filename}: incorrect canonical")
    check(bool(soup.find("meta", attrs={"name": "description", "content": True})), f"{filename}: missing meta description")
    check(bool(soup.find("meta", attrs={"property": "og:image", "content": True})), f"{filename}: missing social image")
    check(len(soup.select(".primary-nav a")) == 3, f"{filename}: primary navigation must expose all three specialties")
    check(soup.get_text(" ", strip=True).count("305-306-6391") == 1, f"{filename}: visible phone number must appear exactly once")

    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    check(len(scripts) == 1, f"{filename}: expected one JSON-LD block")
    for block in scripts:
        try:
            json.loads(block.string or block.get_text())
        except Exception as exc:
            errors.append(f"{filename}: invalid JSON-LD: {exc}")

    for tag in soup.find_all(["a", "img", "link", "script", "source"]):
        for attr in ("href", "src", "srcset"):
            raw = tag.get(attr)
            if not raw:
                continue
            candidates = [part.strip().split(" ")[0] for part in raw.split(",")] if attr == "srcset" else [raw]
            for candidate in candidates:
                target = local_target(candidate)
                check(target is None or target.exists(), f"{filename}: broken local reference {candidate}")

    for image in soup.find_all("img"):
        check(image.has_attr("alt"), f"{filename}: image missing alt text: {image.get('src')}")
        check(image.has_attr("width") and image.has_attr("height"), f"{filename}: image missing intrinsic dimensions: {image.get('src')}")

    lowered = source.lower()
    check("assets/diagrams" not in lowered, f"{filename}: retired diagram asset referenced")
    check("blueprint" not in lowered, f"{filename}: retired blueprint language remains")
    check("fcc inspector" not in lowered, f"{filename}: bare FCC inspector wording is not allowed")

home = soups.get("index.html")
if home:
    tabs = home.select("[data-system-target]")
    panels = home.select("[data-system-panel]")
    check(len(tabs) == 3, "home: expected exactly three system tabs")
    check(len(panels) == 3, "home: expected exactly three system panels")
    check({t.get("data-system-target") for t in tabs} == {"nmea", "electronics", "radio"}, "home: incorrect system tab names")
    check({p.get("data-system-panel") for p in panels} == {"nmea", "electronics", "radio"}, "home: incorrect system panel names")
    for target in ("nmea-networks.html", "marine-electronics.html", "marine-radio-fcc.html"):
        check(bool(home.find("a", href=target)), f"home: missing dedicated-page link to {target}")
    visible = home.get_text(" ", strip=True).lower()
    for phrase in ("nmea networks", "marine electronics", "marine radio + fcc", "fcc ship-radio inspections"):
        check(phrase in visible, f"home: missing offer phrase '{phrase}'")

for filename in SERVICE_PAGES:
    soup = soups.get(filename)
    if not soup:
        continue
    check(len(soup.select(".scope-grid > article")) == 3, f"{filename}: expected three scope lanes")
    check(len(soup.select(".process-section ol > li")) == 4, f"{filename}: expected four process steps")
    check(len(soup.select(".service-switcher > a")) == 2, f"{filename}: expected two specialty switcher links")
    check(len(soup.select(".detail-visual")) == 1, f"{filename}: expected one primary system visual")

check(all_html.count("assets/credentials/nmea.jpg") == 1, "site: official NMEA logo must appear exactly once")
for forbidden in ("black swan marine", "92157 overseas", "3324 deer creek", "4251 nw 5th", "pg00081279", "#8033", "#6332"):
    check(forbidden not in all_html.lower(), f"site: private, stale or superseded text found: {forbidden}")

css = (ROOT / "styles.css").read_text(encoding="utf-8")
check("blueprint" not in css.lower(), "styles.css: retired blueprint styling remains")
check("grid-template" in css, "styles.css: expected responsive layout rules")
check("prefers-reduced-motion" in css, "styles.css: missing reduced-motion support")

script = (ROOT / "script.js").read_text(encoding="utf-8")
for required in ("data-system-target", "IntersectionObserver", "utm_source", "lead_action", "--parallax-y"):
    check(required in script, f"script.js: missing behavior marker {required}")

sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
for canonical in PAGES.values():
    check(canonical in sitemap, f"sitemap missing {canonical}")

referenced_renders = set(re.findall(r"assets/renders/[a-z0-9-]+\.webp", all_html))
actual_renders = {str(path.relative_to(ROOT)) for path in (ROOT / "assets" / "renders").glob("*.webp")}
check(referenced_renders == actual_renders, f"render references differ from production files: refs={sorted(referenced_renders)} files={sorted(actual_renders)}")

for path in (ROOT / "assets").rglob("*"):
    if not path.is_file() or path.name == ".DS_Store":
        continue
    size = path.stat().st_size
    check(size <= MAX_ASSET_BYTES, f"asset exceeds 400KB: {path.relative_to(ROOT)} ({size} bytes)")

if errors:
    print(f"VALIDATION FAILED ({len(errors)} issue(s))")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("VALIDATION PASSED")
print(f"- pages: {len(PAGES)}")
print(f"- home systems: {len(home.select('[data-system-panel]')) if home else 0}")
print(f"- production renders: {len(actual_renders)}")
print("- public wording, metadata, references, privacy and asset budget: pass")
