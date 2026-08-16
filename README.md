# Zenith Marine Electronics — production site

Static one-page Service First website for Zenith Marine Electronics in the Upper Florida Keys.

## Offer

- NMEA 2000 network diagnostics, additions, integration, and commissioning
- Marine Starlink surveys, installation, onboard networking, and verification
- VHF/DSC/AIS service and non-GMDSS ship-radio inspection inquiries

## Architecture

- `index.html` — factual offer, three service lanes, qualifications, and booking intake
- `styles.css` — responsive visual system and reduced-motion behavior
- `app.js` — reversible blueprint-to-vessel scroll morph and prepared-SMS booking
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
```

`validate_site.py` checks metadata, structured data, domain files, references, public wording, privacy limits, service architecture, blueprint purity, and the production asset budget. `qa_responsive.py` tests responsive rendering, accessibility, booking behavior, and the reversible hero interaction.

## Deployment

GitHub Pages deploys `main` to `https://zenithmarineelectronics.com/`. Squarespace manages DNS. `CNAME`, canonical metadata, sitemap, robots, and HTTPS are production requirements.
