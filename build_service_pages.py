#!/usr/bin/env python3
"""Generate Zenith's static high-intent service landing pages."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://zenithmarineelectronics.com/"
PHONE_DISPLAY = "305-306-6391"
PHONE_URI = "+13053066391"
GA4 = "G-H8KGT9K2TM"

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
        f'            <option value="{esc(value)}"{" selected" if value == selected else ""}>{esc(value)}</option>'
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
        f'            <a href="{esc(other["slug"])}">{esc(other["service_type"])}</a>'
        for other in PAGES
        if other["slug"] != current_slug
    )


def render(page: dict) -> str:
    canonical = BASE + page["slug"]
    facts = "\n".join(
        f"          <div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>" for label, value in page["facts"]
    )
    signals = "\n".join(f"            <li>{esc(item)}</li>" for item in page["signals"])
    process = "\n".join(
        f"          <article class=\"detail-card\"><span>{esc(label)}</span><h3>{esc(title.split(' · ', 1)[-1])}</h3><p>{esc(text)}</p></article>"
        for label, text in page["process"]
        for title in [label]
    )
    scope_items = "\n".join(f"            <li>{esc(item)}</li>" for item in page["scope"])
    faqs = "\n".join(
        f"          <article class=\"detail-card\"><h3>{esc(question)}</h3><p>{esc(answer)}</p></article>"
        for question, answer in page["faqs"]
    )

    return f'''<!doctype html>
<html lang="en" class="no-js">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function(){{ window.dataLayer.push(arguments); }};
    window.gtag('js', new Date());
    window.gtag('config', '{GA4}');
  </script>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#071f35">
  <meta name="description" content="{esc(page['description'])}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Zenith Marine Electronics">
  <meta property="og:title" content="{esc(page['title'])}">
  <meta property="og:description" content="{esc(page['description'])}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{BASE}assets/images/harbor-social.webp">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(page['title'])}">
  <meta name="twitter:description" content="{esc(page['description'])}">
  <meta name="twitter:image" content="{BASE}assets/images/harbor-social.webp">
  <title>{esc(page['title'])} | Zenith Marine Electronics</title>
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="icon" href="assets/brand/favicon.png" type="image/png">
  <link rel="stylesheet" href="styles.css?v=20260817">
  <link rel="stylesheet" href="service-pages.css?v=20260817">
  <script>document.documentElement.classList.replace('no-js', 'js');</script>
  <script type="application/ld+json">
{schema(page)}
  </script>
</head>
<body class="service-detail-page">
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header" data-header>
    <div class="shell header-inner">
      <a class="brand" href="index.html" aria-label="Zenith Marine Electronics home">
        <img src="assets/brand/zenith-full.webp" alt="Zenith Marine Electronics" width="1500" height="618">
      </a>
      <nav class="primary-nav" aria-label="Primary navigation">
        <a href="index.html#services">Services</a>
        <a href="index.html#qualifications">Qualifications</a>
        <a href="index.html#service-area">Service area</a>
      </nav>
      <div class="header-actions">
        <a class="header-phone" href="tel:{PHONE_URI}">{PHONE_DISPLAY}</a>
        <a class="button button-small" href="#request">Request availability</a>
      </div>
    </div>
  </header>

  <main id="main">
    <section class="detail-hero" aria-labelledby="detail-title">
      <div class="shell detail-hero-grid">
        <div>
          <nav class="detail-breadcrumbs" aria-label="Breadcrumb">
            <a href="index.html">Home</a><span aria-hidden="true">/</span><span>{esc(page['eyebrow'])}</span>
          </nav>
          <p class="eyebrow">{esc(page['eyebrow'])}</p>
          <h1 id="detail-title">{esc(page['h1'])}</h1>
          <p class="detail-lede">{esc(page['lede'])}</p>
          <div class="detail-actions">
            <a class="button button-hero" href="#request">Request availability</a>
            <a class="detail-call" href="tel:{PHONE_URI}">Call {PHONE_DISPLAY}</a>
          </div>
        </div>
        <dl class="detail-facts">
{facts}
        </dl>
      </div>
    </section>

    <section class="detail-section detail-section-white" aria-labelledby="signals-title">
      <div class="shell detail-grid">
        <div class="detail-copy">
          <p class="eyebrow eyebrow-dark">Problem first</p>
          <h2 id="signals-title">{esc(page['signals_title'])}</h2>
          <p>{esc(page['signals_intro'])}</p>
        </div>
        <ul class="signal-list">
{signals}
        </ul>
      </div>
    </section>

    <section class="detail-section" aria-labelledby="process-title">
      <div class="shell">
        <div class="detail-heading">
          <p class="eyebrow eyebrow-dark">Method</p>
          <h2 id="process-title">Scope it. Test it. Prove it.</h2>
          <p>The point is a useful diagnosis and a defined next step—not parts roulette.</p>
        </div>
        <div class="detail-cards">
{process}
        </div>
      </div>
    </section>

    <section class="detail-section detail-section-white" aria-labelledby="scope-title">
      <div class="shell detail-grid">
        <div class="detail-copy">
          <p class="eyebrow eyebrow-dark">Before scheduling</p>
          <h2 id="scope-title">{esc(page['scope_title'])}</h2>
          <p>Send enough detail to tell whether the problem fits Zenith's scope and what the first visit should accomplish.</p>
          <p class="detail-note"><strong>Scope note:</strong> {esc(page['note'])}</p>
        </div>
        <ul class="scope-list">
{scope_items}
        </ul>
      </div>
    </section>

    <section class="detail-section" aria-labelledby="faq-title">
      <div class="shell">
        <div class="detail-heading">
          <p class="eyebrow eyebrow-dark">Straight answers</p>
          <h2 id="faq-title">Common questions</h2>
        </div>
        <div class="detail-cards">
{faqs}
        </div>
      </div>
    </section>

    <section class="booking section" id="request" aria-labelledby="booking-title">
      <div class="shell booking-grid">
        <div class="booking-copy" id="service-area">
          <p class="eyebrow eyebrow-dark">Demand test</p>
          <h2 id="booking-title">Request availability</h2>
          <p class="booking-intro">Zenith is measuring demand for mobile service in Key Largo, Tavernier, and Islamorada. Send a complete request; availability and scope are confirmed before any work is accepted.</p>
          <h3>Include these details</h3>
          <ol class="intake-list">
            <li><span>1</span>Boat location</li>
            <li><span>2</span>Vessel make, model, and length</li>
            <li><span>3</span>Service needed</li>
            <li><span>4</span>Equipment make and model</li>
            <li><span>5</span>Symptoms or installation request, plus clear photos</li>
          </ol>
          <div class="direct-contact"><span>Call or text</span><a href="tel:{PHONE_URI}">{PHONE_DISPLAY}</a></div>
        </div>

        <form class="booking-form" data-booking-form>
          <div class="form-heading">
            <h3>Service request</h3>
            <p>The button opens a prepared text message. Review it and press send.</p>
          </div>
          <label for="service">Service</label>
          <select id="service" name="service" required>
{options(page['service'])}
          </select>
          <label for="location">Boat location</label>
          <input id="location" name="location" type="text" autocomplete="street-address" placeholder="Marina, city, or address" required>
          <label for="vessel">Vessel and equipment</label>
          <input id="vessel" name="vessel" type="text" placeholder="Boat make/model/length + equipment" required>
          <label for="date">Preferred service date <span>(optional)</span></label>
          <input id="date" name="date" type="date">
          <label for="details">What do you need?</label>
          <textarea id="details" name="details" rows="5" placeholder="Describe the symptom or installation. Mention when it started and what changed." required></textarea>
          <button class="button form-submit" type="submit">Create request text</button>
          <p class="form-status" data-form-status aria-live="polite"></p>
          <noscript><p>JavaScript is required to prepare the request. Call or text <a href="sms:{PHONE_URI}">{PHONE_DISPLAY}</a>.</p></noscript>
        </form>
      </div>
    </section>

    <section class="detail-section detail-section-white" aria-labelledby="related-title">
      <div class="shell detail-copy">
        <p class="eyebrow eyebrow-dark">Related services</p>
        <h2 id="related-title">Other Zenith service lanes</h2>
        <div class="related-services">
{related_links(page['slug'])}
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="shell footer-inner">
      <div><strong>Zenith Marine Electronics</strong><span>Mobile service · Upper Florida Keys</span></div>
      <div class="footer-actions">
        <a href="tel:{PHONE_URI}">Call {PHONE_DISPLAY}</a>
        <a href="sms:{PHONE_URI}">Text Zenith</a>
        <a href="privacy.html">Privacy</a>
      </div>
      <small>© <span data-year></span> Zenith Marine Electronics</small>
    </div>
  </footer>

  <script src="app.js?v=20260817-ga" defer></script>
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
