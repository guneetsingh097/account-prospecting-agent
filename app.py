"""
Account Prospecting Agent — On-Device Hybrid AI Demo
=====================================================
A B2B seller's personal research workbench. Type a company name,
watch the device collect public data, classify with NPU, evaluate fit
with local SLM, and surface internal signals from WorkIQ.

Three data lanes:
  🌐 Web Collection (Brave Search + SEC EDGAR) → downloaded to device
  ☁️ Internal Signals (WorkIQ / M365 Copilot) → queried from cloud
  💻 Local AI (NPU + SLM) → all inference on-device
"""

import os
import sys
import json
import time
import uuid
import threading
from pathlib import Path
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, jsonify, Response, stream_with_context

# Load env
load_dotenv(Path(__file__).parent / ".env")

# Import modules
from collector import collect
from analyzer import analyze_sources, init_npu
from evaluator import evaluate_fit, init_foundry
from workiq import query_workiq
from companies import get_company, list_companies, FICTIONAL_COMPANIES
from tickers import search_tickers

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# In-memory job store (demo scope)
jobs = {}

# In-memory upload store (demo scope — small texts only)
uploaded_docs = {}  # upload_id -> {"filename": ..., "text": ..., "created": ...}
ALLOWED_EXTENSIONS = {'.txt', '.md', '.pdf', '.csv'}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

# Prefetch cache: stores pre-collected sources keyed by company name
prefetch_cache = {}
prefetch_threads = {}

# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
print("=" * 60)
print("  Account Prospecting Assistant — Hybrid AI Demo")
print("  Proseware, Inc. | Sustainability Platform")
print("=" * 60)

init_npu()
init_foundry()

print(f"\n[READY] Fictional companies loaded: {', '.join(list_companies())}")
print(f"[READY] Brave Search API key: {'configured' if os.environ.get('BRAVE_SEARCH_API_KEY') else 'MISSING'}")
print(f"[READY] Open http://localhost:5001 in your browser\n")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/companies", methods=["GET"])
def api_companies():
    """Return list of available fictional companies for autocomplete."""
    return jsonify({"companies": list_companies()})


@app.route("/api/ticker-search", methods=["GET"])
def api_ticker_search():
    """Search public companies by name or ticker symbol for autocomplete."""
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify({"results": []})

    # Also include fictional companies in results
    fictional_matches = []
    for name in list_companies():
        if q.lower() in name.lower():
            fictional_matches.append({
                "ticker": "DEMO",
                "name": name,
                "industry": "Fictional (pre-loaded)"
            })

    ticker_results = search_tickers(q)
    return jsonify({"results": fictional_matches + ticker_results})


@app.route("/api/prefetch", methods=["POST"])
def api_prefetch():
    """
    Start prefetching data for a company in the background.
    Called when user selects from autocomplete — by the time they click Research,
    collection may already be done (Google-style predictive loading).
    """
    data = request.get_json() or {}
    company_name = data.get("company_name", "").strip()
    if not company_name:
        return jsonify({"status": "ignored"})

    # Don't prefetch fictional companies (they're instant anyway)
    if get_company(company_name):
        return jsonify({"status": "fictional", "cached": True})

    # Don't prefetch if already cached or in progress
    if company_name.lower() in prefetch_cache:
        return jsonify({"status": "cached", "sources": len(prefetch_cache[company_name.lower()])})
    if company_name.lower() in prefetch_threads:
        return jsonify({"status": "in_progress"})

    # Start background collection
    def _do_prefetch(name):
        sources = []
        try:
            for event in collect(name):
                if event["event"] == "source_collected":
                    sources.append(event["data"])
                elif event["event"] == "collection_complete":
                    if "sources" in event["data"]:
                        sources = event["data"]["sources"]
            prefetch_cache[name.lower()] = sources
        except Exception as e:
            print(f"[PREFETCH] Error for {name}: {e}")
            prefetch_cache[name.lower()] = sources
        finally:
            prefetch_threads.pop(name.lower(), None)

    t = threading.Thread(target=_do_prefetch, args=(company_name,), daemon=True)
    prefetch_threads[company_name.lower()] = t
    t.start()
    print(f"[PREFETCH] Started background collection for: {company_name}")
    return jsonify({"status": "started"})


@app.route("/api/upload-document", methods=["POST"])
def api_upload_document():
    """Upload a local document for on-device AI analysis."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported file type: {ext}. Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"}), 400

    try:
        if ext == '.pdf':
            import io
            from pypdf import PdfReader

            pdf_bytes = file.read()
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            if len(text.strip()) < 50:
                return jsonify({"error": "PDF appears to be scanned/image-based. Text-based PDFs are supported in this demo."}), 400
        elif ext in ('.txt', '.md', '.csv'):
            text = file.read().decode('utf-8', errors='replace')
        else:
            return jsonify({"error": f"Cannot process {ext} files"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to parse file: {str(e)}"}), 400

    text = text[:100000]

    upload_id = str(uuid.uuid4())[:8]
    uploaded_docs[upload_id] = {
        "filename": filename,
        "text": text,
        "pages": max(1, len(text) // 3000),
        "created": time.time()
    }

    if len(uploaded_docs) > 10:
        oldest = sorted(uploaded_docs.items(), key=lambda x: x[1]["created"])[:len(uploaded_docs) - 10]
        for k, _ in oldest:
            del uploaded_docs[k]

    return jsonify({
        "upload_id": upload_id,
        "filename": filename,
        "pages": uploaded_docs[upload_id]["pages"],
        "chars": len(text),
        "message": f"✓ {filename} parsed locally — {len(text):,} characters extracted on-device"
    })


@app.route("/api/research", methods=["POST"])
def api_research():
    """Start a research job for a company. Returns job_id for SSE stream."""
    data = request.get_json() or {}
    company_name = data.get("company_name", "").strip()
    upload_id = data.get("upload_id", "").strip()
    if not company_name:
        return jsonify({"error": "company_name required"}), 400

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "company_name": company_name,
        "upload_id": upload_id,
        "status": "created",
        "created": time.time()
    }
    return jsonify({"job_id": job_id, "company_name": company_name})


@app.route("/api/research/<job_id>/events")
def api_research_events(job_id):
    """SSE stream for a research job. Streams all phases."""
    if job_id not in jobs:
        return jsonify({"error": "job not found"}), 404

    job = jobs[job_id]
    company_name = job["company_name"]

    def generate():
        compute_metrics = {
            "total_tokens_local": 0,
            "total_tokens_cloud": 0,
            "local_inferences": 0,
            "cloud_inferences": 0,
            "documents_analyzed": 0,
            "npu_calls": 0,
            "slm_calls": 0,
            "cloud_cost_saved": 0.0,
            "local_processing_time_ms": 0,
            "equivalent_cloud_time_ms": 0,
        }

        # Phase 1: Collection
        collected_sources = []
        all_signals = []
        engagement_data = {}
        fictional = get_company(company_name)

        # Start WorkIQ in parallel — it queries cloud while we collect & analyze locally
        import queue
        workiq_queue = queue.Queue()
        def _run_workiq():
            for event in query_workiq(company_name):
                workiq_queue.put(event)
            workiq_queue.put(None)  # sentinel
        from threading import Thread
        workiq_thread = Thread(target=_run_workiq, daemon=True)
        workiq_thread.start()

        def _flush_workiq():
            """Emit any queued WorkIQ events without blocking. Returns (sse_strings, is_done)."""
            chunks = []
            done = False
            while not workiq_queue.empty():
                try:
                    event = workiq_queue.get_nowait()
                except Exception:
                    break
                if event is None:
                    done = True
                    break
                chunks.append(f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n")
                if event["event"] == "workiq_started":
                    compute_metrics["cloud_inferences"] += 1
                elif event["event"] == "workiq_complete":
                    engagement_data["score"] = event["data"].get("engagement_score", 0)
                    engagement_data["engagement_level"] = event["data"].get("engagement_level", "Minimal")
                    engagement_data["total_signals"] = event["data"].get("total_signals", 0)
                    signal_types = list({s.get("type", "").replace("_", " ") for s in event["data"].get("signals", []) if s.get("type") != "npu_insight"})
                    engagement_data["signal_types"] = signal_types
            return chunks, done

        # Check if we have prefetched data (from type-ahead predictive loading)
        prefetched = prefetch_cache.pop(company_name.lower(), None)

        if prefetched and not fictional:
            # Use prefetched data — emit events quickly to show progress
            yield f"event: collection_started\ndata: {json.dumps({'company': company_name, 'mode': 'live (prefetched)', 'scope': '2 years (2024–2026)'})}\n\n"
            num_queries = min(16, len(prefetched))
            for qi in range(num_queries):
                yield f"event: query_sent\ndata: {json.dumps({'query': f'prefetched query {qi+1}', 'index': qi+1, 'total': num_queries})}\n\n"
            total_pages = 0
            for i, src in enumerate(prefetched):
                total_pages += src.get("pages", 10)
                src["total_collected"] = i + 1
                src["total_pages"] = total_pages
                yield f"event: source_collected\ndata: {json.dumps(src)}\n\n"
                time.sleep(0.05)
            collected_sources = prefetched
            compute_metrics["cloud_inferences"] += len(prefetched)
            yield f"event: collection_complete\ndata: {json.dumps({'total_sources': len(prefetched), 'total_queries': num_queries, 'prefetched': True})}\n\n"
        else:
            # Wait for prefetch if in progress
            if company_name.lower() in prefetch_threads:
                t = prefetch_threads.get(company_name.lower())
                if t:
                    t.join(timeout=15)
                    prefetched = prefetch_cache.pop(company_name.lower(), None)
                    if prefetched:
                        yield f"event: collection_started\ndata: {json.dumps({'company': company_name, 'mode': 'live (prefetched)', 'scope': '2 years (2024–2026)'})}\n\n"
                        num_queries2 = min(16, len(prefetched))
                        for qi in range(num_queries2):
                            yield f"event: query_sent\ndata: {json.dumps({'query': f'prefetched query {qi+1}', 'index': qi+1, 'total': num_queries2})}\n\n"
                        total_pages = 0
                        for i, src in enumerate(prefetched):
                            total_pages += src.get("pages", 10)
                            src["total_collected"] = i + 1
                            src["total_pages"] = total_pages
                            yield f"event: source_collected\ndata: {json.dumps(src)}\n\n"
                            time.sleep(0.05)
                        collected_sources = prefetched
                        compute_metrics["cloud_inferences"] += len(prefetched)
                        yield f"event: collection_complete\ndata: {json.dumps({'total_sources': len(prefetched), 'total_queries': num_queries2, 'prefetched': True})}\n\n"

            # Normal collection if no prefetch available
            if not collected_sources:
                for event in collect(company_name):
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
                    if event["event"] == "query_sent" and not fictional:
                        compute_metrics["cloud_inferences"] += 1
                    elif event["event"] == "source_collected":
                        if fictional:
                            src_id = event["data"]["id"]
                            for s in fictional["sources"]:
                                if s["id"] == src_id:
                                    collected_sources.append(s)
                                    break
                        else:
                            collected_sources.append(event["data"])
                    elif event["event"] == "collection_complete":
                        if not fictional and "sources" in event["data"]:
                            collected_sources = event["data"]["sources"]
                        if not fictional and not compute_metrics["cloud_inferences"]:
                            compute_metrics["cloud_inferences"] = event["data"].get("total_queries", len(collected_sources))

        # Phase 2: NPU Analysis
        sources_to_analyze = collected_sources if collected_sources else []
        if fictional and not collected_sources:
            sources_to_analyze = fictional["sources"]

        upload_id = job.get("upload_id", "")
        if upload_id and upload_id in uploaded_docs:
            doc = uploaded_docs[upload_id]
            uploaded_source = {
                "id": "LOCAL-1",
                "type": "local_document",
                "title": f"{doc['filename']} (uploaded locally)",
                "date": "local",
                "url": None,
                "excerpt": doc["text"][:2000],
                "origin": "local_upload"
            }
            if not isinstance(sources_to_analyze, list):
                sources_to_analyze = list(sources_to_analyze)
            sources_to_analyze = list(sources_to_analyze) + [uploaded_source]
            yield f"event: local_document_added\ndata: {json.dumps({'filename': doc['filename'], 'pages': doc['pages'], 'chars': len(doc['text']), 'message': 'Local document added to analysis — processed entirely on-device'})}\n\n"

        analysis_started_at = time.perf_counter()
        workiq_done = False
        for event in analyze_sources(sources_to_analyze, company_name, fictional=bool(fictional)):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
            if event["event"] == "document_analyzed":
                compute_metrics["documents_analyzed"] += 1
                compute_metrics["local_inferences"] += 1
                compute_metrics["total_tokens_local"] += event["data"].get("tokens_processed", 0)
                # Interleave WorkIQ events during analysis
                if not workiq_done:
                    chunks, workiq_done = _flush_workiq()
                    for chunk in chunks:
                        yield chunk
            elif event["event"] == "npu_verification" and event["data"].get("status") == "complete":
                compute_metrics["npu_calls"] += 1
                compute_metrics["local_inferences"] += 1
                compute_metrics["total_tokens_local"] += event["data"].get("tokens_processed", 0)
            elif event["event"] == "analysis_complete":
                all_signals = event["data"].get("signals", [])
        compute_metrics["local_processing_time_ms"] += int((time.perf_counter() - analysis_started_at) * 1000)

        # Flush any remaining WorkIQ events (non-blocking)
        if not workiq_done:
            workiq_thread.join(timeout=0.2)
            chunks, _ = _flush_workiq()
            for chunk in chunks:
                yield chunk

        # Phase 4: SLM Fit Evaluation
        if fictional:
            company_data = {
                "name": fictional["name"],
                "industry": fictional["industry"],
                "revenue": fictional["revenue"],
                "headcount": fictional["headcount"],
                "hq": fictional["hq"],
                "facilities": fictional["facilities"]
            }
        else:
            company_data = {
                "name": company_name,
                "industry": "Unknown",
                "revenue": "Unknown",
                "headcount": "Unknown",
                "hq": "Unknown",
                "facilities": 1
            }

        evaluation_started_at = time.perf_counter()
        for event in evaluate_fit(all_signals, company_data, engagement_data=engagement_data):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
            if event["event"] == "dimension_scored":
                compute_metrics["slm_calls"] += 1
                compute_metrics["local_inferences"] += 1
                compute_metrics["total_tokens_local"] += event["data"].get("tokens", 0)
            elif event["event"] == "narrative_complete":
                evaluation_metrics = event["data"].get("evaluation_metrics", {})
                compute_metrics["total_tokens_local"] += evaluation_metrics.get("narrative_tokens_generated", 0)
                compute_metrics["total_tokens_local"] += evaluation_metrics.get("narrative_input_tokens", 0)
                if evaluation_metrics.get("narrative_call"):
                    compute_metrics["slm_calls"] += 1
                    compute_metrics["local_inferences"] += 1
        compute_metrics["local_processing_time_ms"] += int((time.perf_counter() - evaluation_started_at) * 1000)

        compute_metrics["cloud_cost_saved"] = round(compute_metrics["total_tokens_local"] * 0.000015, 4)
        compute_metrics["equivalent_cloud_time_ms"] = max(
            compute_metrics["local_processing_time_ms"],
            int(compute_metrics["total_tokens_local"] * 2.5) + (compute_metrics["cloud_inferences"] * 800)
        )

        yield f"event: metrics_summary\ndata: {json.dumps(compute_metrics)}\n\n"
        yield f"event: job_complete\ndata: {json.dumps({'job_id': job_id})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@app.route("/api/crm/push", methods=["POST"])
def api_crm_push():
    """Simulate pushing approved prospect to CRM."""
    data = request.get_json() or {}
    company = data.get("company_name", "Unknown")
    return jsonify({
        "success": True,
        "message": f"{company} added to Dynamics 365 pipeline",
        "details": {
            "opportunity_id": f"OPP-{uuid.uuid4().hex[:6].upper()}",
            "stage": "Qualification",
            "owner": "Sam Torres",
            "enrichment_attached": True
        }
    })


@app.route("/api/reanalyze", methods=["POST"])
def api_reanalyze():
    """Re-run evaluation with additional user-provided context (notes, URL content)."""
    data = request.get_json() or {}
    company_name = data.get("company_name", "").strip()
    additional_context = data.get("context", "").strip()
    context_type = data.get("context_type", "notes")  # notes, url, document

    if not company_name or not additional_context:
        return jsonify({"error": "company_name and context required"}), 400

    job_id = f"reanalyze-{uuid.uuid4().hex[:6]}"

    def generate():
        # Create a signal from the additional context
        extra_source = {
            "id": f"USER-{context_type.upper()}-1",
            "type": f"user_{context_type}",
            "title": f"User-provided {context_type}",
            "date": "local",
            "url": None,
            "excerpt": additional_context[:3000],
            "origin": "user_input"
        }

        yield f"event: reanalyze_started\ndata: {json.dumps({'message': 'Re-analyzing with additional context...', 'context_type': context_type, 'chars': len(additional_context)})}\n\n"

        # Run NPU analysis on the new context
        analysis_started_at = time.perf_counter()
        all_signals = []
        for event in analyze_sources([extra_source], company_name, fictional=False):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
            if event["event"] == "analysis_complete":
                all_signals = event["data"].get("signals", [])

        # Look up company data
        fictional = get_company(company_name)
        if fictional:
            company_data = {
                "name": fictional["name"],
                "industry": fictional["industry"],
                "revenue": fictional["revenue"],
                "headcount": fictional["headcount"],
                "hq": fictional["hq"],
                "facilities": fictional["facilities"]
            }
        else:
            company_data = {
                "name": company_name,
                "industry": "Unknown",
                "revenue": "Unknown",
                "headcount": "Unknown",
                "hq": "Unknown",
                "facilities": 1
            }

        # Re-run fit evaluation with new signals
        for event in evaluate_fit(all_signals, company_data, engagement_data={}):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

        local_ms = int((time.perf_counter() - analysis_started_at) * 1000)
        yield f"event: reanalyze_complete\ndata: {json.dumps({'message': 'Re-analysis complete', 'processing_time_ms': local_ms})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"}
    )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
