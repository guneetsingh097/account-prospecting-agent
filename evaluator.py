"""
Evaluator module — SLM (Foundry Local) fit evaluation with streaming.
Scores each dimension of the fit rubric and generates an evidence-based assessment.
"""

import os
import json
import time
from typing import Generator

# Foundry Local (OpenAI-compatible)
foundry_ok = False
client = None
model_id = None

def init_foundry():
    """Initialize Foundry Local for SLM inference (non-blocking)."""
    global foundry_ok, client, model_id
    import threading

    def _init():
        global foundry_ok, client, model_id
        try:
            from foundry_local import FoundryLocalManager
            from openai import OpenAI
            manager = FoundryLocalManager()
            model_id = manager.download_model("phi-4-mini")
            client = OpenAI(base_url=manager.endpoint, api_key=manager.api_key)
            foundry_ok = True
            print(f"[SLM] Foundry Local ready — model: {model_id}")
        except Exception as e:
            print(f"[SLM] Foundry Local not available: {e}")
            print("[SLM] Will use structured evaluation without streaming")

    t = threading.Thread(target=_init, daemon=True)
    t.start()
    print("[SLM] Foundry Local initializing in background...")


# Fit rubric dimensions
DIMENSIONS = [
    {
        "id": "regulatory_pressure",
        "name": "Regulatory Pressure",
        "description": "External regulatory forcing functions (CSRD, SEC climate rules, etc.)",
        "scoring": {
            "8-10": "Active deadline + compliance gap + multiple regulatory frameworks",
            "5-7": "Regulatory mentions in filings with some urgency",
            "2-4": "General awareness of regulations, no specific pressure",
            "0-1": "No regulatory pressure signals found"
        }
    },
    {
        "id": "executive_commitment",
        "name": "Executive Commitment",
        "description": "Leadership-level sustainability commitment signals",
        "scoring": {
            "8-10": "C-suite hire (CSO) + public pledge + board committee + budget allocation",
            "5-7": "Public pledges, sustainability reports, leadership mentions",
            "2-4": "Generic sustainability page, minimal leadership action",
            "0-1": "No executive commitment signals found"
        }
    },
    {
        "id": "measurement_gap",
        "name": "Measurement Gap",
        "description": "Acknowledgment they cannot currently track/measure emissions",
        "scoring": {
            "8-10": "Explicitly stated measurement gaps + active vendor evaluation",
            "5-7": "Partial reporting, known gaps in Scope 3 or supply chain",
            "2-4": "Some measurement but unclear completeness",
            "0-1": "No mention of measurement challenges"
        }
    },
    {
        "id": "budget_availability",
        "name": "Budget Availability",
        "description": "Financial capacity and willingness to invest",
        "scoring": {
            "8-10": "Specific budget allocated + revenue growing + investment language",
            "5-7": "Revenue growing, general sustainability investment signals",
            "2-4": "Stable finances but no specific sustainability budget",
            "0-1": "No financial capacity signals"
        }
    },
    {
        "id": "urgency_timing",
        "name": "Urgency / Timing",
        "description": "Time pressure creating a 'buy now' forcing function",
        "scoring": {
            "8-10": "Hard deadline + active vendor evaluation + board mandate",
            "5-7": "Pledges with dates, upcoming regulatory deadlines",
            "2-4": "Soft timelines or general future commitments",
            "0-1": "No timing signals"
        }
    },
    {
        "id": "deal_size_potential",
        "name": "Deal Size Potential",
        "description": "Estimated annual contract value based on company size/complexity",
        "scoring": {
            "8-10": "Large enterprise ($5B+ revenue, 20+ facilities, multi-country) → $300K+ ACV",
            "5-7": "Mid-market ($1-5B revenue, 5-20 facilities) → $100-300K ACV",
            "2-4": "Growing company ($500M-1B) → $50-100K ACV",
            "0-1": "Small or simple operations → <$50K ACV"
        }
    }
]


def evaluate_fit(signals: list, company_data: dict) -> Generator[dict, None, None]:
    """
    Evaluate company fit using collected signals.
    Yields streaming events: dimension scores, then overall assessment.
    """
    yield {"event": "evaluation_started", "data": {
        "dimensions": len(DIMENSIONS),
        "engine": "SLM (Foundry Local)" if foundry_ok else "Structured Evaluation"
    }}

    # Score each dimension
    scores = {}
    total_score = 0
    evaluation_metrics = {
        "dimension_tokens": 0,
        "narrative_tokens_generated": 0,
        "narrative_call": False,
        "total_evaluation_tokens": 0
    }

    for dim in DIMENSIONS:
        time.sleep(0.5)  # Pacing for visual effect
        dim_signals = [s for s in signals if s["category"] == dim["id"]]
        score, evidence = _score_dimension(dim, dim_signals, company_data)
        scores[dim["id"]] = {"score": score, "evidence": evidence, "name": dim["name"]}
        total_score += score
        estimated_tokens = max(1, (len(evidence) + len(dim["name"]) + len(dim["description"])) // 4)
        evaluation_metrics["dimension_tokens"] += estimated_tokens

        yield {"event": "dimension_scored", "data": {
            "dimension_id": dim["id"],
            "dimension_name": dim["name"],
            "score": score,
            "max_score": 10,
            "evidence": evidence,
            "running_total": total_score,
            "tokens": estimated_tokens
        }}

    max_possible = len(DIMENSIONS) * 10  # 60

    # Determine fit level based on percentage of max
    score_pct = (total_score / max_possible) * 100 if max_possible > 0 else 0
    if score_pct >= 75:
        fit_level = "HIGH"
    elif score_pct >= 45:
        fit_level = "MEDIUM"
    else:
        fit_level = "LOW"

    # Estimate ACV
    acv = _estimate_acv(company_data, total_score)

    # Stream the fit narrative
    yield {"event": "fit_determined", "data": {
        "fit_level": fit_level,
        "total_score": total_score,
        "max_possible": max_possible,
        "acv_estimate": acv,
        "scores": scores
    }}

    evaluation_metrics["total_evaluation_tokens"] = evaluation_metrics["dimension_tokens"]

    # Generate streaming narrative
    if foundry_ok:
        yield from _stream_narrative(company_data, scores, fit_level, total_score, signals, evaluation_metrics)
    else:
        yield from _generate_structured_narrative(company_data, scores, fit_level, total_score, evaluation_metrics)


def _score_dimension(dimension: dict, dim_signals: list, company_data: dict) -> tuple:
    """Score a single dimension 0-10 based on available signals."""
    dim_id = dimension["id"]

    if not dim_signals:
        return 0, "No signals found"

    # Score based on signal strength
    quotes = [s["quote"] for s in dim_signals]
    best_quote = max(quotes, key=len) if quotes else ""
    combined_text = " ".join(quotes).lower()
    num_signals = len(dim_signals)

    # Negative sentiment check — only flag truly negative business context
    negative_indicators = ["layoff", "restructur", "cost-cutting", "spending freeze",
                          "paused sustainability", "suspended sustainability",
                          "cancelled program", "canceled program",
                          "discretionary spending", "abandoned"]
    has_negative = any(neg in combined_text for neg in negative_indicators)

    # For risk_factor dimension — handled separately in evaluate_fit
    if dim_id == "risk_factor":
        return 0, "No risk signals"

    # If overwhelmingly negative with very few signals, score low
    if has_negative and num_signals <= 2:
        return 1, best_quote

    # Quality indicators boost the score
    strong_indicators = ["$", "million", "billion", "hire", "appoint",
                        "deadline", "by 2026", "by 2027", "by 2030",
                        "commit", "pledge", "target", "goal", "invest",
                        "report", "scope 1", "scope 2", "scope 3"]
    quality_hits = sum(1 for ind in strong_indicators if ind in combined_text)

    # 0-10 scoring: signal count + quality
    # Base score from signal count (0-6 range)
    if num_signals >= 10:
        base = 6
    elif num_signals >= 5:
        base = 5
    elif num_signals >= 3:
        base = 4
    elif num_signals >= 2:
        base = 3
    else:
        base = 2

    # Quality bonus (0-4 range)
    if quality_hits >= 4:
        quality_bonus = 4
    elif quality_hits >= 2:
        quality_bonus = 3
    elif quality_hits >= 1:
        quality_bonus = 2
    else:
        quality_bonus = 0

    score = min(10, base + quality_bonus)
    return score, best_quote


def _estimate_acv(company_data: dict, fit_score: int) -> str:
    """Estimate annual contract value based on company characteristics."""
    revenue_str = company_data.get("revenue", "$0")
    facilities = company_data.get("facilities", 1)

    # Parse revenue (rough)
    try:
        rev_num = float(revenue_str.replace("$", "").replace("B", "").replace("M", "").replace(",", "").strip())
        if "B" in revenue_str:
            rev_num *= 1000  # Convert to millions
    except (ValueError, AttributeError):
        rev_num = 1000  # Default $1B

    # Base ACV on revenue + facilities
    if rev_num >= 5000 and facilities >= 15:
        base = "$300K - $750K"
    elif rev_num >= 2000 and facilities >= 8:
        base = "$150K - $350K"
    elif rev_num >= 1000:
        base = "$80K - $200K"
    else:
        base = "$40K - $100K"

    return base


def _stream_narrative(company_data: dict, scores: dict, fit_level: str, total_score: int, signals: list, evaluation_metrics: dict) -> Generator[dict, None, None]:
    """Stream fit narrative using Foundry Local SLM."""
    company_name = company_data.get("name", "the company")

    # Build context for the SLM
    evidence_text = ""
    for dim_id, dim_data in scores.items():
        if dim_data["score"] > 0:
            evidence_text += f"- {dim_data['name']} (score {dim_data['score']}/2): {dim_data['evidence']}\n"
        elif dim_data["score"] < 0:
            evidence_text += f"- ⚠️ {dim_data['name']} (RISK): {dim_data['evidence']}\n"

    prompt = (
        f"You are a B2B sales analyst at Proseware (sustainability/carbon management platform). "
        f"Write a 3-4 sentence executive summary of why {company_name} is a {fit_level} fit prospect. "
        f"Score: {total_score}/12. Be specific and cite the evidence.\n\n"
        f"Evidence:\n{evidence_text}\n\n"
        f"Company: {company_name}, {company_data.get('industry', '')}, {company_data.get('revenue', '')} revenue, "
        f"{company_data.get('headcount', '')} employees, {company_data.get('facilities', '')} facilities.\n\n"
        f"Write the summary now:"
    )

    try:
        evaluation_metrics["narrative_call"] = True
        stream = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            stream=True
        )
        generated_chars = 0
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                generated_chars += len(token)
                yield {"event": "narrative_token", "data": {"token": token, "tokens": max(1, len(token) // 4)}}

        evaluation_metrics["narrative_tokens_generated"] = max(1, generated_chars // 4) if generated_chars else 0
        evaluation_metrics["total_evaluation_tokens"] = evaluation_metrics["dimension_tokens"] + evaluation_metrics["narrative_tokens_generated"]
        yield {"event": "narrative_complete", "data": {"evaluation_metrics": evaluation_metrics}}

    except Exception as e:
        print(f"[SLM] Stream error: {e}")
        yield from _generate_structured_narrative(company_data, scores, fit_level, total_score, evaluation_metrics)


def _generate_structured_narrative(company_data: dict, scores: dict, fit_level: str, total_score: int, evaluation_metrics: dict) -> Generator[dict, None, None]:
    """Generate a narrative without SLM (structured fallback)."""
    company_name = company_data.get("name", "This company")

    # Build narrative from scores
    positives = []
    risks = []
    for dim_id, dim_data in scores.items():
        if dim_data["score"] >= 6:
            positives.append(f"{dim_data['name']}: {dim_data['evidence'][:80]}")
        elif dim_data["score"] < 0:
            risks.append(f"{dim_data['name']}: {dim_data['evidence'][:80]}")

    max_possible = len(DIMENSIONS) * 10
    narrative = f"{company_name} shows {fit_level} fit for Proseware's sustainability platform (score: {total_score}/{max_possible}). "

    if positives:
        narrative += f"Key strengths: {'; '.join(positives[:3])}. "
    if risks:
        narrative += f"Risk factors: {'; '.join(risks[:2])}. "

    if fit_level == "HIGH":
        narrative += "Recommend immediate outreach — multiple buying signals confirmed."
    elif fit_level == "MEDIUM":
        narrative += "Worth monitoring — some signals present but not all dimensions confirmed."
    else:
        narrative += "Not recommended for active pursuit at this time."

    # Stream it token-by-token for visual effect
    words = narrative.split(" ")
    generated_chars = 0
    for word in words:
        time.sleep(0.03)
        token = word + " "
        generated_chars += len(token)
        yield {"event": "narrative_token", "data": {"token": token, "tokens": max(1, len(token) // 4)}}

    evaluation_metrics["narrative_tokens_generated"] = max(1, generated_chars // 4) if generated_chars else 0
    evaluation_metrics["total_evaluation_tokens"] = evaluation_metrics["dimension_tokens"] + evaluation_metrics["narrative_tokens_generated"]
    yield {"event": "narrative_complete", "data": {"evaluation_metrics": evaluation_metrics}}
