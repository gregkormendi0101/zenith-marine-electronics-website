#!/usr/bin/env python3
"""Generate Zenith's static high-intent service landing pages.

DESIGN ROUTE (Oct 2026 relaunch alignment): these pages are SELF-CONTAINED,
mirroring index.html's current design system — inline <style> with the same
CSS custom properties (teal #17a2b0 / navy #0a2233 palette, Barlow Condensed
headings, IBM Plex Mono kickers/prices), the same white sticky header and
white footer, .price-line pricing blocks, and the same gtag setup (GA4 plus
the Google Ads config AW-18533576927). They no longer link styles.css or
service-pages.css (those files remain in the repo for the retired Harbor
design only). The request form keeps its app.js hooks
(form[data-booking-form], #service preselection, [data-form-status]); on
submit, app.js fires GA4 'sms_open' and the inline script in each page
fires the Google Ads conversion, matching index.html's smsBtn wiring.
Regenerate with: python3 build_service_pages.py
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://zenithmarineelectronics.com/"
PHONE_DISPLAY = "305-306-6391"
PHONE_URI = "+13053066391"
GA4 = "G-H8KGT9K2TM"
AW_ID = "AW-18533576927"
AW_SEND_TO = "AW-18533576927/N9TqCLynuakdEN_hv4VF"

PAGES = [
    {
        "slug": "nmea-2000-troubleshooting-upper-florida-keys.html",
        "title": "NMEA 2000 Troubleshooting | Upper Florida Keys",
        "description": "Mobile NMEA 2000 network troubleshooting, device integration, testing, and commissioning in Key Largo, Tavernier, and Islamorada.",
        "eyebrow": "NMEA 2000 · Mobile service",
        "h1": "NMEA 2000 troubleshooting in the Upper Florida Keys",
        "lede": "Intermittent data, missing devices, network alarms, and unreliable integrations traced methodically from power and backbone fundamentals through configuration and commissioning.",
        "service": "NMEA 2000 networks",
        "service_type": "NMEA 2000 network troubleshooting and commissioning",
        "facts": [
            ("Coverage", "Key Largo · Tavernier · Islamorada"),
            ("Scope", "Troubleshooting · additions · commissioning"),
            ("Credential", "Advanced NMEA 2000 Installer"),
        ],
        "pricing": [
            ("Diagnostic visit", "$225"),
            ("Additional labor", "$165/hr"),
            ("NMEA 2000 health report", "$325"),
        ],
        "pricing_note": "Diagnostic visit includes Upper Keys travel and the first 60 minutes on board.",
        "signals_title": "When the network is telling you something is wrong",
        "signals_intro": "NMEA faults are rarely fixed by swapping random displays. Start with the physical network and prove each layer.",
        "signals": [
            "Displays or sensors disappear and return intermittently",
            "One device shows data while another reports blanks or alarms",
            "New equipment will not appear, share data, or configure correctly",
            "The network behaves differently after charging, engine start, or equipment changes",
            "Backbone, drop, power, or termination history is unknown",
        ],
        "process": [
            ("01 · Establish", "Document the symptom, equipment list, recent changes, and the exact conditions that trigger the fault."),
            ("02 · Test", "Check network power, voltage behavior, backbone layout, drops, termination, connectors, and device presence."),
            ("03 · Verify", "Correct the scoped fault, configure affected equipment, and confirm stable network behavior before closeout."),
        ],
        "scope_title": "Useful information before the visit",
        "scope": [
            "Boat location, make, model, and length",
            "Display, sensor, gateway, and network-device makes and models",
            "Exact alarms, missing data, or intermittent symptoms",
            "What changed before the problem began",
            "Clear photos of the backbone, power tee, terminators, and affected devices",
        ],
        "note": "Zenith scopes diagnosis before parts replacement. If the evidence points outside the NMEA network—power distribution, transducer hardware, software support, or another trade—you get that boundary clearly.",
        "faqs": [
            ("Can you add a device to an existing NMEA 2000 network?", "Yes, after confirming the existing backbone, power, loading, connection points, and compatibility support the addition."),
            ("Do you troubleshoot mixed-brand networks?", "Yes. Mixed-brand systems are common. Device compatibility, PGN support, firmware, configuration, and physical-network health are evaluated together."),
            ("What should I send first?", "Send the boat location, vessel details, equipment models, symptoms, recent changes, and clear photos. That is enough to determine the next useful step."),
        ],
    },
    {
        "slug": "marine-starlink-installation-upper-florida-keys.html",
        "title": "Marine Starlink Installation | Upper Florida Keys",
        "description": "Marine Starlink installation surveys, mounting and cable-route planning, power integration, and onboard Wi-Fi setup in the Upper Florida Keys.",
        "eyebrow": "Marine Starlink · Mobile service",
        "h1": "Marine Starlink installation in the Upper Florida Keys",
        "lede": "A clean Starlink install starts before drilling: antenna location, obstruction exposure, cable routing, power, weather sealing, network architecture, and onboard Wi-Fi all need one coherent plan.",
        "service": "Starlink systems",
        "service_type": "Marine Starlink installation and onboard network setup",
        "facts": [
            ("Coverage", "Key Largo · Tavernier · Islamorada"),
            ("Scope", "Survey · installation · onboard Wi-Fi"),
            ("Approach", "Route and power plan before drilling"),
        ],
        "pricing": [
            ("On-board survey", "$175"),
            ("Installation labor", "from $1,250"),
        ],
        "pricing_note": "Survey fee is credited in full toward your installation.",
        "signals_title": "What separates a marine install from a temporary setup",
        "signals_intro": "The antenna is only one component. Reliability depends on the whole path from sky view to the devices using the connection.",
        "signals": [
            "Mounting location needs a practical obstruction and serviceability review",
            "Cable route must avoid damage, water intrusion, pinch points, and ugly shortcuts",
            "Power source and protection need to match the equipment and vessel",
            "Router placement and onboard coverage need to fit the actual use case",
            "Existing network equipment may need integration rather than duplication",
        ],
        "process": [
            ("01 · Survey", "Review the vessel, proposed antenna position, obstruction risks, cable path, power source, and network requirements."),
            ("02 · Install", "Mount and route the system cleanly, protect penetrations, connect power correctly, and configure the onboard network."),
            ("03 · Prove", "Confirm connection, router operation, Wi-Fi coverage, device access, and a maintainable final installation."),
        ],
        "scope_title": "Useful information before the survey",
        "scope": [
            "Boat location, make, model, length, and primary use",
            "Starlink hardware version or kit photos",
            "Possible antenna locations and access below them",
            "Existing router, network, inverter, or DC-power equipment",
            "Where reliable Wi-Fi is needed aboard",
        ],
        "note": "Zenith does not sell fantasy coverage. Satellite visibility, marina structures, vessel geometry, plan terms, and offshore expectations are discussed before the installation is scoped.",
        "faqs": [
            ("Can Starlink be integrated with an existing onboard network?", "Often, yes. The right design depends on the current router, switches, access points, power architecture, and the desired failover or network behavior."),
            ("Do you survey before drilling?", "Yes. Mounting, cable access, weather sealing, serviceability, and power are evaluated before permanent work is proposed."),
            ("Can you improve Wi-Fi coverage aboard?", "Yes. Router placement and existing or proposed access points can be evaluated as part of the onboard-network scope."),
        ],
    },
    {
        "slug": "vhf-dsc-ais-service-upper-florida-keys.html",
        "title": "Marine VHF, DSC & AIS Service | Upper Florida Keys",
        "description": "Mobile marine VHF, DSC, and AIS installation and troubleshooting in Key Largo, Tavernier, and Islamorada, including power, coax, antenna, GPS, and configuration checks.",
        "eyebrow": "VHF · DSC · AIS · Mobile service",
        "h1": "Marine VHF, DSC and AIS service in the Upper Florida Keys",
        "lede": "Radio problems are a system problem until proven otherwise. Power, coax, antenna, GPS position, MMSI/DSC configuration, AIS data, and installation quality all matter.",
        "service": "VHF radio service",
        "service_type": "Marine VHF, DSC, and AIS installation and troubleshooting",
        "facts": [
            ("Coverage", "Key Largo · Tavernier · Islamorada"),
            ("Scope", "Installation · troubleshooting · verification"),
            ("Credential", "FCC General Radiotelephone Operator License"),
        ],
        "pricing": [
            ("Diagnostic visit", "$225"),
            ("FCC Form 824 inspection, single vessel", "$595"),
            ("Fleets of 3+ vessels", "$495 each"),
        ],
        "pricing_note": "Diagnostic visit includes Upper Keys travel and the first 60 minutes on board. Fleet rate applies when three or more vessels are inspected.",
        "signals_title": "Symptoms worth testing instead of guessing",
        "signals_intro": "A radio that powers on is not necessarily transmitting, receiving, identifying, or sharing position correctly.",
        "signals": [
            "Short or inconsistent transmit and receive range",
            "DSC position or identity data is missing or incorrect",
            "AIS targets disappear, own-vessel data is wrong, or alarms persist",
            "Noise, weak audio, voltage drop, or intermittent resets occur",
            "Coax, antenna, GPS, or network connections have unknown condition",
        ],
        "process": [
            ("01 · Identify", "Capture the exact symptom, installation history, equipment models, configuration, and recent changes."),
            ("02 · Test", "Check power and voltage behavior, coax and connectors, antenna path, GPS/DSC data, AIS integration, and configuration."),
            ("03 · Verify", "Correct the scoped issue and confirm the system's operating behavior and data path before closeout."),
        ],
        "scope_title": "Useful information before the visit",
        "scope": [
            "Boat location, make, model, length, and operating area",
            "VHF, AIS, antenna, splitter, GPS, and display makes and models",
            "Exact symptoms, alarms, range concerns, or failed functions",
            "Recent electrical, antenna, software, or network changes",
            "Clear photos of radio, antenna base, coax connections, and related displays",
        ],
        "note": "Non-GMDSS compulsory ship-radio inspection inquiries are screened separately for vessel applicability, equipment scope, calibrated-test requirements, and independence before scheduling. No statutory sign-off is implied by a general service request.",
        "faqs": [
            ("Can you troubleshoot poor VHF range?", "Yes. Power, voltage drop, coax, connectors, antenna path, installation condition, and radio behavior are checked as a system."),
            ("Can you configure DSC and AIS data sharing?", "Yes, when the connected equipment supports the required GPS, identity, network, and configuration functions."),
            ("Do you perform FCC ship-radio inspections?", "Potential non-GMDSS inspection work is screened before scheduling for vessel applicability, scope, calibrated equipment, and independence requirements."),
        ],
    },
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def options(selected: str) -> str:
    values = [
        "NMEA 2000 networks",
        "Starlink systems",
        "VHF radio service",
        "FCC ship-radio inspection",
    ]
    return "\n".join(
        f'              <option value="{esc(value)}"{" selected" if value == selected else ""}>{esc(value)}</option>'
        for value in values
    )


def schema(page: dict) -> str:
    canonical = BASE + page["slug"]
    faq_entities = [
        {
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {"@type": "Answer", "text": answer},
        }
        for question, answer in page["faqs"]
    ]
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Service",
                "name": page["service_type"],
                "url": canonical,
                "description": page["description"],
                "provider": {
                    "@type": "ProfessionalService",
                    "name": "Zenith Marine Electronics",
                    "url": BASE,
                    "telephone": "+1-305-306-6391",
                },
                "areaServed": [
                    {"@type": "City", "name": "Key Largo, Florida"},
                    {"@type": "City", "name": "Tavernier, Florida"},
                    {"@type": "City", "name": "Islamorada, Florida"},
                ],
            },
            {"@type": "FAQPage", "mainEntity": faq_entities},
        ],
    }
    return json.dumps(data, indent=2)


def related_links(current_slug: str) -> str:
    return "\n".join(
        f'''          <a class="related-card" href="{esc(other["slug"])}">
            <span class="related-name">{esc(other["service_type"])}</span>
            <span class="svc-link">Full service details <span aria-hidden="true">→</span></span>
          </a>'''
        for other in PAGES
        if other["slug"] != current_slug
    )


PAGE_CSS = """
      :root {
        color-scheme: light;
        --bg: #eef4f6;
        --bg-deep: #e2ecef;
        --surface: #ffffff;
        --surface-2: #f4f8f9;
        --ink: #0a2233;
        --ink-soft: #33505f;
        --ink-faint: #5d7a89;
        --line: #cfdee3;
        --navy: #071a2b;
        --navy-2: #0a2438;
        --teal: #0e7c86;
        --teal-bright: #17a2b0;
        --cyan: #1593c4;
        --accent-ink: #0b6d77;
        --on-navy: #eaf4f7;
        --on-navy-soft: #a9c6d2;
        --price: #0b6d77;
        --shadow: 0 10px 30px rgba(7, 26, 43, 0.10);
        --radius: 14px;
      }
      @media (prefers-color-scheme: dark) {
        :root {
          color-scheme: dark;
          --bg: #06141f;
          --bg-deep: #04101a;
          --surface: #0a2133;
          --surface-2: #0d283d;
          --ink: #e9f3f6;
          --ink-soft: #b3cdd8;
          --ink-faint: #7e9dab;
          --line: #1d3d53;
          --navy: #04101a;
          --navy-2: #071a2b;
          --teal: #2dd4bf;
          --teal-bright: #3ec6d8;
          --cyan: #4cc3e8;
          --accent-ink: #5eead4;
          --on-navy: #eaf4f7;
          --on-navy-soft: #a9c6d2;
          --price: #5eead4;
          --shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        }
      }

      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        font-family: "Barlow", system-ui, -apple-system, "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--ink);
        line-height: 1.55;
        font-size: 17px;
        -webkit-font-smoothing: antialiased;
      }
      img { max-width: 100%; display: block; }
      a { color: var(--accent-ink); }
      h1, h2, h3 {
        font-family: "Barlow Condensed", "Barlow", sans-serif;
        font-weight: 600;
        line-height: 1.08;
        margin: 0;
        letter-spacing: 0.01em;
      }
      .wrap { max-width: 1160px; margin: 0 auto; padding: 0 22px; }
      section { padding: 84px 0; }
      .section-head { max-width: 720px; margin-bottom: 42px; }
      .section-head h2 { font-size: clamp(32px, 4.4vw, 46px); margin-bottom: 12px; }
      .section-head p { color: var(--ink-soft); margin: 0; font-size: 18px; }
      .kicker {
        font-family: "IBM Plex Mono", ui-monospace, monospace;
        font-size: 12.5px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--accent-ink);
        margin: 0 0 14px;
      }
      .skip-link {
        position: absolute; left: 16px; top: -60px; z-index: 100;
        background: var(--surface); color: var(--accent-ink);
        padding: 10px 16px; border-radius: 8px; font-weight: 600;
        transition: top 0.15s ease;
      }
      .skip-link:focus { top: 12px; }

      /* ---------- Header (matches index.html) ---------- */
      header {
        position: sticky; top: 0; z-index: 50;
        background: #ffffff;
        border-bottom: 1px solid var(--line);
        box-shadow: 0 1px 12px rgba(7, 26, 43, 0.06);
      }
      .header-in {
        display: flex; align-items: center; gap: 18px;
        padding-top: 12px; padding-bottom: 12px;
      }
      .brand { display: flex; align-items: center; gap: 12px; text-decoration: none; margin-right: auto; }
      .brand-logo {
        height: 58px; width: auto; flex: none;
        background: transparent; border-radius: 0; padding: 0;
      }
      .foot-logo {
        height: 46px; width: auto;
        background: transparent; border-radius: 0; padding: 0;
      }
      nav.main { display: flex; align-items: center; gap: 26px; }
      nav.main a {
        color: #0a2233; text-decoration: none;
        font-weight: 500; font-size: 15.5px;
      }
      nav.main a:hover { color: var(--accent-ink); }
      nav.main a.btn-primary { color: #ffffff; }
      nav.main a.btn-primary:hover { color: #ffffff; }
      @media (prefers-color-scheme: dark) {
        nav.main a.btn-primary, nav.main a.btn-primary:hover { color: #04202b; }
      }
      .btn {
        display: inline-flex; align-items: center; gap: 9px;
        font-weight: 600; font-size: 16px; text-decoration: none;
        border-radius: 10px; padding: 12px 22px;
        border: 1px solid transparent; cursor: pointer;
        transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
      }
      .btn-primary { background: var(--teal); color: #ffffff; }
      .btn-primary:hover { background: var(--teal-bright); color: #ffffff; }
      @media (prefers-color-scheme: dark) {
        .btn-primary { color: #04202b; }
        .btn-primary:hover { color: #04202b; }
      }
      .btn-ghost { border-color: rgba(160, 210, 222, 0.45); color: var(--on-navy); background: transparent; }
      .btn-ghost:hover { border-color: var(--teal-bright); color: var(--teal-bright); }
      .btn-head { padding: 9px 18px; font-size: 15px; }
      .head-phone {
        font-family: "IBM Plex Mono", monospace; font-size: 15px;
        color: #0a2233; text-decoration: none; white-space: nowrap;
      }
      .head-phone:hover { color: var(--accent-ink); }
      @media (max-width: 900px) {
        nav.main a.nav-link { display: none; }
      }
      @media (max-width: 560px) {
        .head-phone { display: none; }
        .brand-logo { height: 48px; padding: 0; }
        .foot-logo { height: 40px; }
      }

      /* ---------- Hero (navy band, matches index.html hero/area tones) ---------- */
      .hero {
        position: relative; color: var(--on-navy);
        background: var(--navy-2);
        overflow: hidden;
      }
      .hero-shade {
        position: absolute; inset: 0;
        background: linear-gradient(100deg, rgba(4, 18, 30, 0.94) 22%, rgba(4, 18, 30, 0.78) 52%, rgba(4, 18, 30, 0.42) 100%);
      }
      .hero-in { position: relative; padding: 84px 0 72px; max-width: 820px; }
      .hero .kicker { color: #7fe3d0; }
      .hero h1 { font-size: clamp(40px, 5.8vw, 62px); font-weight: 700; margin-bottom: 20px; }
      .hero-lede { font-size: clamp(18px, 2.2vw, 21px); color: #d3e6ec; margin: 0 0 34px; max-width: 680px; }
      .hero-ctas { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 44px; }
      .hero-ctas .btn { font-size: 17px; padding: 14px 26px; }
      .crumbs {
        position: relative; display: flex; flex-wrap: wrap; gap: 8px;
        font-family: "IBM Plex Mono", monospace; font-size: 12.5px;
        letter-spacing: 0.08em; text-transform: uppercase;
        color: var(--on-navy-soft); margin-bottom: 26px;
      }
      .crumbs a { color: var(--on-navy-soft); text-decoration: none; }
      .crumbs a:hover { color: #7fe3d0; }
      .fact-row {
        position: relative; display: flex; flex-wrap: wrap; gap: 18px 48px;
        border-top: 1px solid rgba(150, 205, 220, 0.28);
        padding-top: 24px; margin: 0;
      }
      .fact dt {
        font-family: "IBM Plex Mono", monospace; font-size: 11.5px;
        letter-spacing: 0.16em; text-transform: uppercase;
        color: #7fe3d0; margin-bottom: 5px;
      }
      .fact dd { margin: 0; font-weight: 600; font-size: 16.5px; color: var(--on-navy); }
      @media (max-width: 640px) {
        .hero-in { padding: 60px 0 56px; }
        .hero-shade { background: linear-gradient(180deg, rgba(4, 18, 30, 0.88), rgba(4, 18, 30, 0.82)); }
      }

      /* ---------- Cards, check lists, pricing (index.html components) ---------- */
      .band { background: var(--bg-deep); }
      .panel {
        background: var(--surface); border: 1px solid var(--line);
        border-radius: var(--radius); padding: 30px;
        box-shadow: var(--shadow);
      }
      .check-list { margin: 0; padding: 0; list-style: none; }
      .check-list li {
        position: relative; padding-left: 24px; margin-bottom: 10px;
        color: var(--ink-soft); font-size: 16.5px;
      }
      .check-list li:last-child { margin-bottom: 0; }
      .check-list li::before {
        content: ""; position: absolute; left: 2px; top: 9px;
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--teal);
      }
      .price-box { border-top: 1px solid var(--line); padding-top: 16px; }
      .price-panel .price-box { border-top: none; padding-top: 0; }
      .price-line { display: flex; justify-content: space-between; align-items: baseline; gap: 14px; padding: 3px 0; }
      .price-line .what { color: var(--ink-soft); font-size: 15.5px; }
      .price-line .amt {
        font-family: "IBM Plex Mono", monospace; font-weight: 500;
        color: var(--price); white-space: nowrap; font-size: 16.5px;
      }
      .price-note { font-size: 14px; color: var(--ink-faint); margin: 8px 0 0; }
      .note-box {
        border: 1px solid var(--line); border-radius: var(--radius);
        background: var(--surface); padding: 24px 26px;
        color: var(--ink-soft); font-size: 16px;
      }
      .note-box strong { color: var(--ink); }
      .note-box p { margin: 0; }

      /* ---------- Process steps (index.html) ---------- */
      .steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }
      @media (max-width: 820px) { .steps { grid-template-columns: 1fr; } }
      .step {
        border: 1px solid var(--line); border-radius: var(--radius);
        background: var(--surface); padding: 28px; box-shadow: var(--shadow);
      }
      .step-num {
        font-family: "IBM Plex Mono", monospace; font-size: 14px;
        color: var(--accent-ink); border: 1px solid var(--line);
        background: var(--surface-2); border-radius: 999px;
        width: 42px; height: 42px; display: flex; align-items: center; justify-content: center;
        margin-bottom: 16px;
      }
      .step h3 { font-size: 24px; margin-bottom: 8px; }
      .step p { margin: 0; color: var(--ink-soft); font-size: 16px; }

      /* ---------- FAQ + related cards (index.html .svc) ---------- */
      .svc-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 22px; }
      @media (max-width: 820px) { .svc-grid { grid-template-columns: 1fr; } }
      .svc {
        background: var(--surface); border: 1px solid var(--line);
        border-radius: var(--radius); padding: 30px 30px 26px;
        box-shadow: var(--shadow);
      }
      .svc h3 { font-size: 24px; margin-bottom: 10px; }
      .svc p { color: var(--ink-soft); margin: 0; font-size: 16.5px; }
      .svc-link { display: inline-block; margin-top: 14px; font-weight: 600; font-size: 15px; color: #0e7c8c; text-decoration: none; }
      .svc-link:hover { text-decoration: underline; }
      .related-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
      @media (max-width: 820px) { .related-grid { grid-template-columns: 1fr; } }
      .related-card {
        display: block; background: var(--surface); border: 1px solid var(--line);
        border-radius: var(--radius); padding: 26px 30px;
        box-shadow: var(--shadow); text-decoration: none;
      }
      .related-card .related-name {
        font-family: "Barlow Condensed", "Barlow", sans-serif; font-weight: 600;
        font-size: 25px; line-height: 1.12; color: var(--ink); display: block;
      }
      .related-card .svc-link { margin-top: 10px; }
      .related-card:hover .related-name { color: var(--accent-ink); }

      /* ---------- Request (index.html form system) ---------- */
      .req-grid { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 48px; align-items: start; }
      @media (max-width: 900px) { .req-grid { grid-template-columns: 1fr; gap: 36px; } }
      .req-copy h2 { font-size: clamp(32px, 4.4vw, 46px); margin-bottom: 12px; }
      .req-copy .intro { color: var(--ink-soft); font-size: 18px; margin: 0 0 26px; }
      .req-copy h3 { font-size: 22px; margin-bottom: 14px; }
      .intake-list { list-style: none; margin: 0 0 28px; padding: 0; display: grid; gap: 12px; }
      .intake-list li { display: flex; gap: 12px; align-items: center; color: var(--ink-soft); font-size: 16.5px; }
      .intake-list .n {
        font-family: "IBM Plex Mono", monospace; font-size: 13px;
        color: var(--accent-ink); border: 1px solid var(--line);
        background: var(--surface-2); border-radius: 999px;
        width: 30px; height: 30px; flex: none;
        display: flex; align-items: center; justify-content: center;
      }
      .direct-contact {
        border: 1px solid var(--line); border-radius: var(--radius);
        background: var(--surface); padding: 20px 24px;
      }
      .direct-contact .dc-label {
        display: block; font-family: "IBM Plex Mono", monospace;
        font-size: 11.5px; letter-spacing: 0.16em; text-transform: uppercase;
        color: var(--accent-ink); margin-bottom: 6px;
      }
      .direct-contact .dc-phone {
        font-family: "Barlow Condensed", sans-serif; font-size: 30px; font-weight: 700;
        color: var(--ink); text-decoration: none; line-height: 1;
      }
      .direct-contact .dc-phone:hover { color: var(--accent-ink); }
      .form-card {
        background: var(--surface); border: 1px solid var(--line);
        border-radius: var(--radius); padding: 30px; box-shadow: var(--shadow);
      }
      .form-heading h3 { font-size: 26px; margin-bottom: 6px; }
      .form-heading p { color: var(--ink-soft); font-size: 15.5px; margin: 0 0 22px; }
      form.req { display: grid; gap: 16px; }
      .field label { display: block; font-weight: 600; font-size: 15px; margin-bottom: 6px; }
      .field label .opt { font-weight: 400; color: var(--ink-faint); }
      .field input, .field select, .field textarea {
        width: 100%; font: inherit; font-size: 16px; color: var(--ink);
        background: var(--surface); border: 1px solid var(--line);
        border-radius: 10px; padding: 12px 14px;
      }
      .field textarea { min-height: 108px; resize: vertical; }
      .field input:focus, .field select:focus, .field textarea:focus {
        outline: 2px solid var(--teal-bright); outline-offset: 1px; border-color: transparent;
      }
      .form-submit { justify-content: center; width: 100%; }
      .form-status { margin: 0; min-height: 1.4em; font-size: 15px; color: var(--accent-ink); }
      .form-noscript { margin: 0; font-size: 15px; color: var(--ink-soft); }

      /* ---------- Footer (matches index.html) ---------- */
      footer {
        background: #ffffff; color: #33505f;
        padding: 44px 0 36px; border-top: 1px solid #cfdee3;
        box-shadow: 0 -1px 12px rgba(7, 26, 43, 0.06);
      }
      .foot-in { display: flex; flex-wrap: wrap; gap: 18px 40px; align-items: flex-start; justify-content: space-between; }
      .foot-brand { display: flex; align-items: center; gap: 12px; }
      .foot-links { display: flex; flex-wrap: wrap; gap: 8px 26px; font-size: 15.5px; }
      .foot-links a { color: #0a2233; text-decoration: none; font-weight: 500; }
      .foot-links a:hover { color: var(--accent-ink); }
      .foot-bottom {
        margin-top: 30px; padding-top: 20px;
        border-top: 1px solid #cfdee3;
        color: #5d7a89;
        font-size: 14px; display: flex; flex-wrap: wrap; gap: 6px 22px; justify-content: space-between;
      }

      section[id], footer[id] { scroll-margin-top: 84px; }
      @media (prefers-reduced-motion: reduce) {
        html { scroll-behavior: auto; }
        * { transition: none !important; }
      }
"""

# Fired on the request form's submit, alongside app.js's GA4 'sms_open',
# mirroring index.html's smsBtn conversion wiring.
CONVERSION_SCRIPT = """
    <script>
      (function () {
        var form = document.querySelector('[data-booking-form]');
        if (!form) { return; }
        form.addEventListener('submit', function () {
          if (!form.checkValidity()) { return; }
          if (typeof window.gtag === 'function') {
            window.gtag('event', 'conversion', {'send_to': 'AW-18533576927/N9TqCLynuakdEN_hv4VF'});
          }
        });
      })();
    </script>
"""


PHONE_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'


def render(page: dict) -> str:
    canonical = BASE + page["slug"]
    facts = "\n".join(
        f'          <div class="fact"><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>'
        for label, value in page["facts"]
    )
    signals = "\n".join(f"              <li>{esc(item)}</li>" for item in page["signals"])
    pricing_lines = "\n".join(
        f'              <div class="price-line"><span class="what">{esc(what)}</span><span class="amt">{esc(amt)}</span></div>'
        for what, amt in page["pricing"]
    )
    steps = []
    for label, text in page["process"]:
        num, _, step_title = label.partition(" · ")
        steps.append(
            f'''          <article class="step">
            <div class="step-num">{esc(num)}</div>
            <h3>{esc(step_title or label)}</h3>
            <p>{esc(text)}</p>
          </article>'''
        )
    process = "\n".join(steps)
    scope_items = "\n".join(f"              <li>{esc(item)}</li>" for item in page["scope"])
    faqs = "\n".join(
        f'''          <article class="svc">
            <h3>{esc(question)}</h3>
            <p>{esc(answer)}</p>
          </article>'''
        for question, answer in page["faqs"]
    )

    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="color-scheme" content="light dark" />
    <meta name="description" content="{esc(page['description'])}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Zenith Marine Electronics" />
    <meta property="og:title" content="{esc(page['title'])}" />
    <meta property="og:description" content="{esc(page['description'])}" />
    <meta property="og:url" content="{esc(canonical)}" />
    <meta property="og:image" content="{BASE}assets/images/harbor-social.webp" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{esc(page['title'])}" />
    <meta name="twitter:description" content="{esc(page['description'])}" />
    <meta name="twitter:image" content="{BASE}assets/images/harbor-social.webp" />
    <link rel="icon" href="assets/brand/favicon.png" type="image/png" />
    <title>{esc(page['title'])} | Zenith Marine Electronics</title>
    <link rel="canonical" href="{esc(canonical)}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
    <style>{PAGE_CSS}    </style>
    <script type="application/ld+json">
{schema(page)}
    </script>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA4}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      window.gtag = window.gtag || function(){{ window.dataLayer.push(arguments); }};
      window.gtag('js', new Date());
      window.gtag('config', '{GA4}');
      window.gtag('config', '{AW_ID}');
    </script>
  <!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '1055938024136920');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=1055938024136920&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->
</head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>

    <!-- ================= Header ================= -->
    <header data-header>
      <div class="wrap header-in">
        <a class="brand" href="index.html" aria-label="Zenith Marine Electronics — home">
          <img class="brand-logo" src="assets/brand/zenith-full.webp" alt="Zenith Marine Electronics" width="1500" height="618" />
        </a>
        <nav class="main" aria-label="Main">
          <a class="nav-link" href="index.html#services">Services</a>
          <a class="nav-link" href="index.html#why">Why Zenith</a>
          <a class="nav-link" href="index.html#area">Service Area</a>
          <a class="head-phone" href="tel:{PHONE_URI}">{PHONE_DISPLAY}</a>
          <a class="btn btn-primary btn-head" href="#request">Request Service</a>
        </nav>
      </div>
    </header>

    <main id="main">
      <!-- ================= Hero ================= -->
      <div class="hero">
        <div class="hero-shade" aria-hidden="true"></div>
        <div class="wrap">
          <div class="hero-in">
            <nav class="crumbs" aria-label="Breadcrumb">
              <a href="index.html">Home</a><span aria-hidden="true">/</span><span>{esc(page['eyebrow'])}</span>
            </nav>
            <p class="kicker">{esc(page['eyebrow'])}</p>
            <h1>{esc(page['h1'])}</h1>
            <p class="hero-lede">{esc(page['lede'])}</p>
            <div class="hero-ctas">
              <a class="btn btn-primary" href="tel:{PHONE_URI}">{PHONE_SVG} Call or text {PHONE_DISPLAY}</a>
              <a class="btn btn-ghost" href="#request">Request service</a>
            </div>
            <dl class="fact-row">
{facts}
            </dl>
          </div>
        </div>
      </div>

      <!-- ================= Signals ================= -->
      <section aria-labelledby="signals-title">
        <div class="wrap">
          <div class="section-head">
            <p class="kicker">Problem first</p>
            <h2 id="signals-title">{esc(page['signals_title'])}</h2>
            <p>{esc(page['signals_intro'])}</p>
          </div>
          <div class="panel">
            <ul class="check-list">
{signals}
            </ul>
          </div>
        </div>
      </section>

      <!-- ================= Pricing ================= -->
      <section class="band" aria-labelledby="pricing-title">
        <div class="wrap">
          <div class="section-head">
            <p class="kicker">Pricing</p>
            <h2 id="pricing-title">Published pricing</h2>
            <p>Straight pricing, published up front. Parts and materials are quoted before any work starts — no surprises on the invoice.</p>
          </div>
          <div class="panel price-panel">
            <div class="price-box">
{pricing_lines}
              <p class="price-note">{esc(page['pricing_note'])}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= Process ================= -->
      <section aria-labelledby="process-title">
        <div class="wrap">
          <div class="section-head">
            <p class="kicker">Method</p>
            <h2 id="process-title">Scope it. Test it. Prove it.</h2>
            <p>The point is a useful diagnosis and a defined next step—not parts roulette.</p>
          </div>
          <div class="steps">
{process}
          </div>
        </div>
      </section>

      <!-- ================= Scope ================= -->
      <section class="band" aria-labelledby="scope-title">
        <div class="wrap">
          <div class="section-head">
            <p class="kicker">Before scheduling</p>
            <h2 id="scope-title">{esc(page['scope_title'])}</h2>
            <p>Send enough detail to tell whether the problem fits Zenith's scope and what the first visit should accomplish.</p>
          </div>
          <div class="req-grid">
            <div class="panel">
              <ul class="check-list">
{scope_items}
              </ul>
            </div>
            <div class="note-box">
              <p><strong>Scope note:</strong> {esc(page['note'])}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= FAQ ================= -->
      <section aria-labelledby="faq-title">
        <div class="wrap">
          <div class="section-head">
            <p class="kicker">Straight answers</p>
            <h2 id="faq-title">Common questions</h2>
          </div>
          <div class="svc-grid">
{faqs}
          </div>
        </div>
      </section>

      <!-- ================= Request ================= -->
      <section id="request" aria-labelledby="booking-title">
        <div class="wrap">
          <div class="req-grid">
            <div class="req-copy" id="service-area">
              <p class="kicker">Request service</p>
              <h2 id="booking-title">Request availability</h2>
              <p class="intro">Mobile service in Key Largo, Tavernier, and Islamorada. Send a complete request; availability and scope are confirmed before any work is accepted.</p>
              <h3>Include these details</h3>
              <ol class="intake-list">
                <li><span class="n">1</span>Boat location</li>
                <li><span class="n">2</span>Vessel make, model, and length</li>
                <li><span class="n">3</span>Service needed</li>
                <li><span class="n">4</span>Equipment make and model</li>
                <li><span class="n">5</span>Symptoms or installation request, plus clear photos</li>
              </ol>
              <div class="direct-contact">
                <span class="dc-label">Call or text</span>
                <a class="dc-phone" href="tel:{PHONE_URI}">{PHONE_DISPLAY}</a>
              </div>
            </div>

            <div class="form-card">
              <div class="form-heading">
                <h3>Service request</h3>
                <p>The button opens a prepared text message. Review it and press send.</p>
              </div>
              <form class="req" data-booking-form>
                <div class="field">
                  <label for="service">Service</label>
                  <select id="service" name="service" required>
{options(page['service'])}
                  </select>
                </div>
                <div class="field">
                  <label for="location">Boat location</label>
                  <input id="location" name="location" type="text" autocomplete="street-address" placeholder="Marina, city, or address" required />
                </div>
                <div class="field">
                  <label for="vessel">Vessel and equipment</label>
                  <input id="vessel" name="vessel" type="text" placeholder="Boat make/model/length + equipment" required />
                </div>
                <div class="field">
                  <label for="date">Preferred service date <span class="opt">(optional)</span></label>
                  <input id="date" name="date" type="date" />
                </div>
                <div class="field">
                  <label for="details">What do you need?</label>
                  <textarea id="details" name="details" rows="5" placeholder="Describe the symptom or installation. Mention when it started and what changed." required></textarea>
                </div>
                <button class="btn btn-primary form-submit" type="submit">Create request text</button>
                <p class="form-status" data-form-status aria-live="polite"></p>
                <noscript><p class="form-noscript">JavaScript is required to prepare the request. Call or text <a href="sms:{PHONE_URI}">{PHONE_DISPLAY}</a>.</p></noscript>
              </form>
            </div>
          </div>
        </div>
      </section>

      <!-- ================= Related ================= -->
      <section class="band" aria-labelledby="related-title">
        <div class="wrap">
          <div class="section-head">
            <p class="kicker">Related services</p>
            <h2 id="related-title">Other Zenith service lanes</h2>
          </div>
          <div class="related-grid">
{related_links(page['slug'])}
          </div>
        </div>
      </section>
    </main>

    <!-- ================= Footer ================= -->
    <footer>
      <div class="wrap">
        <div class="foot-in">
          <div class="foot-brand">
            <img class="foot-logo" src="assets/brand/zenith-full.webp" alt="Zenith Marine Electronics" width="1500" height="618" />
          </div>
          <nav class="foot-links" aria-label="Footer">
            <a href="index.html#services">Services</a>
            <a href="index.html#why">Why Zenith</a>
            <a href="index.html#how">How it works</a>
            <a href="index.html#area">Service Area</a>
            <a href="#request">Request Service</a>
            <a href="privacy.html">Privacy</a>
            <a href="sms:{PHONE_URI}">Text Zenith</a>
            <a href="tel:{PHONE_URI}">{PHONE_DISPLAY}</a>
          </nav>
        </div>
        <div class="foot-bottom">
          <span>© <span data-year>2026</span> Zenith Marine Electronics</span>
          <span>Mobile service · Key Largo · Tavernier · Islamorada</span>
        </div>
      </div>
    </footer>

    <script src="app.js?v=20260817-ga" defer></script>
{CONVERSION_SCRIPT}
  </body>
</html>
'''


def main() -> None:
    for page in PAGES:
        target = ROOT / page["slug"]
        target.write_text(render(page), encoding="utf-8")
        print(target.name)


if __name__ == "__main__":
    main()
