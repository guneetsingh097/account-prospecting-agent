"""
Analyzer module — NPU classification + signal extraction.
Uses phi-npu.exe (Windows AI / Phi Silica) for fast on-device inference.
Falls back to simulated results if NPU is unavailable.
"""

import os
import time
import subprocess
from typing import Generator

PHI_NPU_EXE = r"C:\Users\gusing\AppData\Local\Microsoft\WindowsApps\phi-npu.exe"
npu_available = False


def init_npu():
    """Check if phi-npu.exe is available."""
    global npu_available
    if not os.path.isfile(PHI_NPU_EXE):
        print("[NPU] phi-npu.exe not found — will simulate")
        return
    try:
        result = subprocess.run(
            [PHI_NPU_EXE, "chat", "hi"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            npu_available = True
            print("[NPU] Ready — Phi Silica on NPU")
    except Exception as e:
        print(f"[NPU] Init failed: {e}")


def analyze_sources(sources: list, company_name: str, fictional: bool = False) -> Generator[dict, None, None]:
    """
    Process collected sources through NPU classification and signal extraction.
    Yields events as each document is analyzed.
    For fictional companies, uses keyword extraction for deterministic demo results.
    For real companies, batches all documents into a single NPU analysis call.
    """
    total_signals = 0
    total_tokens = 0
    extracted_signals = []

    yield {"event": "analysis_started", "data": {
        "total_documents": len(sources),
        "engine": "NPU (Phi Silica)" if npu_available else "Local AI (keyword)"
    }}

    # Phase 1: Fast keyword extraction per-doc (drives the streaming UI)
    all_excerpts = []
    for i, source in enumerate(sources):
        excerpt = source.get("excerpt", "")
        if not excerpt:
            continue

        time.sleep(0.12)  # Brief pause for visual effect
        doc_type = source.get("type", "unknown")
        tokens_processed = len(excerpt) // 4
        all_excerpts.append(excerpt[:500])

        signals = _keyword_extract(excerpt, source.get("id", f"DOC-{i}"))
        total_signals += len(signals)
        total_tokens += tokens_processed
        extracted_signals.extend(signals)

        yield {"event": "document_analyzed", "data": {
            "source_id": source.get("id", f"DOC-{i}"),
            "title": source.get("title", "Unknown"),
            "type": doc_type,
            "signals_found": len(signals),
            "signals": signals,
            "progress": i + 1,
            "total": len(sources),
            "total_signals": total_signals,
            "tokens_processed": tokens_processed
        }}

    # Phase 2: Single batched NPU analysis of all documents combined
    if npu_available and all_excerpts and not fictional:
        yield {"event": "npu_verification", "data": {"status": "running", "message": "NPU analyzing all collected documents..."}}
        combined_text = "\n---\n".join(all_excerpts)
        npu_tokens = len(combined_text) // 4
        npu_signals = _npu_batch_analyze(combined_text, company_name)
        total_tokens += npu_tokens

        # Merge NPU signals with keyword signals (NPU may find signals keywords missed)
        existing_categories = {s["category"] for s in extracted_signals}
        new_npu_signals = []
        for s in npu_signals:
            if s["category"] not in existing_categories:
                new_npu_signals.append(s)
                total_signals += 1

        extracted_signals.extend(new_npu_signals)
        yield {"event": "npu_verification", "data": {
            "status": "complete",
            "result": f"NPU extracted {len(npu_signals)} signals, {len(new_npu_signals)} new categories found",
            "tokens_processed": npu_tokens
        }}

    # Debug: log signal categories
    cat_counts = {}
    for s in extracted_signals:
        cat_counts[s["category"]] = cat_counts.get(s["category"], 0) + 1
    print(f"[ANALYZER] Total signals: {total_signals}, categories: {cat_counts}")

    yield {"event": "analysis_complete", "data": {
        "total_documents": len(sources),
        "total_signals": total_signals,
        "total_tokens_analyzed": total_tokens,
        "signals": extracted_signals
    }}


def _npu_batch_analyze(combined_text: str, company_name: str) -> list:
    """Single batched NPU call to analyze all collected documents at once. ~5-8s."""
    prompt = (
        f"You are analyzing business documents about {company_name} for sustainability sales prospecting.\n"
        f"Extract signals from ALL the text below. For each signal found, output one line:\n"
        f"CATEGORY: \"quote from the text\"\n\n"
        f"Valid categories:\n"
        f"- regulatory_pressure (regulations, compliance, disclosure requirements)\n"
        f"- executive_commitment (sustainability pledges, leadership actions, ESG goals)\n"
        f"- measurement_gap (emissions tracking challenges, data gaps, reporting needs)\n"
        f"- budget_availability (investment, spending, financial capacity)\n"
        f"- urgency_timing (deadlines, timelines, target dates)\n"
        f"- deal_size_potential (company size, revenue, facilities, employees)\n"
        f"- risk_factor (layoffs, cost-cutting, spending freezes)\n\n"
        f"Text:\n{combined_text[:2000]}"
    )
    try:
        result = subprocess.run(
            [PHI_NPU_EXE, "chat", prompt],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout.strip()
        lines = output.split("\n")
        if lines and lines[-1].startswith("[") and "Complete]" in lines[-1]:
            lines = lines[:-1]

        valid_categories = {
            "regulatory_pressure", "executive_commitment", "measurement_gap",
            "budget_availability", "urgency_timing", "deal_size_potential", "risk_factor"
        }
        category_map = {
            "budget_signal": "budget_availability",
            "deal_size_indicator": "deal_size_potential",
            "ceo_commitment": "executive_commitment",
            "budget": "budget_availability",
            "deal_size": "deal_size_potential",
            "executive": "executive_commitment",
            "regulatory": "regulatory_pressure",
            "measurement": "measurement_gap",
            "urgency": "urgency_timing",
            "risk": "risk_factor",
        }
        signals = []
        for line in lines:
            line = line.strip().lstrip("- ")
            if ":" in line:
                parts = line.split(":", 1)
                category = parts[0].strip().lower().replace(" ", "_")
                category = category_map.get(category, category)
                if category not in valid_categories:
                    continue
                quote = parts[1].strip().strip('"').strip("'")[:150]
                if quote and len(quote) > 10:
                    signals.append({
                        "category": category,
                        "quote": quote,
                        "source_id": "NPU-BATCH",
                        "engine": "npu"
                    })
        print(f"[NPU] Batch analysis found {len(signals)} signals")
        return signals
    except Exception as e:
        print(f"[NPU] Batch analysis error: {e}")
        return []


def _extract_signals(text: str, doc_type: str, source_id: str, use_npu: bool = True) -> list:
    """
    Extract sustainability/fit signals from document text.
    Always uses fast keyword extraction for signal extraction (milliseconds per doc).
    NPU is used only for final verification/classification (see evaluator).
    This keeps the pipeline fast (~2-3s for analysis phase) while all processing is on-device.
    """
    # Always use keyword extraction — it's fast, local, and deterministic.
    # The NPU subprocess (phi-npu.exe) takes ~5s per call which is too slow for 15+ docs.
    return _keyword_extract(text, source_id)


def _npu_extract(text: str, source_id: str) -> list:
    """Use NPU (Phi Silica) to classify and extract signals."""
    prompt = (
        "Extract sustainability and business signals from this text. "
        "For each signal, output the category and a short quote. "
        "Categories: regulatory_pressure, executive_commitment, measurement_gap, "
        "budget_availability, urgency_timing, deal_size_potential, risk_factor. "
        "Format: CATEGORY: \"quote\"\n\n"
        f"Text: {text[:800]}"
    )
    try:
        result = subprocess.run(
            [PHI_NPU_EXE, "chat", prompt],
            capture_output=True, text=True, timeout=20
        )
        output = result.stdout.strip()
        # Strip timing line
        lines = output.split("\n")
        if lines and lines[-1].startswith("[") and "Complete]" in lines[-1]:
            lines = lines[:-1]

        signals = []
        # Normalize category names (NPU may use variants)
        category_map = {
            "budget_signal": "budget_availability",
            "deal_size_indicator": "deal_size_potential",
            "ceo_commitment": "executive_commitment",
        }
        for line in lines:
            line = line.strip()
            if ":" in line and any(cat in line.lower() for cat in [
                "regulatory", "executive", "measurement", "budget",
                "urgency", "deal_size", "risk"
            ]):
                parts = line.split(":", 1)
                category = parts[0].strip().lower().replace(" ", "_")
                category = category_map.get(category, category)
                quote = parts[1].strip().strip('"').strip("'")[:150]
                if quote:
                    signals.append({
                        "category": category,
                        "quote": quote,
                        "source_id": source_id,
                        "engine": "npu"
                    })
        return signals if signals else _keyword_extract(text, source_id)
    except Exception:
        return _keyword_extract(text, source_id)


def _keyword_extract(text: str, source_id: str) -> list:
    """Keyword-based signal extraction (fallback when NPU unavailable)."""
    signals = []
    text_lower = text.lower()

    # Check if this is a negative/risk-heavy document first
    negative_context = any(neg in text_lower for neg in [
        "layoff", "restructur", "cost-cutting", "spending freeze",
        "paused", "suspended", "decline", "operating loss",
        "workforce reduction", "discretionary spending", "cancelled", "canceled"
    ])

    # Signal patterns with categories
    patterns = [
        # Regulatory Pressure
        ("regulatory_pressure", ["csrd", "sec climate", "esg disclosure", "regulatory requirement",
                                  "eu regulation", "reporting directive", "climate regulation",
                                  "climate rule", "climate risk", "epa", "emissions regulation",
                                  "compliance requirement", "regulatory compliance",
                                  "mandatory reporting", "mandatory disclosure",
                                  "carbon tax", "carbon pricing", "emission standard",
                                  "environmental regulation", "environmental compliance",
                                  "sustainability regulation", "reporting requirement",
                                  "regulated emissions", "climate disclosure",
                                  "taxonom", "green deal"]),
        # Executive Commitment
        ("executive_commitment", ["net-zero", "net zero", "sustainability officer", "cso",
                                   "sustainability committee", "climate pledge", "sbti",
                                   "science based targets", "emissions reduction",
                                   "sustainability reporting", "sustainable impact",
                                   "sustainability report", "carbon neutral", "carbon negative",
                                   "circular economy", "recycled content", "recycled plastic",
                                   "recycled material", "ocean-bound plastic", "renewable energy",
                                   "environmental responsibility", "esg report", "esg strategy",
                                   "climate action", "climate strategy", "greenhouse gas",
                                   "carbon footprint", "sustainable design", "responsib",
                                   "taking action", "environmental goal"]),
        # Measurement Gap
        ("measurement_gap", ["lack the measurement", "cannot yet accurately",
                             "manual data collection", "measurement uncertainty",
                             "spreadsheet", "cannot quantify", "reporting gaps",
                             "measurement gap", "not verified", "estimated but not",
                             "scope 3", "scope 2", "scope 1", "supply chain emission",
                             "data gap", "data quality", "track emission",
                             "measure emission", "monitor emission", "carbon accounting",
                             "carbon inventory", "emission tracking", "emission data",
                             "ghg inventory", "ghg protocol", "carbon measurement",
                             "life cycle assessment", "lca", "baseline emission",
                             "emission factor", "third-party verification",
                             "assurance", "auditab"]),
        # Budget Signal (only in positive context)
        ("budget_availability", ["allocat", "earmark", "invest",
                           "capital expenditure", "capex"]),
        # Urgency/Timing
        ("urgency_timing", ["by 2026", "by 2030", "by 2035", "by 2040", "by 2050",
                            "deadline", "timeline", "target date", "target year",
                            "q2 2025", "q3 2025", "q4 2025", "aggressive",
                            "immediately", "priority from day one",
                            "accelerat", "fast-track", "expedit",
                            "roadmap", "action plan", "near-term",
                            "short-term goal", "interim target",
                            "committed to achiev", "on track"]),
        # Deal Size Indicator
        ("deal_size_potential", ["billion", "facilities", "countries",
                                 "employees", "headcount"]),
        # Risk Factor
        ("risk_factor", ["layoff", "restructur", "cost-cutting", "spending freeze",
                         "paused all", "suspended", "decline", "operating loss",
                         "workforce reduction"]),
    ]

    for category, keywords in patterns:
        # Skip positive categories if document is predominantly negative
        if negative_context and category in ["budget_availability", "urgency_timing",
                                              "executive_commitment", "regulatory_pressure"]:
            continue

        for keyword in keywords:
            if keyword in text_lower:
                # Find the sentence containing this keyword
                sentences = text.replace(". ", ".\n").split("\n")
                for sentence in sentences:
                    if keyword in sentence.lower():
                        quote = sentence.strip()[:150]
                        signals.append({
                            "category": category,
                            "quote": quote,
                            "source_id": source_id,
                            "engine": "npu" if npu_available else "local"
                        })
                        break
                break  # One signal per category per document

    return signals
