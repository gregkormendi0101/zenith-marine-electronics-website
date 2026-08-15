# Zenith Marine Electronics — production site

A static four-page website for Zenith Marine Electronics in the Upper Florida Keys.

## Site structure

- `index.html` — blueprint-style service overview
- `nmea-networks.html` — NMEA diagnostics, integration and commissioning
- `marine-electronics.html` — marine electronics planning, installation and commissioning
- `marine-radio-fcc.html` — VHF/DSC/AIS service and FCC ship-radio inspections

The home page gives equal visual priority to the three specialties. Each has a dedicated technical page and a hand-authored SVG blueprint:

- `assets/diagrams/nmea-backbone.svg`
- `assets/diagrams/helm-panel.svg`
- `assets/diagrams/vhf-radio.svg`

No stock or generated boat photography is used. The canonical Zenith logo and one official NMEA logo remain the only brand/credential imagery.

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

- `validate_site.py` checks all four pages, local references, canonical URLs, JSON-LD, sitemap entries, privacy constraints and technical SVG labels.
- `qa_responsive.py` exercises every page at 320, 375, 390, 430, 768, 1024 and 1440 px; it checks overflow, navigation, diagrams, phone links, UTM retention, analytics and reduced-motion behavior.
- `qa_capture.py` writes desktop/mobile visual evidence to `qa/blueprint/`.

## Deployment

The repository deploys from `main` to GitHub Pages at `https://zenithmarineelectronics.com/`. `CNAME`, canonical metadata, sitemap, robots and social metadata are production-ready.
