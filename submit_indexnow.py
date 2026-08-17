#!/usr/bin/env python3
"""Submit Zenith's current sitemap URLs to IndexNow."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
SITEMAP = ROOT / "sitemap.xml"
ENDPOINT = "https://api.indexnow.org/indexnow"
EXPECTED_HOST = "zenithmarineelectronics.com"
KEY_FILE_RE = re.compile(r"^[A-Za-z0-9-]{8,128}\.txt$")


def find_key_file() -> tuple[Path, str]:
    matches: list[tuple[Path, str]] = []
    for path in ROOT.glob("*.txt"):
        if not KEY_FILE_RE.fullmatch(path.name):
            continue
        value = path.read_text(encoding="utf-8").strip()
        if value == path.stem:
            matches.append((path, value))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one valid IndexNow key file, found {len(matches)}")
    return matches[0]


def sitemap_urls() -> list[str]:
    root = ET.parse(SITEMAP).getroot()
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text.strip() for node in root.findall("sm:url/sm:loc", namespace) if node.text]
    if not urls:
        raise RuntimeError("No URLs found in sitemap.xml")
    bad = [url for url in urls if urlparse(url).hostname != EXPECTED_HOST]
    if bad:
        raise RuntimeError(f"Sitemap contains URLs outside {EXPECTED_HOST}: {bad}")
    return urls


def build_payload() -> dict[str, object]:
    key_file, key = find_key_file()
    return {
        "host": EXPECTED_HOST,
        "key": key,
        "keyLocation": f"https://{EXPECTED_HOST}/{key_file.name}",
        "urlList": sitemap_urls(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Validate without contacting IndexNow")
    args = parser.parse_args()

    payload = build_payload()
    urls = payload["urlList"]
    assert isinstance(urls, list)
    if args.dry_run:
        print(f"INDEXNOW DRY RUN PASSED: host={EXPECTED_HOST} urls={len(urls)}")
        return 0

    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "Zenith-IndexNow/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        print(f"INDEXNOW SUBMISSION FAILED: HTTP {exc.code}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"INDEXNOW SUBMISSION FAILED: {exc.reason}", file=sys.stderr)
        return 1

    if status not in {200, 202}:
        print(f"INDEXNOW SUBMISSION FAILED: HTTP {status}", file=sys.stderr)
        return 1
    print(f"INDEXNOW SUBMISSION ACCEPTED: HTTP {status}; urls={len(urls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
