"""
WorkIQ module — simulates querying Microsoft 365 Copilot for internal signals.
In demo mode, returns pre-loaded marketing signals for fictional companies.
For real companies, generates realistic engagement signals to simulate WorkIQ integration.
"""

import time
import random
from typing import Generator
from companies import get_company


# Realistic marketing signal templates for real companies
_EBOOK_TEMPLATES = [
    "Downloaded: 'Scope 3 Emissions Measurement Guide'",
    "Downloaded: 'Carbon Accounting for Enterprise'",
    "Downloaded: 'ESG Reporting Best Practices 2024'",
    "Downloaded: 'Supply Chain Sustainability Playbook'",
    "Downloaded: 'Net-Zero Roadmap for Large Enterprises'",
]

_WEBINAR_TEMPLATES = [
    "Attended: 'Automating ESG Disclosure with AI'",
    "Attended: 'From Data to Action: Sustainability Analytics'",
    "Attended: 'CSRD Compliance Workshop'",
    "Attended: 'Measuring What Matters: Carbon Metrics'",
]

_TITLE_POOL = [
    "VP Sustainability", "Director of ESG", "Chief Sustainability Officer",
    "Head of Environmental Programs", "Director of Corporate Responsibility",
    "SVP Operations", "CFO", "VP Supply Chain",
]


def _generate_real_company_signals(company_name: str) -> list:
    """Generate plausible WorkIQ signals for a real (non-fictional) company."""
    # Use company name as seed for consistent results per company
    seed = sum(ord(c) for c in company_name.lower())
    rng = random.Random(seed)

    signals = []
    # 70% chance of ebook download
    if rng.random() < 0.7:
        title = rng.choice(_TITLE_POOL)
        first_names = ["Sarah", "Michael", "Jennifer", "David", "Lisa", "James", "Emily", "Robert"]
        last_names = ["Chen", "Park", "Williams", "Johnson", "Martinez", "Thompson", "Lee", "Anderson"]
        contact = f"{rng.choice(first_names)} {rng.choice(last_names)}, {title}"
        month = rng.randint(1, 4)
        signals.append({
            "type": "ebook_download",
            "icon": "📖",
            "title": rng.choice(_EBOOK_TEMPLATES),
            "date": f"2025-0{month}-{rng.randint(5, 28):02d}",
            "contact": contact,
            "source": "Marketing Automation"
        })

    # 50% chance of webinar attendance
    if rng.random() < 0.5:
        title = rng.choice(_TITLE_POOL)
        first_names = ["Alex", "Rachel", "Tom", "Diana", "Kevin", "Maria"]
        last_names = ["Gupta", "Nakamura", "O'Brien", "Foster", "Singh", "Zhang"]
        contact = f"{rng.choice(first_names)} {rng.choice(last_names)}, {title}"
        month = rng.randint(1, 3)
        signals.append({
            "type": "webinar_attendance",
            "icon": "🎥",
            "title": rng.choice(_WEBINAR_TEMPLATES),
            "date": f"2025-0{month}-{rng.randint(5, 28):02d}",
            "contact": contact,
            "source": "Webinar Platform"
        })

    # 30% chance of CRM note from marketing
    if rng.random() < 0.3:
        signals.append({
            "type": "crm_note",
            "icon": "📝",
            "title": f"Marketing flagged: {company_name} showing intent signals in sustainability",
            "date": f"2025-04-{rng.randint(1, 28):02d}",
            "contact": "",
            "source": "CRM"
        })

    # If nothing generated, always give at least one signal
    if not signals:
        signals.append({
            "type": "ebook_download",
            "icon": "📖",
            "title": "Downloaded: 'Enterprise Carbon Accounting Guide'",
            "date": "2025-03-12",
            "contact": f"Unknown contact at {company_name}",
            "source": "Marketing Automation"
        })

    return signals


def query_workiq(company_name: str) -> Generator[dict, None, None]:
    """
    Query internal systems (WorkIQ / M365 Copilot) for marketing signals.
    Yields events showing what internal data was found.
    """
    yield {"event": "workiq_started", "data": {
        "company": company_name,
        "source": "Microsoft 365 Copilot (WorkIQ)"
    }}

    # Check for pre-loaded signals (fictional companies)
    fictional = get_company(company_name)

    if fictional and fictional.get("workiq_signals"):
        signals = fictional["workiq_signals"]
        found_signals = []

        time.sleep(0.8)  # Simulate cloud query latency

        # Check each signal type
        if signals.get("ebook_download"):
            sig = signals["ebook_download"]
            found_signals.append({
                "type": "ebook_download",
                "icon": "📖",
                "title": sig["title"],
                "date": sig["date"],
                "contact": sig["contact"],
                "source": "Marketing Automation"
            })
            yield {"event": "workiq_signal", "data": found_signals[-1]}
            time.sleep(0.4)

        if signals.get("webinar"):
            sig = signals["webinar"]
            found_signals.append({
                "type": "webinar_attendance",
                "icon": "🎥",
                "title": sig["title"],
                "date": sig["date"],
                "contact": sig["contact"],
                "source": "Webinar Platform"
            })
            yield {"event": "workiq_signal", "data": found_signals[-1]}
            time.sleep(0.4)

        if signals.get("meeting"):
            sig = signals["meeting"]
            found_signals.append({
                "type": "meeting_scheduled",
                "icon": "📅",
                "title": sig["title"],
                "date": sig["date"],
                "contact": sig.get("contact", ""),
                "source": sig.get("source", "Outlook Calendar")
            })
            yield {"event": "workiq_signal", "data": found_signals[-1]}
            time.sleep(0.4)

        if signals.get("crm_note"):
            sig = signals["crm_note"]
            found_signals.append({
                "type": "crm_note",
                "icon": "📝",
                "title": sig["title"],
                "date": sig["date"],
                "contact": "",
                "source": sig.get("source", "CRM")
            })
            yield {"event": "workiq_signal", "data": found_signals[-1]}
            time.sleep(0.4)

        yield {"event": "workiq_complete", "data": {
            "total_signals": len(found_signals),
            "signals": found_signals,
            "summary": _summarize_signals(found_signals, company_name)
        }}
    else:
        # Real company — generate plausible signals
        time.sleep(1.2)  # Simulate cloud query latency
        found_signals = _generate_real_company_signals(company_name)

        for sig in found_signals:
            yield {"event": "workiq_signal", "data": sig}
            time.sleep(0.4)

        yield {"event": "workiq_complete", "data": {
            "total_signals": len(found_signals),
            "signals": found_signals,
            "summary": _summarize_signals(found_signals, company_name)
        }}


def _summarize_signals(signals: list, company_name: str) -> str:
    """Generate a one-liner summary of internal engagement."""
    if not signals:
        return f"No prior engagement with {company_name}."

    parts = []
    for s in signals:
        if s["type"] == "ebook_download":
            parts.append(f"{s['contact']} downloaded content")
        elif s["type"] == "webinar_attendance":
            parts.append(f"{s['contact']} attended a webinar")
        elif s["type"] == "meeting_scheduled":
            parts.append("meeting already scheduled")
        elif s["type"] == "crm_note":
            parts.append("marketing flagged this account")

    return f"Internal signals: {', '.join(parts)}. They're already warming up."
