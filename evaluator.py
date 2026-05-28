"""
Evaluator module — NPU + SLM fit evaluation with streaming.
Scores each dimension using phi-npu.exe (Phi Silica) and generates an evidence-based assessment.
"""

import os
import time
import subprocess
import platform
from typing import Generator

# NPU subprocess flags (no console window on Windows)
_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0

# NPU executable (legacy fallback)
PHI_NPU_EXE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "phi-npu.exe")
npu_eval_available = os.path.exists(PHI_NPU_EXE)

# Foundry Local (OpenAI-compatible)
foundry_ok = False
client = None
model_id = None


def init_foundry():
    """Initialize evaluation engine and local SLM fallback."""
    global foundry_ok, client, model_id, npu_eval_available
    import threading

    # Use phi-npu.exe (Phi Silica) — proven to work on this hardware
    if os.path.exists(PHI_NPU_EXE):
        npu_eval_available = True
        print("[EVAL] phi-npu.exe (Phi Silica) ready for scoring")

    # Fallback to Foundry Local
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
        "description": "US federal and state government pressure to improve sustainability reporting and reduce emissions",
        "max_score": 10,
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
        "description": "CEO or executive-level public commitment to sustainability goals",
        "max_score": 10,
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
        "description": "Data or measurements they are not collecting today — gaps our software can fill",
        "max_score": 10,
        "scoring": {
            "8-10": "Explicitly stated measurement gaps + active vendor evaluation",
            "5-7": "Partial reporting, known gaps in Scope 3 or supply chain",
            "2-4": "Some measurement but unclear completeness",
            "0-1": "No mention of measurement challenges"
        }
    },
    {
        "id": "deal_size",
        "name": "Deal Size",
        "description": "Size of the company's US footprint — revenue, facilities, employees",
        "max_score": 10,
        "scoring": {
            "8-10": "Large enterprise ($5B+ revenue, 20+ facilities, multi-country) → $300K+ ACV",
            "5-7": "Mid-market ($1-5B revenue, 5-20 facilities) → $100-300K ACV",
            "2-4": "Growing company ($500M-1B) → $50-100K ACV",
            "0-1": "Small or simple operations → <$50K ACV"
        }
    },
    {
        "id": "urgency_timing",
        "name": "Urgency / Timing",
        "description": "Climate goals, pledges, or regulatory deadlines creating pressure to act now",
        "max_score": 10,
        "scoring": {
            "8-10": "Hard deadline + active vendor evaluation + board mandate",
            "5-7": "Pledges with dates, upcoming regulatory deadlines",
            "2-4": "Soft timelines or general future commitments",
            "0-1": "No timing signals"
        }
    },
    {
        "id": "internal_engagement",
        "name": "Internal Engagement",
        "description": "How engaged this account is with our sellers and marketing content (emails, webinars, meetings, downloads)",
        "max_score": 50,
        "scoring": {
            "35-50": "Multi-channel engagement: meetings booked, content consumed, Teams discussions, site visits",
            "20-34": "Moderate engagement: webinar attendance, email opens, some site activity",
            "10-19": "Light engagement: single content download or site visit",
            "0-9": "Minimal or no internal engagement signals"
        }
    }
]


def _npu_score_dimensions(signals: list, company_data: dict) -> dict:
    """Use phi-npu.exe to score all fit dimensions in a single batch call.
    Returns dict of {dim_id: {"score": int, "evidence": str}}."""
    company_name = company_data.get("name", "the company")

    # Build signal summary for prompts
    signal_summary = {}
    for s in signals:
        cat = s.get("category", "unknown")
        if cat not in signal_summary:
            signal_summary[cat] = []
        if len(signal_summary[cat]) < 3:
            signal_summary[cat].append(s.get("quote", "")[:80])

    signal_text = ""
    for cat, quotes in signal_summary.items():
        signal_text += f"{cat}: {'; '.join(quotes)}\n"

    # Use phi-npu.exe for scoring
    prompt = (
        f"Score {company_name} on sustainability platform fit. For each dimension, output: DIMENSION|SCORE|REASON\n"
        f"Score 0-10. Dimensions: regulatory_pressure, executive_commitment, measurement_gap, deal_size, urgency_timing\n\n"
        f"Signals found:\n{signal_text[:1200]}\n\n"
        f"Output one line per dimension:"
    )

    try:
        result = subprocess.run(
            [PHI_NPU_EXE, "chat", prompt],
            capture_output=True, text=True, timeout=30,
            creationflags=_SUBPROCESS_FLAGS
        )
        output = result.stdout.strip()
        lines = output.split("\n")
        if lines and lines[-1].startswith("[") and "Complete]" in lines[-1]:
            lines = lines[:-1]

        input_tokens = max(1, int(len(prompt) / 3.5))
        output_tokens = max(1, int(len(output) / 3.5))
        print(f"[NPU-EVAL] Scored dimensions: {input_tokens}+{output_tokens} tokens")

        valid_dims = {"regulatory_pressure", "executive_commitment", "measurement_gap", "deal_size", "urgency_timing"}
        dim_map = {
            "regulatory": "regulatory_pressure",
            "executive": "executive_commitment",
            "measurement": "measurement_gap",
            "deal": "deal_size",
            "urgency": "urgency_timing",
        }
        npu_scores = {}

        for line in lines:
            line = line.strip().lstrip("- ")
            parts = line.split("|")
            if len(parts) >= 3:
                dim_id = parts[0].strip().lower().replace(" ", "_")
                for prefix, full_id in dim_map.items():
                    if prefix in dim_id:
                        dim_id = full_id
                        break
                if dim_id not in valid_dims:
                    continue
                try:
                    score = int(parts[1].strip().split("/")[0].strip())
                    score = max(0, min(10, score))
                except (ValueError, IndexError):
                    continue
                reason = parts[2].strip()[:200]
                npu_scores[dim_id] = {"score": score, "evidence": reason}

        return npu_scores

    except Exception as e:
        print(f"[NPU-EVAL] Scoring error: {e}")
        return {}


def evaluate_fit(signals: list, company_data: dict, engagement_data: dict = None) -> Generator[dict, None, None]:
    """
    Evaluate company fit using collected signals.
    Yields streaming events: dimension scores, then overall assessment.
    Uses NPU scoring when available.
    Overlaps narrative generation with dimension display for speed.
    engagement_data: dict with 'score', 'level', 'signals' from WorkIQ
    """
    import threading

    engine_name = "NPU (Phi Silica)" if npu_eval_available else "Structured Evaluation"

    yield {"event": "evaluation_started", "data": {
        "dimensions": len(DIMENSIONS),
        "engine": engine_name
    }}

    # Score each dimension
    scores = {}
    total_score = 0
    max_possible = 0
    evaluation_metrics = {
        "dimension_tokens": 0,
        "narrative_tokens_generated": 0,
        "narrative_call": False,
        "total_evaluation_tokens": 0
    }

    # Use NPU to score all dimensions at once (single call for speed)
    npu_scores = {}
    if npu_eval_available and signals:
        npu_scores = _npu_score_dimensions(signals, company_data)

    # Start narrative NPU call in background (overlaps with dimension UI stagger)
    narrative_result = {"text": None, "tokens": (0, 0)}
    if npu_eval_available:
        def _bg_narrative():
            """Pre-generate narrative while dimensions display."""
            company_name = company_data.get("name", "the company")
            est_total = sum(d.get("score", 5) for d in npu_scores.values())
            est_level = "HIGH" if est_total >= 35 else "MEDIUM" if est_total >= 20 else "LOW"
            dim_summary = [f"{d.get('evidence', '')[:40]}" for d in npu_scores.values()]

            prompt = (
                f"Write 2-3 sentences about why {company_name} is a {est_level} fit for a sustainability software platform. "
                f"Key findings: {'; '.join(dim_summary[:3])}. "
                f"Be specific to {company_name}. No markdown or formatting."
            )

            try:
                result = subprocess.run(
                    [PHI_NPU_EXE, "chat", prompt],
                    capture_output=True, text=True, timeout=30,
                    creationflags=_SUBPROCESS_FLAGS
                )
                output = result.stdout.strip()
                lines = output.split("\n")
                if lines and lines[-1].startswith("[") and "Complete]" in lines[-1]:
                    lines = lines[:-1]
                text = " ".join(lines).strip()
                import re
                text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
                text = re.sub(r'\*([^*]+)\*', r'\1', text)
                text = re.sub(r'<[^>]*>', '', text)
                input_tokens = max(1, int(len(prompt) / 3.5))
                output_tokens = max(1, int(len(text) / 3.5))
                narrative_result["text"] = text
                narrative_result["tokens"] = (input_tokens, output_tokens)
            except Exception as e:
                print(f"[NPU-EVAL] BG narrative error: {e}")

        narrative_thread = threading.Thread(target=_bg_narrative, daemon=True)
        narrative_thread.start()

    for dim in DIMENSIONS:
        dim_max = dim.get("max_score", 10)
        max_possible += dim_max

        if dim["id"] == "internal_engagement":
            score, evidence = _score_internal_engagement(engagement_data)
        elif dim["id"] in npu_scores:
            score = npu_scores[dim["id"]]["score"]
            evidence = npu_scores[dim["id"]]["evidence"]
        else:
            dim_signals = [s for s in signals if s["category"] == dim["id"]]
            score, evidence = _score_dimension(dim, dim_signals, company_data)

        scores[dim["id"]] = {"score": score, "evidence": evidence, "name": dim["name"]}
        total_score += score
        estimated_tokens = max(1, (len(evidence) + len(dim["name"]) + len(dim["description"])) // 4)
        evaluation_metrics["dimension_tokens"] += estimated_tokens

        time.sleep(0.15)  # Stagger dimension reveals for visual feedback
        yield {"event": "dimension_scored", "data": {
            "dimension_id": dim["id"],
            "dimension_name": dim["name"],
            "score": score,
            "max_score": dim_max,
            "evidence": evidence,
            "running_total": total_score,
            "tokens": estimated_tokens
        }}

    # Determine fit level
    score_pct = (total_score / max_possible) * 100 if max_possible > 0 else 0
    if score_pct >= 75:
        fit_level = "HIGH"
    elif score_pct >= 45:
        fit_level = "MEDIUM"
    else:
        fit_level = "LOW"

    acv = _estimate_acv(company_data, total_score)

    yield {"event": "fit_determined", "data": {
        "fit_level": fit_level,
        "total_score": total_score,
        "max_possible": max_possible,
        "acv_estimate": acv,
        "scores": scores
    }}

    evaluation_metrics["total_evaluation_tokens"] = evaluation_metrics["dimension_tokens"]

    # Wait for background narrative (should be done by now — ran during dimension display)
    if npu_eval_available:
        narrative_thread.join(timeout=10)
        if narrative_result["text"] and len(narrative_result["text"]) >= 20:
            input_tokens, output_tokens = narrative_result["tokens"]
            evaluation_metrics["narrative_call"] = True
            evaluation_metrics["narrative_tokens_generated"] = output_tokens
            evaluation_metrics["narrative_input_tokens"] = input_tokens
            evaluation_metrics["total_evaluation_tokens"] += input_tokens + output_tokens
            yield {"event": "narrative_token", "data": {"token": narrative_result["text"], "tokens": output_tokens}}
            yield {"event": "narrative_complete", "data": {"evaluation_metrics": evaluation_metrics}}
        else:
            yield from _generate_structured_narrative(company_data, scores, fit_level, total_score, evaluation_metrics)
    elif foundry_ok:
        yield from _stream_narrative(company_data, scores, fit_level, total_score, signals, evaluation_metrics)
    else:
        yield from _generate_structured_narrative(company_data, scores, fit_level, total_score, evaluation_metrics)


def _score_internal_engagement(engagement_data: dict) -> tuple:
    """Score internal engagement 0-50 based on WorkIQ signals.
    Maps the raw engagement score (0-123 range) proportionally to 0-50."""
    if not engagement_data:
        return 0, "No internal engagement data available"

    raw_score = engagement_data.get("score", 0)
    level = engagement_data.get("engagement_level", "Minimal")
    total_sigs = engagement_data.get("total_signals", 0)
    signal_types = engagement_data.get("signal_types", [])

    # Proportional scaling: raw points (max ~123) → 0-50
    # Use 100 as effective max so typical scores map intuitively
    score = min(50, round((raw_score / 100) * 50))

    if score >= 35:
        evidence = f"{level} engagement ({total_sigs} signals) — multi-channel activity detected"
    elif score >= 20:
        evidence = f"{level} engagement ({total_sigs} signals) — moderate interest signals"
    elif score >= 10:
        evidence = f"{level} engagement ({total_sigs} signals) — early-stage interest"
    else:
        evidence = f"{level} engagement ({total_sigs} signals) — minimal activity"

    if signal_types:
        evidence += f": {', '.join(signal_types[:4])}"

    return score, evidence


def _score_dimension(dimension: dict, dim_signals: list, company_data: dict) -> tuple:
    """Score a single dimension 0-10 based on available signals."""
    dim_id = dimension["id"]
    company_name = company_data.get("name", "").lower()

    if not dim_signals:
        return 0, "No signals found"

    # Filter signals — prefer those mentioning the target company
    relevant_signals = [s for s in dim_signals if company_name and company_name.split()[0].lower() in s.get("quote", "").lower()]
    if not relevant_signals:
        relevant_signals = dim_signals  # fallback to all if none mention company

    quotes = [s["quote"] for s in relevant_signals]
    combined_text = " ".join(quotes).lower()
    num_signals = len(relevant_signals)

    # Negative sentiment check
    negative_indicators = ["layoff", "restructur", "cost-cutting", "spending freeze",
                          "paused sustainability", "suspended sustainability",
                          "cancelled program", "canceled program",
                          "discretionary spending", "abandoned"]
    has_negative = any(neg in combined_text for neg in negative_indicators)

    if dim_id == "risk_factor":
        return 0, "No risk signals"

    if has_negative and num_signals <= 2:
        return 1, "Mixed signals — some negative business context detected"

    # Quality indicators boost the score
    strong_indicators = ["$", "million", "billion", "hire", "appoint",
                        "deadline", "by 2026", "by 2027", "by 2030",
                        "commit", "pledge", "target", "goal", "invest",
                        "report", "scope 1", "scope 2", "scope 3"]
    quality_hits = sum(1 for ind in strong_indicators if ind in combined_text)

    # 0-10 scoring: signal count + quality
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

    if quality_hits >= 4:
        quality_bonus = 4
    elif quality_hits >= 2:
        quality_bonus = 3
    elif quality_hits >= 1:
        quality_bonus = 2
    else:
        quality_bonus = 0

    score = min(10, base + quality_bonus)

    # Generate human-readable evidence summary (not raw quotes)
    evidence = _summarize_evidence(dim_id, num_signals, quality_hits, score, company_data)
    return score, evidence


def _summarize_evidence(dim_id: str, num_signals: int, quality_hits: int, score: int, company_data: dict) -> str:
    """Generate a clean evidence summary instead of showing raw search quotes."""
    company_name = company_data.get("name", "This company")

    if dim_id == "regulatory_pressure":
        if score >= 8:
            return f"{num_signals} regulatory signals found — SEC climate disclosure rules, state-level mandates, and compliance deadlines creating urgency"
        elif score >= 5:
            return f"{num_signals} signals — regulatory mentions in public filings indicate growing compliance pressure"
        elif score >= 2:
            return f"{num_signals} signals — general regulatory awareness but no immediate compliance deadlines"
        return "No regulatory pressure signals detected"

    elif dim_id == "executive_commitment":
        if score >= 8:
            return f"{num_signals} signals — C-suite sustainability pledges, published goals, and dedicated leadership roles confirmed"
        elif score >= 5:
            return f"{num_signals} signals — public sustainability commitments and reporting from leadership"
        elif score >= 2:
            return f"{num_signals} signals — basic sustainability page or mentions, limited executive action"
        return "No executive commitment signals found"

    elif dim_id == "measurement_gap":
        if score >= 8:
            return f"{num_signals} signals — acknowledged gaps in emissions tracking, Scope 3 data incomplete, opportunity for platform to fill"
        elif score >= 5:
            return f"{num_signals} signals — partial emissions reporting with known gaps in supply chain or Scope 3 data"
        elif score >= 2:
            return f"{num_signals} signals — some sustainability data published but completeness unclear"
        return "No measurement gap signals found"

    elif dim_id == "deal_size":
        if score >= 8:
            return f"{num_signals} signals — large enterprise footprint with multi-billion revenue, significant facilities and workforce"
        elif score >= 5:
            return f"{num_signals} signals — mid-market presence with meaningful revenue and operational complexity"
        elif score >= 2:
            return f"{num_signals} signals — growing company with moderate US footprint"
        return "Limited company size data available"

    elif dim_id == "urgency_timing":
        if score >= 8:
            return f"{num_signals} signals — hard deadlines, published target dates, and active sustainability roadmap creating buy-now pressure"
        elif score >= 5:
            return f"{num_signals} signals — stated climate goals with specific target years (2030, 2035)"
        elif score >= 2:
            return f"{num_signals} signals — soft timelines or general future commitments noted"
        return "No urgency or timing signals found"

    return f"{num_signals} signals found across {quality_hits} quality indicators"


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


def _npu_narrative(company_data: dict, scores: dict, fit_level: str, total_score: int, evaluation_metrics: dict) -> Generator[dict, None, None]:
    """Generate fit narrative using NPU (Phi Silica)."""
    company_name = company_data.get("name", "the company")

    # Build context from scored dimensions
    dim_summary = []
    for dim_id, dim_data in scores.items():
        if dim_data["score"] > 0 and dim_id != "internal_engagement":
            dim_summary.append(f"{dim_data['name']}: {dim_data['score']}/10")

    prompt = (
        f"Write 2-3 sentences about why {company_name} is a {fit_level} fit for a sustainability software platform. "
        f"Scores: {', '.join(dim_summary)}. Total: {total_score}/100. "
        f"Be specific to {company_name}. No markdown or formatting."
    )

    try:
        yield {"event": "narrative_token", "data": {"token": "", "status": "thinking"}}
        result = subprocess.run(
            [PHI_NPU_EXE, "chat", prompt],
            capture_output=True, text=True, timeout=30,
            creationflags=_SUBPROCESS_FLAGS
        )
        output = result.stdout.strip()
        # Strip timing line
        lines = output.split("\n")
        if lines and lines[-1].startswith("[") and "Complete]" in lines[-1]:
            lines = lines[:-1]
        narrative = " ".join(lines).strip()

        if not narrative or len(narrative) < 20:
            # Fallback to structured
            yield from _generate_structured_narrative(company_data, scores, fit_level, total_score, evaluation_metrics)
            return

        # Strip any markdown formatting NPU might add
        import re
        narrative = re.sub(r'\*\*([^*]+)\*\*', r'\1', narrative)
        narrative = re.sub(r'\*([^*]+)\*', r'\1', narrative)
        narrative = re.sub(r'<[^>]*>', '', narrative)

        input_tokens = max(1, int(len(prompt) / 3.5))
        output_tokens = max(1, int(len(narrative) / 3.5))

        evaluation_metrics["narrative_call"] = True
        evaluation_metrics["narrative_tokens_generated"] = output_tokens
        evaluation_metrics["narrative_input_tokens"] = input_tokens
        evaluation_metrics["total_evaluation_tokens"] = evaluation_metrics["dimension_tokens"] + input_tokens + output_tokens

        yield {"event": "narrative_token", "data": {"token": narrative, "tokens": output_tokens}}
        yield {"event": "narrative_complete", "data": {"evaluation_metrics": evaluation_metrics}}
        print(f"[NPU-EVAL] Narrative: {input_tokens}+{output_tokens} tokens")

    except Exception as e:
        print(f"[NPU-EVAL] Narrative error: {e}")
        yield from _generate_structured_narrative(company_data, scores, fit_level, total_score, evaluation_metrics)


def _stream_narrative(company_data: dict, scores: dict, fit_level: str, total_score: int, signals: list, evaluation_metrics: dict) -> Generator[dict, None, None]:
    """Stream fit narrative using Foundry Local SLM."""
    company_name = company_data.get("name", "the company")

    # Build compact context — top 3 scoring dimensions only, capped evidence
    scored_dims = [(d, s) for d, s in scores.items() if s["score"] > 0]
    scored_dims.sort(key=lambda x: x[1]["score"], reverse=True)
    evidence_text = ""
    for dim_id, dim_data in scored_dims[:3]:
        evidence_text += f"- {dim_data['name']}: {dim_data['evidence'][:100]}\n"

    prompt = (
        f"You are a B2B sales analyst. Write 2-3 sentences on why {company_name} is a {fit_level} fit "
        f"for a sustainability platform. Score: {total_score}. Be specific.\n\n"
        f"Evidence:\n{evidence_text}\n"
        f"Summary:"
    )

    try:
        evaluation_metrics["narrative_call"] = True
        yield {"event": "narrative_token", "data": {"token": "", "status": "thinking"}}
        stream = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            stream=True
        )
        output_tokens = 0
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                output_tokens += 1
                yield {"event": "narrative_token", "data": {"token": token, "tokens": 1}}

        input_tokens = max(1, int(len(prompt) / 3.5))
        evaluation_metrics["narrative_tokens_generated"] = output_tokens
        evaluation_metrics["narrative_input_tokens"] = input_tokens
        evaluation_metrics["total_evaluation_tokens"] = evaluation_metrics["dimension_tokens"] + input_tokens + output_tokens
        yield {"event": "narrative_complete", "data": {"evaluation_metrics": evaluation_metrics}}

    except Exception as e:
        print(f"[SLM] Stream error: {e}")
        yield from _generate_structured_narrative(company_data, scores, fit_level, total_score, evaluation_metrics)


def _generate_structured_narrative(company_data: dict, scores: dict, fit_level: str, total_score: int, evaluation_metrics: dict) -> Generator[dict, None, None]:
    """Generate a clean narrative without SLM (structured fallback)."""
    company_name = company_data.get("name", "This company")

    # Identify top scoring dimensions (excluding internal_engagement for cleaner output)
    scored_dims = []
    for dim_id, dim_data in scores.items():
        if dim_id == "internal_engagement":
            continue
        if dim_data["score"] >= 5:
            scored_dims.append(dim_data)
    scored_dims.sort(key=lambda x: x["score"], reverse=True)

    # Build clean narrative
    max_possible = sum(d.get("max_score", 10) for d in DIMENSIONS)

    if fit_level == "HIGH":
        narrative = f"{company_name} is a strong fit for Proseware's sustainability platform. "
        if len(scored_dims) >= 2:
            narrative += f"Strong signals across {scored_dims[0]['name'].lower()} and {scored_dims[1]['name'].lower()} indicate active need and budget alignment. "
        narrative += "Multiple buying signals confirmed — recommend immediate outreach with a tailored sustainability ROI analysis."
    elif fit_level == "MEDIUM":
        narrative = f"{company_name} shows moderate fit for Proseware's platform. "
        if scored_dims:
            narrative += f"Positive signals in {scored_dims[0]['name'].lower()}, but not all dimensions are confirmed. "
        narrative += "Worth monitoring — consider nurture-track outreach and alert on regulatory trigger events."
    else:
        narrative = f"{company_name} shows limited fit at this time. "
        narrative += "Insufficient buying signals across key dimensions. Revisit if regulatory pressure increases or leadership changes occur."

    # Emit narrative all at once — fast and clean
    words = narrative.split(" ")
    output_tokens = len(words)
    yield {"event": "narrative_token", "data": {"token": narrative, "tokens": output_tokens}}

    evaluation_metrics["narrative_tokens_generated"] = output_tokens
    evaluation_metrics["total_evaluation_tokens"] = evaluation_metrics["dimension_tokens"] + output_tokens
    yield {"event": "narrative_complete", "data": {"evaluation_metrics": evaluation_metrics}}
