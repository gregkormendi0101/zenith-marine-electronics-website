# Zenith Marine Electronics — production site

A static, mobile-first lead-generation site for Zenith Marine Electronics in the Upper Florida Keys.

## Preview

```bash
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/`.

## V3 direction

- The three offers are explicit in the first screen: NMEA networks, marine electronics installation, and marine radio service with FCC ship-radio inspections.
- All vessel/helm photography is real stock photography under the Unsplash License; sources are documented in `ASSET_SOURCES.md`.
- The former generated speeding-boat and dock images were removed.
- Three hand-authored SVG system diagrams show plausible NMEA 2000, installation, and VHF/DSC signal paths.
- Diagram route markers and the page signal line move with scroll direction—down or up—without an animation library.
- The canonical Zenith logo and one official NMEA logo are used.
- Public credentials are limited to AMEI, Advanced NMEA 2000, FCC GROL, and USCG 100-Ton Master.
- No framework or external runtime dependency is required.

## Validation

```bash
python3 validate_site.py
python3 qa_responsive.py
python3 qa_capture.py
```

`qa_responsive.py` checks widths from 320px through 1440px, horizontal overflow, image loading, touch targets, anchor offsets, phone links, scroll-reversible graphics, mobile lead behavior, analytics events and JavaScript errors. `qa_capture.py` renders desktop and iPhone-width evidence under `qa/` for visual review.

## Deployment

The repository deploys to GitHub Pages at `https://zenithmarineelectronics.com/`. `CNAME`, canonical metadata, sitemap, robots and social metadata are production-ready.
