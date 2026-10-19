# Zenith Marine Electronics — production site

Approved **Harbor** homepage with three retained high-intent service landing pages. Static GitHub Pages site at https://zenithmarineelectronics.com/.


> **2026-10-19:** Homepage replaced with the approved one-page design (transparent launch pricing, FCC Form 824 lane, white header/footer with the original logo). The Harbor homepage remains in git history for rollback. Service landing pages and privacy page retained; their request sections were relabelled from 'Demand test' to 'Request service'.

## Runtime
- `index.html`, `harbor.css`, `harbor.js`: concise homepage, three expandable service lanes, qualifications, operator/process information and a locally prepared SMS request.
- `*-upper-florida-keys.html`: existing NMEA troubleshooting, Starlink installation and VHF/DSC/AIS landing pages. Preserve these URLs for organic search and existing campaign links.
- `styles.css`, `service-pages.css`, `app.js`: retained landing-page/privacy dependencies. Old hero assets remain available for compatibility; the new homepage does not load them or the old morph runtime.
- `build_service_pages.py`: deterministic source for the service pages.
- `privacy.html`: analytics, bounded attribution and text-message disclosure.
- `assets/images/harbor-social.webp`: verified 1200×630 social card for the new design.
- Canonical logo/favicon, `CNAME`, `.nojekyll`, robots/sitemap and IndexNow ownership file retained.

## Contact and measurement
The homepage drafts an SMS locally, then provides an explicit Open in Messages action. No request is sent automatically and no appointment is confirmed. The builder is disabled without JavaScript; direct SMS and telephone fallbacks remain. Changed inputs invalidate the draft; required fields reject whitespace-only values.

The existing GA4 stream records `service_select`, `sms_open` and `call_click`. Preparing a draft is **not** an SMS-open event or a confirmed lead. Typed location, vessel and request details are never supplied to custom analytics events. `generate_lead` is reserved for a real received inquiry.

Campaign attribution uses bounded normalized `utm_source`, `utm_medium`, `utm_campaign`, `ref`/`utm_content` tokens. It is preserved in prepared SMS and homepage-to-service-page navigation; arbitrary URL parameters and full browsing URLs are not propagated into those links/messages.

Legacy homepage anchors (`#book`, `#qualifications`, `#service-area` and the three service IDs) are retained.

## Validation
```bash
uv run --with beautifulsoup4 --with playwright==1.62.0 --with axe-playwright-python python validate_site.py
uv run --with beautifulsoup4 --with playwright==1.62.0 --with axe-playwright-python python qa_responsive.py
uv run --with beautifulsoup4 --with playwright==1.62.0 --with axe-playwright-python python qa_service_pages.py
```
The same browser checks run on production with `ZENITH_QA_URL=https://zenithmarineelectronics.com`. QA intercepts analytics transport and prevents actual calls/texts; it checks event hooks, not GA dashboard ingestion. Generated evidence is ignored under `.qa-artifacts/`.

The homepage suite checks six widths, twelve collapsed/expanded accessibility states, all service selectors, keyboard flow, metadata/anchors/assets, SMS draft/encoding/attribution, no-JS behavior, iPhone SMS URI syntax and reduced motion. Service-page QA checks three retained pages at desktop/mobile sizes.

## Deployment and rollback
GitHub Pages publishes `main` from the repository root. Squarespace manages DNS; no DNS changes are required for a redesign. Push normally, wait for successful Pages deployment and verify the served homepage plus every retained landing page. Keep QA captures and project/private evidence out of the commit.

Rollback: revert the Harbor release commit with a new Git commit and push normally. Never force-push deployment history.

After a meaningful verified release, `python submit_indexnow.py --dry-run` validates current URLs; `python submit_indexnow.py` notifies IndexNow. Do not repeatedly resubmit unchanged content.
