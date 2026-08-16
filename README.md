# Zenith Marine Electronics — production site

Static four-page website for Zenith Marine Electronics in the Upper Florida Keys.

## Architecture

- `index.html` — the three specialties presented as an interactive systems console
- `nmea-networks.html` — NMEA diagnostics, integration and commissioning
- `marine-electronics.html` — marine electronics planning, installation and commissioning
- `marine-radio-fcc.html` — VHF/DSC/AIS service and FCC ship-radio inspections

## Preview

```bash
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/`.

## Validation

```bash
python3 validate_site.py
python3 qa_responsive.py
python3 qa_capture.py
```

- `validate_site.py` checks the four pages, metadata, local references, service architecture, public wording, privacy constraints and production asset sizes.
- `qa_responsive.py` exercises all pages at 320, 375, 390, 430, 768, 1024 and 1440 px, including overflow, image loading, tab behavior, UTM retention, lead tracking and reduced motion.

## Deployment

GitHub Pages deploys `main` to `https://zenithmarineelectronics.com/`. `CNAME`, canonical metadata, sitemap, robots and social metadata are production assets.
