#!/usr/bin/env python3
import os, sys, urllib.request
from pathlib import Path
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

BASE=os.environ.get("SITE_URL","http://127.0.0.1:4173/")
AXE=Path("/tmp/zenith-axe.min.js")
if not AXE.exists():
    urllib.request.urlretrieve("https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js",AXE)
PAGES=("","nmea-networks.html","marine-electronics.html","marine-radio-fcc.html")
fail=[]
with sync_playwright() as p:
    browser=p.chromium.launch()
    for width in (390,1440):
        page=browser.new_page(viewport={"width":width,"height":900})
        for path in PAGES:
            page.goto(urljoin(BASE,path),wait_until="networkidle")
            page.add_script_tag(path=str(AXE))
            result=page.evaluate("""async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}})""")
            for v in result["violations"]:
                nodes=[n["target"] for n in v["nodes"]]
                fail.append(f"{width}px {path or 'index.html'}: {v['id']} ({v.get('impact')}) {nodes}")
        page.close()
    browser.close()
if fail:
    print("ACCESSIBILITY QA FAILED")
    print("\n".join(f"- {x}" for x in fail))
    sys.exit(1)
print("ACCESSIBILITY QA PASSED: 8 axe/WCAG page-width checks")
