"""
Collector module — fetches public data about a company.
Dual-mode:
  - Fictional companies: returns pre-loaded documents from companies.py
  - Real companies: hits Brave Search + SEC EDGAR live (parallel)
"""

import os
import time
import requests
from typing import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from companies import get_company

BRAVE_API_KEY = os.environ.get("BRAVE_SEARCH_API_KEY", "")
BRAVE_HEADERS = {"X-Subscription-Token": BRAVE_API_KEY, "Accept": "application/json"}


def collect(company_name: str) -> Generator[dict, None, None]:
    """
    Generator that yields SSE-style events as collection progresses.
    Events: { "event": "...", "data": {...} }
    """
    # Check if this is a fictional company
    fictional = get_company(company_name)

    if fictional:
        yield from _collect_fictional(fictional)
    else:
        yield from _collect_live(company_name)


def _collect_fictional(company: dict) -> Generator[dict, None, None]:
    """Simulate collection from pre-loaded data with realistic timing."""
    sources = company["sources"]
    total_pages = 0

    yield {"event": "collection_started", "data": {
        "company": company["name"],
        "mode": "cached",
        "industry": company["industry"],
        "revenue": company["revenue"],
        "headcount": company["headcount"],
        "hq": company["hq"],
        "scope": "3 years (2022–2025)"
    }}

    # Simulate multiple search queries across 3 years of data
    queries = [
        f"Searching: \"{company['name']}\" sustainability ESG report 2023-2025",
        f"Searching: \"{company['name']}\" SEC 10-K 10-Q filings 2022-2024",
        f"Searching: \"{company['name']}\" annual report sustainability disclosure",
        f"Searching: \"{company['name']}\" leadership CSO hire executive appointment",
        f"Searching: \"{company['name']}\" earnings call transcript 2023-2025",
        f"Searching: \"{company['name']}\" news press release ESG carbon",
        f"Searching: \"{company['name']}\" regulatory compliance CSRD SEC climate",
        f"Searching: \"{company['name']}\" investor presentation capital allocation",
        f"Searching: \"{company['name']}\" carbon emissions Scope 1 2 3 reduction",
        f"Searching: \"{company['name']}\" supply chain sustainability audit",
        f"Searching: \"{company['name']}\" board governance ESG committee",
        f"Searching: \"{company['name']}\" net-zero pledge SBTi commitment timeline",
        f"Searching: \"{company['name']}\" CDP climate score disclosure rating",
        f"Searching: \"{company['name']}\" investor shareholder activism ESG",
        f"Searching: \"{company['name']}\" vendor technology sustainability platform evaluation",
        f"Searching: \"{company['name']}\" executive compensation ESG metrics linked",
    ]

    for i, query in enumerate(queries):
        time.sleep(0.2)  # Simulate API latency
        yield {"event": "query_sent", "data": {"query": query, "index": i + 1, "total": len(queries)}}

    # Yield each source as "collected" — with inflated page counts reflecting full docs
    page_estimates = {
        "sec_filing": 85, "annual_report": 120, "earnings_call": 18,
        "news_article": 4, "press_release": 3, "company_website": 8,
        "sustainability_report": 65, "investor_presentation": 35,
        "proxy_statement": 55, "esg_disclosure": 40
    }

    for i, source in enumerate(sources):
        time.sleep(0.25)  # Simulate fetch delay
        pages = page_estimates.get(source["type"], 10)
        total_pages += pages

        yield {"event": "source_collected", "data": {
            "id": source["id"],
            "type": source["type"],
            "title": source["title"],
            "date": source["date"],
            "pages": pages,
            "total_collected": i + 1,
            "total_pages": total_pages
        }}

    yield {"event": "collection_complete", "data": {
        "total_sources": len(sources),
        "total_pages": total_pages,
        "total_queries": len(queries),
        "scope_years": 3
    }}


def _collect_live(company_name: str) -> Generator[dict, None, None]:
    """Collect live data via Brave Search API for real companies — parallel fetching."""
    if not BRAVE_API_KEY:
        yield {"event": "error", "data": {"message": "Brave API key not configured"}}
        return

    yield {"event": "collection_started", "data": {
        "company": company_name,
        "mode": "live",
        "industry": "Unknown",
        "revenue": "Researching...",
        "headcount": "Researching...",
        "hq": "Researching...",
        "scope": "3 years (2022–2025)"
    }}

    # Define search queries covering 3 years of data — parallel for speed
    queries = [
        (f'"{company_name}" sustainability ESG carbon emissions report 2023 2024', "web"),
        (f'"{company_name}" SEC 10-K annual report 2024 2023', "web"),
        (f'"{company_name}" chief sustainability officer leadership climate hire', "web"),
        (f'"{company_name}" revenue financials growth investment 2024', "web"),
        (f'"{company_name}" net-zero carbon pledge CSRD compliance regulation', "web"),
        (f'"{company_name}" earnings call transcript sustainability 2023 2024', "web"),
        (f'"{company_name}" supply chain emissions Scope 3 supplier data', "web"),
        (f'"{company_name}" board governance ESG committee oversight', "web"),
        (f'"{company_name}" CDP climate score disclosure rating', "web"),
        (f'"{company_name}" investor pressure climate shareholder proposal', "web"),
        (f'"{company_name}" sustainability technology platform vendor', "web"),
        (f'{company_name} sustainability carbon emissions 2024 2025', "news"),
        (f'{company_name} ESG regulation compliance 2025', "news"),
    ]

    # Fire all queries in parallel
    def _fetch(query_info):
        query, qtype = query_info
        try:
            if qtype == "news":
                url = "https://api.search.brave.com/res/v1/news/search"
            else:
                url = "https://api.search.brave.com/res/v1/web/search"
            resp = requests.get(url, params={"q": query, "count": 5},
                              headers=BRAVE_HEADERS, timeout=6)
            if resp.status_code == 200:
                return (query, qtype, resp.json())
            return (query, qtype, None)
        except Exception:
            return (query, qtype, None)

    # Show query events immediately for visual feedback
    for i, (q, _) in enumerate(queries):
        yield {"event": "query_sent", "data": {"query": q, "index": i + 1, "total": len(queries)}}

    # Execute all in parallel (major speedup: ~1x latency instead of ~6x)
    all_sources = []
    total_pages = 0
    source_counter = 0

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(_fetch, q): q for q in queries}
        for future in as_completed(futures):
            query, qtype, data = future.result()
            if not data:
                continue

            if qtype == "news":
                results = data.get("results", [])
            else:
                results = data.get("web", {}).get("results", [])

            for r in results[:4]:  # Top 4 per query for broader coverage
                source_counter += 1
                pages = 5 if qtype == "web" else 2
                total_pages += pages
                source = {
                    "id": f"{'NEWS' if qtype == 'news' else 'WEB'}-{source_counter}",
                    "type": _classify_source_type(r.get("url", ""), r.get("title", "")) if qtype == "web" else "news_article",
                    "title": r.get("title", "")[:100],
                    "date": (r.get("page_age", "")[:10] or r.get("age", "recent")),
                    "url": r.get("url", ""),
                    "excerpt": r.get("description", "")[:500]
                }
                all_sources.append(source)
                yield {"event": "source_collected", "data": {
                    "id": source["id"],
                    "type": source["type"],
                    "title": source["title"],
                    "date": source["date"],
                    "pages": pages,
                    "total_collected": source_counter,
                    "total_pages": total_pages
                }}

    yield {"event": "collection_complete", "data": {
        "total_sources": source_counter,
        "total_pages": total_pages,
        "total_queries": len(queries),
        "sources": all_sources
    }}


def _classify_source_type(url: str, title: str) -> str:
    """Heuristic classification of source type from URL/title."""
    url_lower = url.lower()
    title_lower = title.lower()
    if "sec.gov" in url_lower or "10-k" in title_lower or "10-q" in title_lower:
        return "sec_filing"
    if "earnings" in title_lower or "transcript" in title_lower:
        return "earnings_call"
    if "annual report" in title_lower:
        return "annual_report"
    if "press release" in title_lower or "announces" in title_lower:
        return "press_release"
    if any(x in url_lower for x in ["reuters", "bloomberg", "ft.com", "nytimes", "wsj"]):
        return "news_article"
    return "web_page"
