#!/usr/bin/env python3
"""Harbor release QA, using the same suite locally and on public HTTPS."""
import functools
import http.server
import json
import os
from pathlib import Path
import threading
import urllib.request
from urllib.parse import urljoin, unquote
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'.qa-artifacts/harbor'
OUT.mkdir(parents=True,exist_ok=True)
server=None
BASE=os.environ.get('ZENITH_QA_URL','').rstrip('/')
if not BASE:
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    BASE=f'http://127.0.0.1:{server.server_port}'
AXE=urllib.request.urlopen('https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js',timeout=25).read().decode()
result={'base':BASE,'viewports':[],'checks':[]}
external=[]

def guard(route):
    req=route.request
    if 'googletagmanager.com/gtag/js' in req.url:
        route.fulfill(status=200,content_type='application/javascript',body='/* QA: tracking transport disabled */')
    elif req.url.startswith(BASE) and req.method=='GET':
        route.continue_()
    else:
        external.append(req.url)
        route.abort()

def persist():
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')

try:
    with sync_playwright() as p:
        b=p.chromium.launch()
        for width,height in [(320,780),(390,844),(430,932),(768,1024),(1024,900),(1440,1000)]:
            ctx=b.new_context(viewport={'width':width,'height':height})
            ctx.route('**/*',guard)
            ctx.add_init_script('window.__qaEvents=[];window.gtag=(...args)=>window.__qaEvents.push(args);')
            page=ctx.new_page()
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
            page.goto(BASE+'/?utm_source=harbor-qa&utm_medium=test&utm_campaign=release&ref=quality&email=DO_NOT_FORWARD',wait_until='networkidle')
            assert page.locator('h1').count()==1
            assert page.locator('[data-service-card]').count()==3
            assert page.locator('.qualification').count()==4
            assert page.locator('meta[name="robots"][content*="noindex"]').count()==0
            assert 'DESIGN PREVIEW' not in page.locator('body').inner_text()
            assert page.locator('link[rel="canonical"]').get_attribute('href')=='https://zenithmarineelectronics.com/'
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('img').evaluate_all('(es)=>es.every(e=>e.complete&&e.naturalWidth>0)')
            box=page.locator('.hero .button').bounding_box()
            assert box and box['y']<height-52
            for a in page.locator('a[href^="#"]').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'):
                assert page.locator(a).count()==1,a
            page.screenshot(path=str(OUT/f'{width}-full.png'),full_page=True)
            page.screenshot(path=str(OUT/f'{width}-first.png'))
            for key in ('nmea','starlink','radio'):
                details=page.locator(f'[data-service-card="{key}"]')
                details.locator('summary').focus();page.keyboard.press('Enter')
                assert details.evaluate('(e)=>e.open')
                link=details.locator('.service-page-link').get_attribute('href') or ''
                assert 'utm_source=harbor-qa' in link and 'DO_NOT_FORWARD' not in link
                button=details.locator('[data-select-service]')
                chosen=button.get_attribute('data-select-service');button.click()
                assert page.locator('#service').input_value()==chosen
                assert page.locator('#service').evaluate('(e)=>document.activeElement===e')
                details.evaluate('(e)=>e.open=false')
            assert page.evaluate('window.ZenithBooking.attribution().source')=='harbor-qa'
            page.locator('#location').fill('Tavernier')
            page.locator('#vessel').fill('PRIVATE_VESSEL_MARKER')
            page.locator('#details').fill('PRIVATE_REQUEST_MARKER — please diagnose the radio.')
            page.locator('#prepare-text').click()
            assert page.locator('#draft').is_visible()
            message=page.locator('#message-preview').input_value()
            assert 'Lead source: harbor-qa / test / release / quality' in message
            assert unquote((page.locator('#sms-link').get_attribute('href') or '').split('body=',1)[1])==message
            before=page.evaluate('window.__qaEvents.filter(e=>e[0]==="event").map(e=>e[1])')
            assert 'sms_open' not in before,'Preparing text must not count as opening SMS'
            for selector in ['#sms-link','a[href^="tel:"]']:
                page.locator(selector).first.evaluate('(e)=>{e.addEventListener("click",ev=>ev.preventDefault(),{once:true});e.click()}')
            events=page.evaluate('window.__qaEvents.filter(e=>e[0]==="event")')
            names=[e[1] for e in events]
            assert {'service_select','sms_open','call_click'}<=set(names)
            assert 'generate_lead' not in names
            assert 'PRIVATE_' not in json.dumps(events),'Typed form data leaked into analytics'
            page.locator('#details').fill('Changed request')
            assert page.locator('#draft').is_hidden()
            page.locator('#location').fill('   ');page.locator('#prepare-text').click()
            assert page.locator('#draft').is_hidden()
            assert page.locator('#location').evaluate('(e)=>!e.validity.valid')
            page.reload(wait_until='networkidle');page.add_script_tag(content=AXE)
            violations=[]
            for state in ('collapsed','expanded'):
                if state=='expanded':page.locator('[data-service-card]').evaluate_all('(es)=>es.forEach(e=>e.open=true)')
                r=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})")
                violations.extend({'state':state,'id':v['id'],'targets':[n['target'] for n in v['nodes']]} for v in r['violations'])
            assert not errors,errors
            result['viewports'].append({'width':width,'overflow':False,'js_errors':errors,'axe_violations':violations,'events':names})
            persist();assert not violations,violations
            ctx.close()
        ctx=b.new_context(**p.devices['iPhone 13'],reduced_motion='reduce')
        ctx.route('**/*',guard);page=ctx.new_page();page.goto(BASE+'/',wait_until='networkidle')
        assert page.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto'
        page.locator('#service').select_option(label='Starlink systems');page.locator('#location').fill('Islamorada');page.locator('#details').fill('Starlink install');page.locator('#prepare-text').click()
        assert (page.locator('#sms-link').get_attribute('href') or '').startswith('sms:+13053066391&body=')
        ctx.close()
        ctx=b.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        ctx.route('**/*',guard);page=ctx.new_page();page.goto(BASE+'/',wait_until='networkidle')
        assert page.locator('#prepare-text').is_disabled()
        assert page.locator('noscript a').is_visible()
        page.locator('[data-service-card="radio"] summary').click()
        assert page.locator('[data-service-card="radio"] .service-detail').is_visible()
        ctx.close()
        ctx=b.new_context();ctx.route('**/*',guard);page=ctx.new_page();page.goto(BASE+'/',wait_until='networkidle')
        urls=set(page.locator('a').evaluate_all('(es)=>es.map(e=>e.getAttribute("href")).filter(v=>v&&!v.startsWith("#")&&!v.startsWith("sms:")&&!v.startsWith("tel:"))'))
        urls.update(['robots.txt','sitemap.xml','assets/brand/favicon.png','assets/brand/zenith-full.webp','harbor.css?v=20260905','harbor.js?v=20260905','assets/images/harbor-social.webp'])
        for u in sorted(urls):
            response=page.request.get(urljoin(BASE+'/',u));assert response.ok,(u,response.status)
        result['checked_urls']=sorted(urls)
        ctx.close();b.close()
    result['checks']=['six responsive widths','three service selectors and keyboard disclosures','legacy anchors and all public assets','attribution retained in SMS and service-page links','GA4 event hooks without request PII or false leads','iPhone SMS syntax','reduced motion','no-JS fallback']
    assert not external,external
    result['ok']=True;persist();print(json.dumps(result,indent=2))
finally:
    if server:server.shutdown()
