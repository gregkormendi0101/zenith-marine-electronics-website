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
MEASUREMENT_ID = "G-H8KGT9K2TM"
MAX_ASSET_BYTES = 400 * 1024
SERVICE_PAGES = {
    "nmea-2000-troubleshooting-upper-florida-keys.html": "NMEA 2000 troubleshooting",
    "marine-starlink-installation-upper-florida-keys.html": "Marine Starlink installation",
    "vhf-dsc-ais-service-upper-florida-keys.html": "Marine VHF, DSC and AIS service",
}
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
check(len(soup.select("[data-service-card]")) == 3, "expected exactly three service cards")
check(len(soup.select(".qualification")) == 4, "expected four verified qualification labels")
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
for phrase in ("NMEA 2000 networks", "Marine Starlink", "VHF & FCC inspections", "Key Largo", "Tavernier", "Islamorada"):
    check(phrase in visible, f"missing public offer phrase: {phrase}")
check(all(term in soup.select_one(".hero").get_text(" ") for term in ("NMEA", "Starlink", "VHF", "FCC")), "first-view offer is incomplete")
check(len(soup.select(f'a[href="tel:{PHONE}"]')) >= 1, "telephone action is missing or inconsistent")
check(len(soup.select(f'a[href="sms:{PHONE}"]')) >= 1, "SMS fallback is missing or inconsistent")
check(not soup.select(".morph-status, .morph-instruction"), "hero-state labels remain")
check(bool(soup.select_one('a[href="privacy.html"]')), "privacy policy is not linked from the footer")
check(f"googletagmanager.com/gtag/js?id={MEASUREMENT_ID}" in source, "GA4 loader is missing or incorrect")
check(source.count(MEASUREMENT_ID) >= 2, "GA4 measurement ID is not configured")

lowered = source.lower()
for forbidden in ("black swan marine", "92157 overseas", "3324 deer creek", "4251 nw 5th", "pg00081279", "#8033", "#6332", "fcc inspector", "fully insured"):
    check(forbidden not in lowered, f"private, stale, or unapproved wording found: {forbidden}")
for old_page in ("nmea-networks.html", "marine-electronics.html", "marine-radio-fcc.html"):
    check(not (ROOT / old_page).exists(), f"retired page remains: {old_page}")

css = (ROOT / "harbor.css").read_text(encoding="utf-8")
for raw in re.findall(r'url\(["\']?([^"\')]+)', css):
    target = local_target(raw)
    check(target is None or target.exists(), f"missing CSS asset: {raw}")
check("prefers-reduced-motion" in css, "missing reduced-motion support")

script = (ROOT / "harbor.js").read_text(encoding="utf-8")
for marker in (
    "window.ZenithBooking",
    "window.ZenithAnalytics",
    'trackEvent("service_select"',
    'trackEvent("sms_open"',
    'trackEvent("call_click"',
):
    check(marker in script, f"app.js missing behavior marker: {marker}")
check("generate_lead" not in script, "click instrumentation must not claim a confirmed lead")

for filename, expected_h1 in SERVICE_PAGES.items():
    path = ROOT / filename
    check(path.exists(), f"missing service landing page: {filename}")
    check(f'href="{filename}"' in source, f"home page does not link service page: {filename}")
    if not path.exists():
        continue

    service_source = path.read_text(encoding="utf-8")
    service_soup = BeautifulSoup(service_source, "html.parser")
    service_h1 = service_soup.find_all("h1")
    check(len(service_h1) == 1, f"{filename}: expected exactly one h1")
    if service_h1:
        check(expected_h1.lower() in service_h1[0].get_text(" ", strip=True).lower(), f"{filename}: incorrect h1")
    check(bool(service_soup.find("meta", attrs={"name": "description", "content": True})), f"{filename}: missing meta description")
    service_canonical = service_soup.find("link", rel="canonical")
    check(bool(service_canonical and service_canonical.get("href") == f"{CANONICAL}{filename}"), f"{filename}: incorrect canonical")
    check(f"googletagmanager.com/gtag/js?id={MEASUREMENT_ID}" in service_source, f"{filename}: missing GA4 loader")
    check(bool(service_soup.select_one("form[data-booking-form]")), f"{filename}: missing request form")
    check(bool(service_soup.select_one("#service option[selected]")), f"{filename}: service is not preselected")
    check(len(service_soup.select(f'a[href="tel:{PHONE}"]')) >= 3, f"{filename}: telephone actions missing")
    check(bool(service_soup.select_one(f'a[href="sms:{PHONE}"]')), f"{filename}: SMS fallback missing")
    check(bool(service_soup.select_one('link[href^="service-pages.css"]')), f"{filename}: service CSS missing")

    for tag in service_soup.find_all(["a", "img", "link", "script", "source"]):
        for attr in ("href", "src", "srcset"):
            raw = tag.get(attr)
            if not raw:
                continue
            candidates = [part.strip().split(" ")[0] for part in raw.split(",")] if attr == "srcset" else [raw]
            for candidate in candidates:
                target = local_target(candidate)
                check(target is None or target.exists(), f"{filename}: broken local reference: {candidate}")

    service_schemas = service_soup.find_all("script", attrs={"type": "application/ld+json"})
    check(len(service_schemas) == 1, f"{filename}: expected one JSON-LD block")
    for block in service_schemas:
        try:
            data = json.loads(block.string or block.get_text())
            types = {item.get("@type") for item in data.get("@graph", []) if isinstance(item, dict)}
            check({"Service", "FAQPage"}.issubset(types), f"{filename}: JSON-LD lacks Service or FAQPage")
        except Exception as exc:
            errors.append(f"{filename}: invalid JSON-LD: {exc}")

    service_lowered = service_source.lower()
    for forbidden in ("92157 overseas", "3324 deer creek", "4251 nw 5th", "pg00081279", "#8033", "#6332", "fcc inspector", "fully insured"):
        check(forbidden not in service_lowered, f"{filename}: private or unapproved wording found: {forbidden}")

privacy_path = ROOT / "privacy.html"
check(privacy_path.exists(), "missing privacy.html")
if privacy_path.exists():
    privacy_source = privacy_path.read_text(encoding="utf-8")
    privacy_text = BeautifulSoup(privacy_source, "html.parser").get_text(" ", strip=True)
    for phrase in ("Google Analytics", "prepared text message", "campaign attribution", "305-306-6391"):
        check(phrase in privacy_text, f"privacy policy missing disclosure: {phrase}")

check('noindex' not in source.lower(), "production contains noindex")
check('DESIGN PREVIEW' not in source and 'Private design preview' not in source, "preview labels remain")
for anchor in ('book','qualifications','service-area','nmea-service','starlink-service','radio-service'):
    check(bool(soup.find(id=anchor)), f"missing legacy anchor: {anchor}")
check(bool(soup.select_one('#prepare-text[disabled]')), "no-JS builder must default disabled")

check((ROOT / "CNAME").read_text(encoding="utf-8").strip() == "zenithmarineelectronics.com", "CNAME is wrong")
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
check(CANONICAL in sitemap, "sitemap lacks canonical URL")
check(f"{CANONICAL}privacy.html" in sitemap, "sitemap lacks privacy URL")
for filename in SERVICE_PAGES:
    check(f"{CANONICAL}{filename}" in sitemap, f"sitemap lacks service page: {filename}")
check("Sitemap: https://zenithmarineelectronics.com/sitemap.xml" in (ROOT / "robots.txt").read_text(encoding="utf-8"), "robots.txt lacks sitemap")
check((ROOT / "assets/images/harbor-social.webp").exists(), "social image is missing")

for path in (ROOT / "assets").rglob("*"):
    if path.is_file() and path.name != ".DS_Store":
        check(path.stat().st_size <= MAX_ASSET_BYTES, f"asset exceeds 400KB: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")

if errors:
    print(f"VALIDATION FAILED ({len(errors)} issue(s))")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("VALIDATION PASSED")
print("- Harbor homepage with preserved high-intent service pages")
print("- metadata, JSON-LD, canonical, sitemap, robots, and CNAME: pass")
print("- public wording, privacy limits, local references, and asset budget: pass")
print("- GA4 loader/events and privacy disclosure: pass")
print("- three expandable service lanes, prepared SMS, and reduced motion: pass")
