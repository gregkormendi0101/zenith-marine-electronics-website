# Zenith Marine Electronics — V2

A brand-new, mobile-first landing page for Zenith Marine Electronics in the Upper Florida Keys.

## Preview

```bash
python3 -m http.server 4173 --bind 100.122.63.73
```

Open `http://100.122.63.73:4173/` over Greg's Tailscale network.

## Direction

- Premium dark marine editorial design
- Real Zenith logo assets
- Recraft-generated, visually reviewed boat and helm photography
- Short, lead-first copy
- One official NMEA logo
- Advanced credentials only
- Mobile-safe call and SMS actions
- No frameworks or external runtime dependencies

## Validation

```bash
python3 validate_site.py
python3 qa_responsive.py
```

The responsive QA uses Playwright with the installed Google Chrome and checks widths from 320px through 1440px, image loading, touch targets, anchor offsets, phone links, analytics events, JavaScript errors and horizontal overflow.

## Assets

Optimized WebP production images live under `assets/images/`. Original high-resolution Recraft PNGs are archived beside this directory in `../zenith-v2-image-sources/`. Rendered QA screenshots are archived in `../zenith-v2-qa/`.
