# Zenith Marine Electronics — production site

Static one-page Service First website for Zenith Marine Electronics in the Upper Florida Keys.

## Offer

- NMEA 2000 network diagnostics, additions, integration, and commissioning
- Marine Starlink surveys, installation, onboard networking, and verification
- VHF/DSC/AIS service and non-GMDSS ship-radio inspection inquiries

## Architecture

- `index.html` — factual offer, three service lanes, qualifications, and booking intake
- `*-upper-florida-keys.html` — three high-intent service landing pages with preselected inquiry paths
- `styles.css` — responsive visual system and reduced-motion behavior
- `service-pages.css` — shared landing-page layout and responsive treatment
- `app.js` — reversible blueprint-to-vessel scroll morph, prepared-SMS booking, privacy-safe UTM/referrer attribution, and GA4 interaction events
- `build_service_pages.py` — deterministic source for regenerating all three landing pages
- `privacy.html` — plain-language analytics, attribution, and SMS disclosure
- `assets/hero-blueprint*.svg` — pure-vector, text-free vessel drawings
- `assets/hero-yacht*.webp` — aligned desktop/mobile vessel images
- `assets/images/social.webp` — 1200×630 social preview

## Preview

```bash
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/`.

## Validation

```bash
uv run --with beautifulsoup4 python validate_site.py
uv run --with playwright --with axe-playwright-python python qa_responsive.py
uv run --with playwright --with axe-playwright-python python qa_service_pages.py
```

`validate_site.py` checks metadata, structured data, domain files, references, public wording, privacy limits, GA4 instrumentation, service architecture, blueprint purity, and the production asset budget. `qa_responsive.py` tests the home page. `qa_service_pages.py` tests every landing page at mobile and desktop widths, including accessibility, attribution, preselected booking, SMS construction, call-event instrumentation, broken images, console errors, and overflow.

Run the service-page suite against production after deployment:

```bash
ZENITH_QA_URL=https://zenithmarineelectronics.com uv run --with playwright --with axe-playwright-python python qa_service_pages.py
```

Campaign links may use `utm_source`, `utm_medium`, `utm_campaign`, and `ref`/`utm_content` for a specific partner or placement. The booking text carries only normalized attribution tokens (or the external referrer hostname), never a full browsing URL.

GA4 measurement ID `G-H8KGT9K2TM` records `service_select`, `sms_open`, and `call_click`. A click is not treated as a confirmed lead; `generate_lead` is intentionally reserved for a real inquiry logged after receipt.

## Deployment

GitHub Pages deploys `main` to `https://zenithmarineelectronics.com/`. Squarespace manages DNS. `CNAME`, canonical metadata, sitemap, robots, and HTTPS are production requirements.
