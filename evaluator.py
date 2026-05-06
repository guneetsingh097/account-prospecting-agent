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
            2: "Active deadline within 12 months + explicit compliance gap acknowledged",
            1: "Regulatory mentions in filings but no urgent deadline",
            0: "No regulatory pressure signals found",
            -1: "Already compliant or exempt from regulations"
        }
    },
    {
        "id": "executive_commitment",
        "name": "Executive Commitment",
        "description": "Leadership-level sustainability commitment signals",
        "scoring": {
            2: "C-suite hire (CSO) + public pledge + board-level committee",
            1: "Public pledge OR leadership hire (one signal)",
            0: "Generic sustainability page but no leadership action",
            -1: "Leadership actively deprioritizing sustainability"
        }
    },
    {
        "id": "measurement_gap",
        "name": "Measurement Gap",
        "description": "Acknowledgment they cannot currently track/measure emissions",
        "scoring": {
            2: "Explicitly stated: 'we lack measurement infrastructure'",
            1: "Partial reporting acknowledged (Scope 1&2 only, manual processes)",
            0: "No mention of measurement challenges",
            -1: "Already have comprehensive automated measurement"
        }
    },
    {
        "id": "budget_availability",
        "name": "Budget Availability",
        "description": "Financial capacity and willingness to invest",
        "scoring": {
            2: "Specific budget allocated ($XM for sustainability tech) + revenue growing",
            1: "Revenue growing, general investment language",
            0: "Flat or unclear financial position",
            -1: "Cost-cutting, spending freeze, declining revenue"
        }
    },
    {
        "id": "urgency_timing",
        "name": "Urgency / Timing",
        "description": "Time pressure creating a 'buy now' forcing function",
        "scoring": {
            2: "Hard deadline (CSRD Jan 2026) + vendor evaluation in progress",
            1: "Soft timeline mentioned (pledges with dates)",
            0: "No timing signals",
            -1: "Explicitly paused all evaluations"
        }
    },
    {
        "id": "deal_size_potential",
        "name": "Deal Size Potential",
        "description": "Estimated annual contract value based on company size/complexity",
        "scoring": {
            2: "Large enterprise ($5B+ revenue, 20+ facilities, multi-country) → $300K+ ACV",
            1: "Mid-market ($1-5B revenue, 5-20 facilities) → $100-300K ACV",
            0: "Small ($500M-1B, few facilities) → $50-100K ACV",
            -1: "Very small or simple operations → <$50K ACV"
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
            "max_score": 2,
            "evidence": evidence,
            "running_total": total_score,
            "tokens": estimated_tokens
        }}

    # Apply risk factor penalty — risk signals reduce the total
    risk_signals = [s for s in signals if s["category"] == "risk_factor"]
    if risk_signals:
        risk_penalty = min(len(risk_signals), 4)  # 1 point per risk signal, cap at 4
        total_score -= risk_penalty
        scores["risk_factor"] = {
            "score": -risk_penalty,
            "evidence": risk_signals[0]["quote"],
            "name": "Risk Factors"
        }
        risk_tokens = max(1, (len(risk_signals[0]["quote"]) + len("Risk Factors")) // 4)
        evaluation_metrics["dimension_tokens"] += risk_tokens
        yield {"event": "dimension_scored", "data": {
            "dimension_id": "risk_factor",
            "dimension_name": "⚠️ Risk Factors",
            "score": -risk_penalty,
            "max_score": 0,
            "evidence": risk_signals[0]["quote"],
            "running_total": total_score,
            "tokens": risk_tokens
        }}

    # Determine fit level
    if total_score >= 8:
        fit_level = "HIGH"
    elif total_score >= 4:
        fit_level = "MEDIUM"
    else:
        fit_level = "LOW"

    # Estimate ACV
    acv = _estimate_acv(company_data, total_score)

    # Stream the fit narrative
    yield {"event": "fit_determined", "data": {
        "fit_level": fit_level,
        "total_score": total_score,
        "max_possible": 12,
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
    """Score a single dimension based on available signals."""
    dim_id = dimension["id"]

    if not dim_signals:
        return 0, "No signals found"

    # Score based on signal strength
    quotes = [s["quote"] for s in dim_signals]
    best_quote = max(quotes, key=len) if quotes else ""
    combined_text = " ".join(quotes).lower()

    # Negative sentiment check — if the signal contains cost-cutting/negative language,
    # it should score negatively even if the keyword matched
    negative_indicators = ["layoff", "restructur", "cost-cutting", "spending freeze",
                          "paused", "suspended", "decline", "loss", "reduced", "cancelled",
                          "canceled", "cut ", "freeze", "discretionary spending"]
    has_negative = any(neg in combined_text for neg in negative_indicators)

    # For risk_factor dimension — negative signals score negative
    if dim_id == "risk_factor":
        # Risk factor is inverted: presence of risk = negative for fit
        # We DON'T add risk_factor to the total — instead we handle it specially
        return 0, "No risk signals"  # Risk handled via other dimensions

    # If negative language present in this dimension's signals, score down
    if has_negative:
        return -1, best_quote

    # Heuristic scoring based on signal count and content
    if len(dim_signals) >= 2:
        return 2, best_quote
    elif len(dim_signals) == 1:
        strong_indicators = ["$", "million", "billion", "hire", "appoint",
                            "deadline", "by 2026", "lack", "cannot", "commit"]
        if any(ind in best_quote.lower() for ind in strong_indicators):
            return 2, best_quote
        return 1, best_quote
    return 0, "Insufficient evidence"


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
        if dim_data["score"] >= 2:
            positives.append(f"{dim_data['name']}: {dim_data['evidence'][:80]}")
        elif dim_data["score"] < 0:
            risks.append(f"{dim_data['name']}: {dim_data['evidence'][:80]}")

    narrative = f"{company_name} shows {fit_level} fit for Proseware's sustainability platform (score: {total_score}/12). "

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
