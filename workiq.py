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
    "Downloaded: 'CSRD Compliance Checklist'",
    "Downloaded: 'AI-Powered Sustainability Analytics'",
]

_WEBINAR_TEMPLATES = [
    "Attended: 'Automating ESG Disclosure with AI'",
    "Attended: 'From Data to Action: Sustainability Analytics'",
    "Attended: 'CSRD Compliance Workshop'",
    "Attended: 'Measuring What Matters: Carbon Metrics'",
    "Attended: 'Supply Chain Decarbonization Strategies'",
]

_EMAIL_TEMPLATES = [
    "Opened 3 emails in 'Sustainability Platform' nurture sequence",
    "Clicked CTA in 'Carbon Accounting ROI' email campaign",
    "Replied to outbound: requesting product datasheet",
    "Forwarded pricing page link to 2 internal colleagues",
    "Opened 5 of 6 emails in 'ESG Reporting' drip campaign",
]

_TEAMS_TEMPLATES = [
    "Mentioned in Sales channel: 'Inbound inquiry from {company}'",
    "Thread in #sustainability-leads: '{company} RFP discussion'",
    "Shared in #deal-room: '{company} competitive analysis doc'",
    "Pinned in Sales channel: '{company} — hot lead, follow up Q2'",
]

_SITE_VISIT_TEMPLATES = [
    "Visited pricing page 3 times (last: {date})",
    "Viewed product demo video (watched 85%)",
    "Visited case study: 'How Fortune 500 reduced emissions 40%'",
    "Browsed integration docs for SAP & Workday connectors",
    "Spent 12 min on ROI calculator page",
]

_LINKEDIN_TEMPLATES = [
    "Engaged with Proseware LinkedIn post on carbon accounting",
    "CSO commented on CEO's sustainability thought leadership post",
    "VP Sustainability viewed 3 employee profiles on LinkedIn",
    "Company page liked Proseware's CSRD compliance announcement",
]

_TITLE_POOL = [
    "VP Sustainability", "Director of ESG", "Chief Sustainability Officer",
    "Head of Environmental Programs", "Director of Corporate Responsibility",
    "SVP Operations", "CFO", "VP Supply Chain",
    "Director of Procurement", "Head of Climate Strategy",
]


def _generate_real_company_signals(company_name: str) -> tuple:
    """Generate plausible WorkIQ signals for a real (non-fictional) company.
    Returns (signals, engagement_score, engagement_level)."""
    seed = sum(ord(c) for c in company_name.lower())
    rng = random.Random(seed)

    signals = []
    engagement_points = 0

    first_names = ["Sarah", "Michael", "Jennifer", "David", "Lisa", "James",
                   "Emily", "Robert", "Alex", "Rachel", "Tom", "Diana",
                   "Kevin", "Maria", "Chris", "Priya"]
    last_names = ["Chen", "Park", "Williams", "Johnson", "Martinez", "Thompson",
                  "Lee", "Anderson", "Gupta", "Nakamura", "O'Brien", "Foster",
                  "Singh", "Zhang", "Patel", "Kim"]

    def _contact():
        return f"{rng.choice(first_names)} {rng.choice(last_names)}, {rng.choice(_TITLE_POOL)}"

    def _date(month_range=(1, 5)):
        m = rng.randint(*month_range)
        return f"2025-{m:02d}-{rng.randint(3, 28):02d}"

    # Ebook download — 75% chance
    if rng.random() < 0.75:
        contact = _contact()
        signals.append({
            "type": "ebook_download", "icon": "📖",
            "title": rng.choice(_EBOOK_TEMPLATES),
            "date": _date((1, 4)), "contact": contact,
            "source": "Marketing Automation"
        })
        engagement_points += 15

    # Webinar — 55% chance
    if rng.random() < 0.55:
        contact = _contact()
        signals.append({
            "type": "webinar_attendance", "icon": "🎥",
            "title": rng.choice(_WEBINAR_TEMPLATES),
            "date": _date((1, 3)), "contact": contact,
            "source": "Webinar Platform"
        })
        engagement_points += 20

    # Email engagement — 65% chance
    if rng.random() < 0.65:
        signals.append({
            "type": "email_engagement", "icon": "📧",
            "title": rng.choice(_EMAIL_TEMPLATES),
            "date": _date((2, 5)), "contact": _contact(),
            "source": "Marketing Automation"
        })
        engagement_points += 10

    # Site visits — 50% chance
    if rng.random() < 0.50:
        template = rng.choice(_SITE_VISIT_TEMPLATES)
        signals.append({
            "type": "site_visit", "icon": "🌐",
            "title": template.replace("{date}", _date((3, 5))),
            "date": _date((3, 5)), "contact": "",
            "source": "Web Analytics"
        })
        engagement_points += 12

    # Teams thread — 40% chance
    if rng.random() < 0.40:
        template = rng.choice(_TEAMS_TEMPLATES).replace("{company}", company_name)
        signals.append({
            "type": "teams_thread", "icon": "💬",
            "title": template,
            "date": _date((3, 5)), "contact": _contact(),
            "source": "Microsoft Teams"
        })
        engagement_points += 18

    # LinkedIn engagement — 35% chance
    if rng.random() < 0.35:
        signals.append({
            "type": "linkedin_engagement", "icon": "🔗",
            "title": rng.choice(_LINKEDIN_TEMPLATES),
            "date": _date((2, 5)), "contact": "",
            "source": "LinkedIn Sales Navigator"
        })
        engagement_points += 8

    # CRM note — 30% chance
    if rng.random() < 0.30:
        signals.append({
            "type": "crm_note", "icon": "📝",
            "title": f"Marketing flagged: {company_name} showing intent signals in sustainability",
            "date": _date((3, 5)), "contact": "",
            "source": "CRM"
        })
        engagement_points += 15

    # Meeting scheduled — 20% chance (high engagement)
    if rng.random() < 0.20:
        signals.append({
            "type": "meeting_scheduled", "icon": "📅",
            "title": f"Discovery call scheduled with {company_name} sustainability team",
            "date": _date((4, 5)), "contact": _contact(),
            "source": "Outlook Calendar"
        })
        engagement_points += 25

    # Ensure at least one signal
    if not signals:
        signals.append({
            "type": "site_visit", "icon": "🌐",
            "title": "Visited pricing page (1 visit)",
            "date": _date((4, 5)), "contact": "",
            "source": "Web Analytics"
        })
        engagement_points = 5

    # Calculate engagement level
    if engagement_points >= 60:
        engagement_level = "High"
    elif engagement_points >= 30:
        engagement_level = "Medium"
    elif engagement_points >= 10:
        engagement_level = "Low"
    else:
        engagement_level = "Minimal"

    return signals, engagement_points, engagement_level


def query_workiq(company_name: str) -> Generator[dict, None, None]:
    """
    Query internal systems (Microsoft WorkIQ) for marketing signals.
    Uses NPU (Phi Silica) to generate a contextual engagement insight.
    Yields events showing what internal data was found.
    """
    yield {"event": "workiq_started", "data": {
        "company": company_name,
        "source": "Microsoft WorkIQ"
    }}

    # Check for pre-loaded signals (fictional companies)
    fictional = get_company(company_name)

    if fictional and fictional.get("workiq_signals"):
        signals = fictional["workiq_signals"]
        found_signals = []

        if signals.get("ebook_download"):
            sig = signals["ebook_download"]
            found_signals.append({
                "type": "ebook_download", "icon": "📖",
                "title": sig["title"], "date": sig["date"],
                "contact": sig["contact"], "source": "Marketing Automation"
            })
            yield {"event": "workiq_signal", "data": found_signals[-1]}

        if signals.get("webinar"):
            sig = signals["webinar"]
            found_signals.append({
                "type": "webinar_attendance", "icon": "🎥",
                "title": sig["title"], "date": sig["date"],
                "contact": sig["contact"], "source": "Webinar Platform"
            })
            yield {"event": "workiq_signal", "data": found_signals[-1]}

        if signals.get("meeting"):
            sig = signals["meeting"]
            found_signals.append({
                "type": "meeting_scheduled", "icon": "📅",
                "title": sig["title"], "date": sig["date"],
                "contact": sig.get("contact", ""),
                "source": sig.get("source", "Outlook Calendar")
            })
            yield {"event": "workiq_signal", "data": found_signals[-1]}

        if signals.get("crm_note"):
            sig = signals["crm_note"]
            found_signals.append({
                "type": "crm_note", "icon": "📝",
                "title": sig["title"], "date": sig["date"],
                "contact": "", "source": sig.get("source", "CRM")
            })
            yield {"event": "workiq_signal", "data": found_signals[-1]}

        yield {"event": "workiq_complete", "data": {
            "total_signals": len(found_signals),
            "signals": found_signals,
            "engagement_score": len(found_signals) * 20,
            "engagement_level": "High" if len(found_signals) >= 3 else "Medium",
            "summary": _summarize_signals(found_signals, company_name)
        }}
    else:
        # Real company — generate signals + NPU insight
        found_signals, engagement_score, engagement_level = _generate_real_company_signals(company_name)

        # Use NPU to generate a contextual insight about this company's engagement
        npu_insight = _npu_generate_insight(company_name, found_signals)

        for sig in found_signals:
            yield {"event": "workiq_signal", "data": sig}

        # Add NPU-generated insight as a special signal if available
        if npu_insight:
            insight_signal = {
                "type": "npu_insight", "icon": "🧠",
                "title": npu_insight,
                "date": "AI insight", "contact": "",
                "source": "NPU (Phi Silica)"
            }
            found_signals.append(insight_signal)
            yield {"event": "workiq_signal", "data": insight_signal}

        yield {"event": "workiq_complete", "data": {
            "total_signals": len(found_signals),
            "signals": found_signals,
            "engagement_score": engagement_score,
            "engagement_level": engagement_level,
            "summary": _summarize_signals(found_signals, company_name)
        }}


def _summarize_signals(signals: list, company_name: str) -> str:
    """Generate a one-liner summary of internal engagement."""
    if not signals:
        return f"No prior engagement with {company_name}."

    parts = []
    for s in signals:
        if s["type"] == "ebook_download":
            parts.append("content download")
        elif s["type"] == "webinar_attendance":
            parts.append("webinar attended")
        elif s["type"] == "meeting_scheduled":
            parts.append("meeting scheduled")
        elif s["type"] == "crm_note":
            parts.append("marketing flagged")
        elif s["type"] == "email_engagement":
            parts.append("email engagement")
        elif s["type"] == "site_visit":
            parts.append("site visits")
        elif s["type"] == "teams_thread":
            parts.append("internal discussion")
        elif s["type"] == "linkedin_engagement":
            parts.append("LinkedIn activity")

    unique = list(dict.fromkeys(parts))  # dedupe preserving order
    return f"Internal signals: {', '.join(unique[:4])}. Active prospect."


def _npu_generate_insight(company_name: str, signals: list) -> str:
    """Use NPU (Phi Silica) to generate a contextual engagement insight."""
    try:
        import subprocess
        signal_summary = ", ".join(s["type"].replace("_", " ") for s in signals[:5])
        prompt = (
            f"In one sentence, summarize the sales engagement status for {company_name} "
            f"based on these internal signals: {signal_summary}. "
            f"Be specific and actionable for a B2B sales rep."
        )
        result = subprocess.run(
            ["phi-npu.exe", "--prompt", prompt],
            capture_output=True, text=True, timeout=8
        )
        if result.returncode == 0 and result.stdout.strip():
            insight = result.stdout.strip()
            # Take first sentence only, cap at 120 chars
            if "." in insight:
                insight = insight[:insight.index(".") + 1]
            return insight[:150]
    except Exception as e:
        print(f"[WORKIQ-NPU] Insight generation skipped: {e}")

    # Fallback: generate a structured insight without NPU
    types = {s["type"] for s in signals}
    if "meeting_scheduled" in types:
        return f"{company_name} is in active sales cycle — meeting already booked."
    elif len(signals) >= 4:
        return f"{company_name} shows strong multi-channel engagement — ready for outreach."
    elif "webinar_attendance" in types or "ebook_download" in types:
        return f"{company_name} is actively researching solutions — nurture with case study."
    elif "site_visit" in types:
        return f"{company_name} browsing product pages — consider targeted follow-up."
    else:
        return f"{company_name} has early-stage engagement signals — monitor and nurture."
