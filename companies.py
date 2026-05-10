"""
Pre-loaded fictional company data for reliable demo mode.
Each company has curated source documents (excerpts) that the AI pipeline processes live.
For real companies, the collector fetches live data instead.
"""

FICTIONAL_COMPANIES = {
    "adatum corporation": {
        "name": "Adatum Corporation",
        "industry": "Technology / Manufacturing",
        "revenue": "$4.2B",
        "headcount": "18,000",
        "hq": "Portland, OR",
        "country_code": "us",
        "facilities": 12,
        "description": "Global technology manufacturer specializing in industrial IoT sensors and smart building systems.",
        "sources": [
            {
                "id": "WEB-1",
                "type": "annual_report",
                "title": "Adatum Corporation 2024 Annual Report",
                "date": "2024-03-15",
                "url": "https://investors.adatum.com/annual-report-2024",
                "excerpt": "We are committing to net-zero emissions by 2030. Today we lack the measurement infrastructure to track progress against this goal. Our manufacturing operations across 12 facilities generated an estimated 340,000 metric tons of CO2 equivalent last year, but we acknowledge significant gaps in our Scope 3 reporting. The Board has authorized management to evaluate technology solutions for comprehensive emissions tracking and reporting."
            },
            {
                "id": "WEB-2",
                "type": "press_release",
                "title": "Adatum Appoints Chief Sustainability Officer",
                "date": "2025-02-10",
                "url": "https://news.adatum.com/2025/02/cso-appointment",
                "excerpt": "Adatum Corporation today announced the appointment of Maria Rodriguez as Chief Sustainability Officer, reporting directly to CEO James Chen. Rodriguez joins from the EPA where she led industrial emissions policy. 'Maria's expertise in environmental measurement and regulatory compliance will be critical as we build our sustainability infrastructure,' said Chen."
            },
            {
                "id": "WEB-3",
                "type": "news_article",
                "title": "Adatum Opens Third Manufacturing Facility in Oregon",
                "date": "2025-01-22",
                "url": "https://bizjournals.com/portland/adatum-expansion-2025",
                "excerpt": "Adatum Corporation broke ground on its third Oregon manufacturing facility, a 400,000 sq ft complex in Hillsboro that will employ 2,000 workers. The $180M investment represents Adatum's largest single capital expenditure. Environmental groups have called on the company to disclose emissions projections for the new facility. CEO James Chen said sustainability reporting for the new site 'will be a priority from day one.'"
            },
            {
                "id": "WEB-4",
                "type": "news_article",
                "title": "Industrial Manufacturers Face CSRD Deadline Pressure",
                "date": "2025-03-05",
                "url": "https://esgtoday.com/csrd-manufacturers-2025",
                "excerpt": "Technology manufacturers with EU operations face mounting pressure as CSRD reporting deadlines approach. Adatum Corporation, which derives 35% of revenue from European markets, is among those expected to need significant reporting infrastructure upgrades. Analysts estimate compliance costs of $2-5M annually for companies of Adatum's size without automated tracking systems."
            },
            {
                "id": "WEB-5",
                "type": "earnings_call",
                "title": "Adatum Q4 2024 Earnings Call Transcript",
                "date": "2024-12-14",
                "url": "https://seekingalpha.com/adatum-q4-2024",
                "excerpt": "Analyst: Can you quantify the sustainability reporting investment planned for FY25? Chen: We've earmarked $15-20M for sustainability infrastructure over the next 18 months. That includes measurement technology, third-party auditing, and headcount. We're evaluating three platform vendors currently. Rodriguez starts in February and will own that decision. We need to be ready for CSRD by January 2026."
            },
            {
                "id": "WEB-6",
                "type": "sec_filing",
                "title": "Adatum Corporation 10-K FY2024",
                "date": "2024-08-15",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=adatum",
                "excerpt": "Risk Factors: The Company faces increasing regulatory requirements related to environmental, social, and governance disclosures. The European Corporate Sustainability Reporting Directive (CSRD) will require detailed emissions reporting beginning January 2026 for our EU operations. Failure to comply may result in fines of up to 5% of EU revenue. We have not yet implemented automated emissions measurement systems across our manufacturing operations."
            },
            {
                "id": "SEC-1",
                "type": "sec_filing",
                "title": "Adatum 10-K — Financial Summary",
                "date": "2024-08-15",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=adatum",
                "excerpt": "Total revenue for fiscal year 2024 was $4.2 billion, an increase of 18% year-over-year. Operating income grew 22% to $890 million. The Company maintains strong free cash flow of $1.1B. Capital expenditure plans for FY2025 include $180M for the Hillsboro facility and $15-20M for sustainability and compliance infrastructure."
            },
            {
                "id": "WEB-7",
                "type": "press_release",
                "title": "Adatum Joins Science Based Targets Initiative",
                "date": "2024-11-08",
                "url": "https://news.adatum.com/2024/11/sbti-commitment",
                "excerpt": "Adatum Corporation today announced its commitment to the Science Based Targets initiative (SBTi), pledging to set near-term emission reduction targets aligned with limiting global warming to 1.5°C. 'This commitment requires rigorous measurement and transparent reporting,' said incoming CSO Maria Rodriguez. 'We are building the data infrastructure to back these pledges with verifiable numbers.'"
            },
            {
                "id": "SEC-2",
                "type": "sec_filing",
                "title": "Adatum 10-K FY2023 — Environmental Risk Factors",
                "date": "2023-08-12",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=adatum&year=2023",
                "excerpt": "The Company currently has limited capability to quantify emissions across its supply chain. As regulatory requirements evolve, management anticipates significant investment will be required to build measurement and disclosure infrastructure. European operations represented 35% of revenue in FY2023."
            },
            {
                "id": "WEB-8",
                "type": "sustainability_report",
                "title": "Adatum 2023 Sustainability Report",
                "date": "2023-06-01",
                "url": "https://adatum.com/sustainability/report-2023",
                "excerpt": "We are early in our sustainability journey. Scope 1 emissions from our 10 manufacturing facilities totaled approximately 290,000 tCO2e in 2022. Scope 2 data is partially available. Scope 3 remains unquantified due to the complexity of our 1,800-supplier global supply chain. We acknowledge this gap and are evaluating technology solutions to improve our environmental data quality."
            },
            {
                "id": "WEB-9",
                "type": "earnings_call",
                "title": "Adatum Q2 2023 Earnings Call Transcript",
                "date": "2023-06-20",
                "url": "https://seekingalpha.com/adatum-q2-2023",
                "excerpt": "Chen: We're seeing increasing investor questions about our ESG posture. Revenue grew 14% in Q2 to $980M. We recognize the need to invest in sustainability infrastructure but want to be thoughtful about vendor selection. This is a multi-year journey. We'll have more to share by year-end."
            },
            {
                "id": "WEB-10",
                "type": "news_article",
                "title": "Adatum Named to 'ESG Laggards' Watchlist by MSCI",
                "date": "2023-09-15",
                "url": "https://esgtoday.com/adatum-msci-downgrade-2023",
                "excerpt": "MSCI downgraded Adatum Corporation's ESG rating from BBB to BB, citing lack of emissions measurement infrastructure and absence of a dedicated sustainability leadership role. Adatum responded that it is 'actively developing a comprehensive sustainability strategy' and expects to announce concrete initiatives in early 2024."
            },
            {
                "id": "WEB-11",
                "type": "investor_presentation",
                "title": "Adatum Capital Markets Day 2024 — Sustainability Strategy",
                "date": "2024-05-10",
                "url": "https://investors.adatum.com/cmd-2024",
                "excerpt": "Sustainability investment roadmap: FY2024 $5M (planning & assessment), FY2025 $15-20M (platform deployment & measurement), FY2026 $8M (optimization & reporting). Target: full Scope 1-3 automated reporting by Q3 2026. Estimated annual recurring cost of compliance: $3-4M post-implementation."
            },
            {
                "id": "SEC-3",
                "type": "proxy_statement",
                "title": "Adatum 2024 Proxy Statement — Board ESG Oversight",
                "date": "2024-04-01",
                "url": "https://sec.gov/adatum-proxy-2024",
                "excerpt": "The Board established an ESG Oversight Committee in Q1 2024, chaired by Director Sarah Kim (former EPA Deputy Administrator). The committee meets quarterly and oversees management's sustainability strategy, including vendor evaluation for emissions measurement technology. Director compensation now includes ESG metric targets beginning FY2025."
            },
            {
                "id": "WEB-12",
                "type": "news_article",
                "title": "Adatum Supply Chain Audit Reveals Emissions Gaps",
                "date": "2024-09-20",
                "url": "https://supplychaindive.com/adatum-audit-2024",
                "excerpt": "An independent audit of Adatum Corporation's supply chain found that 60% of tier-1 suppliers lack emissions measurement capabilities. The report recommended Adatum invest in supply chain engagement technology to collect primary data from suppliers. CFO noted: 'This audit confirms what we suspected — our Scope 3 numbers are essentially guesswork without proper technology infrastructure.'"
            },
            {
                "id": "WEB-13",
                "type": "news_article",
                "title": "Adatum Faces Investor Pressure on Climate Disclosure Quality",
                "date": "2024-07-15",
                "url": "https://bloomberg.com/adatum-investor-pressure-2024",
                "excerpt": "A coalition of institutional investors managing $2.8 trillion in assets sent a letter to Adatum's board demanding 'material improvement' in climate disclosure quality. The letter cited Adatum's reliance on estimated emissions data and called for third-party verified reporting by 2026. Adatum responded that investment in measurement technology is 'a top priority for FY2025.'"
            },
            {
                "id": "WEB-14",
                "type": "news_article",
                "title": "Adatum CEO: 'Sustainability Tech is Our #1 Infrastructure Priority'",
                "date": "2025-03-25",
                "url": "https://techcrunch.com/adatum-ceo-sustainability-tech-2025",
                "excerpt": "In a keynote at the Global Manufacturing Summit, Adatum CEO James Chen declared sustainability measurement technology the company's 'number one infrastructure investment priority for 2025.' Chen revealed the company has narrowed its vendor shortlist to two platforms and expects to sign by end of Q2. 'We cannot credibly claim leadership without the data to prove it.'"
            },
            {
                "id": "WEB-15",
                "type": "esg_disclosure",
                "title": "Adatum CDP Climate Questionnaire Response 2024",
                "date": "2024-08-30",
                "url": "https://cdp.net/responses/adatum-2024",
                "excerpt": "Adatum received a CDP score of C (Awareness) for climate disclosure, down from B- in 2023. The scoring noted: 'Company demonstrates awareness of climate risks but lacks comprehensive measurement systems. Governance structures are in place but data quality remains a significant gap.' Adatum flagged this as a priority improvement area."
            },
            {
                "id": "SEC-4",
                "type": "sec_filing",
                "title": "Adatum Proxy Statement 2025 — Executive Compensation ESG Metrics",
                "date": "2025-03-01",
                "url": "https://sec.gov/adatum-proxy-2025",
                "excerpt": "Beginning FY2025, 15% of executive variable compensation will be tied to sustainability metrics including: (1) deployment of emissions measurement technology, (2) Scope 1+2 verification achievement, and (3) CDP score improvement. The Board believes linking compensation to measurable environmental outcomes will accelerate the Company's sustainability infrastructure buildout."
            }
        ],
        "workiq_signals": {
            "ebook_download": {"title": "Downloaded: 'Manufacturing Emissions Tracking Guide'", "date": "2025-03-20", "contact": "Lisa Park, VP Operations"},
            "webinar": {"title": "Attended: 'CSRD Compliance for Manufacturers' webinar", "date": "2025-02-28", "contact": "Maria Rodriguez, CSO"},
            "meeting": {"title": "Discovery call with Maria Rodriguez scheduled", "date": "2025-04-15", "source": "Outlook Calendar"},
            "crm_note": None
        },
        "expected_fit": "HIGH",
        "expected_score": 10,
        "expected_acv": "$180K - $350K"
    },

    "fabrikam, inc.": {
        "name": "Fabrikam, Inc.",
        "industry": "Manufacturing / Industrial",
        "revenue": "$7.8B",
        "headcount": "32,000",
        "hq": "Chicago, IL",
        "country_code": "us",
        "facilities": 24,
        "description": "Diversified manufacturer of industrial equipment and precision components with operations in 14 countries.",
        "sources": [
            {
                "id": "WEB-1",
                "type": "sec_filing",
                "title": "Fabrikam Inc. 10-K FY2024",
                "date": "2024-09-30",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=fabrikam",
                "excerpt": "The Company faces increasing regulatory requirements around ESG disclosure, particularly as we expand operations into European markets subject to the Corporate Sustainability Reporting Directive (CSRD). Management estimates compliance infrastructure investment of $30-50M over 24 months. Current emissions reporting relies on manual data collection from facility managers, which auditors have noted introduces material measurement uncertainty."
            },
            {
                "id": "WEB-2",
                "type": "news_article",
                "title": "Fabrikam Board Establishes Sustainability Committee",
                "date": "2025-01-18",
                "url": "https://reuters.com/fabrikam-sustainability-committee-2025",
                "excerpt": "Fabrikam Inc.'s board of directors voted unanimously to establish a Sustainability and Governance Committee, allocating $25M for initial compliance initiatives. Board Chair Thomas Wright said: 'Our EU expansion timeline requires CSRD-ready reporting by January 2026. This is not optional — it is a market access requirement.' The committee will oversee vendor selection for emissions tracking technology."
            },
            {
                "id": "WEB-3",
                "type": "news_article",
                "title": "Fabrikam Accelerates EU Expansion with Frankfurt Hub",
                "date": "2025-03-01",
                "url": "https://ft.com/fabrikam-frankfurt-expansion",
                "excerpt": "Fabrikam Inc. announced a €200M investment in a new European operations hub in Frankfurt, targeting Q3 2025 opening. The facility will serve as the company's EMEA headquarters and primary manufacturing site for the European market. Compliance with EU sustainability regulations was cited as a key planning factor."
            },
            {
                "id": "WEB-4",
                "type": "earnings_call",
                "title": "Fabrikam Q3 2024 Earnings Call",
                "date": "2024-11-10",
                "url": "https://seekingalpha.com/fabrikam-q3-2024",
                "excerpt": "CFO: We're allocating significant capital to compliance infrastructure for EU expansion. We cannot access the European market without CSRD-compliant reporting. Our current manual processes won't scale — we're actively evaluating automated platforms. Timeline is aggressive: vendor selection by Q2, implementation by Q4, operational by Jan 2026."
            },
            {
                "id": "WEB-5",
                "type": "press_release",
                "title": "Fabrikam Commits to 50% Emissions Reduction by 2030",
                "date": "2024-10-20",
                "url": "https://news.fabrikam.com/2024/10/climate-pledge",
                "excerpt": "Fabrikam Inc. today announced a commitment to reduce absolute Scope 1 and Scope 2 emissions by 50% by 2030 from a 2022 baseline. CEO Patricia Fernandez: 'This pledge requires measurement capabilities we don't fully have today. We will invest in the technology and talent needed to track, verify, and reduce our carbon footprint across all 24 facilities and our extended supply chain.'"
            },
            {
                "id": "SEC-1",
                "type": "sec_filing",
                "title": "Fabrikam 10-K — Financial Highlights",
                "date": "2024-09-30",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=fabrikam",
                "excerpt": "Revenue: $7.8B (+12% YoY). Operating income: $1.4B. Free cash flow: $2.1B. European operations contributed 28% of revenue and growing. Capital budget for FY2025: $800M including $200M EU expansion and $30-50M sustainability compliance. Headcount: 32,000 across 14 countries, 24 manufacturing facilities."
            },
            {
                "id": "SEC-2",
                "type": "sec_filing",
                "title": "Fabrikam 10-K FY2023 — Operations Risk",
                "date": "2023-09-30",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=fabrikam&year=2023",
                "excerpt": "The Company's European operations are subject to evolving sustainability disclosure regulations. Management has identified CSRD compliance as a critical enabler of planned EU market expansion. Current environmental reporting processes are manual, facility-by-facility, and have been flagged by external auditors as insufficient for regulatory-grade disclosure."
            },
            {
                "id": "WEB-6",
                "type": "sustainability_report",
                "title": "Fabrikam 2023 ESG Report",
                "date": "2023-07-15",
                "url": "https://fabrikam.com/esg/report-2023",
                "excerpt": "Fabrikam's Scope 1 and 2 emissions totaled 1.2M tCO2e across 22 facilities (2022 data). Scope 3 supply chain emissions remain estimated at 4.8M tCO2e based on spend analysis rather than primary data. We acknowledge the need for technology-driven measurement improvements to achieve the accuracy required by upcoming regulations."
            },
            {
                "id": "WEB-7",
                "type": "earnings_call",
                "title": "Fabrikam Q1 2024 Earnings Call Transcript",
                "date": "2024-02-10",
                "url": "https://seekingalpha.com/fabrikam-q1-2024",
                "excerpt": "Fernandez: European revenue grew 18% and now represents our fastest-growing region. We're accelerating compliance infrastructure investment because CSRD reporting is a gate to market access. We expect to select a sustainability platform vendor by mid-2025. Budget is approved and ring-fenced."
            },
            {
                "id": "WEB-8",
                "type": "news_article",
                "title": "Fabrikam Among Manufacturers Racing to Meet EU Green Rules",
                "date": "2024-06-20",
                "url": "https://reuters.com/fabrikam-csrd-preparation-2024",
                "excerpt": "A dozen major U.S. manufacturers including Fabrikam Inc. are investing heavily in sustainability reporting technology as EU CSRD deadlines approach. Industry sources say Fabrikam has shortlisted three enterprise carbon accounting platforms and expects to begin implementation in early 2025."
            },
            {
                "id": "WEB-9",
                "type": "investor_presentation",
                "title": "Fabrikam Investor Day 2023 — Growth Strategy",
                "date": "2023-11-15",
                "url": "https://investors.fabrikam.com/investor-day-2023",
                "excerpt": "5-year European expansion plan: double EU revenue contribution from 22% to 44% by 2028. Sustainability compliance identified as 'table stakes' for European market access. Initial compliance budget: $30M FY2024-2025. Long-term sustainability operating cost: $5-8M annually once implemented."
            },
            {
                "id": "WEB-10",
                "type": "news_article",
                "title": "Fabrikam's EU Suppliers Demand Emissions Data Sharing",
                "date": "2025-02-20",
                "url": "https://supplychaindive.com/fabrikam-eu-suppliers-2025",
                "excerpt": "Fabrikam's major European customers have begun requiring emissions intensity data for all supplied components. BMW, Siemens, and Schneider Electric have issued formal data requests to Fabrikam under their Scope 3 programs. Fabrikam's VP Supply Chain noted: 'We need automated systems to respond to these requests at scale — manual reporting is unsustainable.'"
            },
            {
                "id": "WEB-11",
                "type": "news_article",
                "title": "Fabrikam Hires Chief Data Officer to Lead Sustainability Analytics",
                "date": "2025-01-05",
                "url": "https://reuters.com/fabrikam-cdo-hire-2025",
                "excerpt": "Fabrikam appointed Dr. Amanda Liu as Chief Data Officer, tasked with building the company's environmental data infrastructure. Liu previously led climate analytics at a Big Four firm. 'Our sustainability ambitions require world-class data pipelines,' said CEO Fernandez. 'Amanda will architect the measurement systems we need for CSRD and beyond.'"
            },
            {
                "id": "WEB-12",
                "type": "esg_disclosure",
                "title": "Fabrikam CDP Climate Response 2024",
                "date": "2024-09-15",
                "url": "https://cdp.net/responses/fabrikam-2024",
                "excerpt": "Fabrikam received a CDP score of B- (Management), noting: 'Company has strong governance and targets but measurement infrastructure is underdeveloped for scope and complexity of operations. Recommends investment in automated data collection and third-party verification processes.' Score decreased from B due to EU operations scale increase without corresponding reporting capabilities."
            },
            {
                "id": "SEC-3",
                "type": "proxy_statement",
                "title": "Fabrikam 2024 Proxy — Board Sustainability Oversight",
                "date": "2024-04-15",
                "url": "https://sec.gov/fabrikam-proxy-2024",
                "excerpt": "The Board's Sustainability Committee met 8 times in FY2024, reviewing vendor proposals for emissions measurement technology. Committee Chair Dr. Elena Voss reported: 'Management has presented three finalist platforms for full-enterprise deployment. We expect vendor selection by Q2 2025 with implementation beginning immediately thereafter. Budget of $30-50M is pre-approved.'"
            },
            {
                "id": "WEB-13",
                "type": "investor_presentation",
                "title": "Fabrikam ESG Roadshow — Sustainability Infrastructure Plan",
                "date": "2024-12-01",
                "url": "https://investors.fabrikam.com/esg-roadshow-2024",
                "excerpt": "Investor presentation outlining $30-50M sustainability infrastructure investment: Phase 1 (Q1-Q2 2025): Vendor selection and pilot at 3 facilities. Phase 2 (Q3-Q4 2025): Full deployment across 24 facilities. Phase 3 (2026): Supply chain integration and CSRD-compliant reporting. Expected annual operational savings from automation: $5-8M vs. manual processes. ROI positive within 18 months."
            }
        ],
        "workiq_signals": {
            "ebook_download": {"title": "Downloaded: 'CSRD Compliance Playbook for Manufacturers'", "date": "2025-01-25", "contact": "Robert Kim, Director of Compliance"},
            "webinar": None,
            "meeting": None,
            "crm_note": {"title": "Fabrikam mentioned in industry report as 'actively evaluating' platforms", "date": "2025-02-15", "source": "Marketing Intel"}
        },
        "expected_fit": "HIGH",
        "expected_score": 9,
        "expected_acv": "$350K - $750K"
    },

    "trey research": {
        "name": "Trey Research",
        "industry": "Professional Services / Consulting",
        "revenue": "$1.8B",
        "headcount": "9,500",
        "hq": "San Francisco, CA",
        "country_code": "us",
        "facilities": 4,
        "description": "Management consulting and research firm specializing in digital transformation advisory.",
        "sources": [
            {
                "id": "WEB-1",
                "type": "press_release",
                "title": "Trey Research Announces Strategic Restructuring",
                "date": "2025-02-01",
                "url": "https://news.treyresearch.com/2025/02/restructuring",
                "excerpt": "Trey Research today announced a strategic restructuring that will reduce its global workforce by approximately 12%, or 1,140 positions. CEO David Park stated: 'Market conditions require us to prioritize operational efficiency and focus on our core consulting practices. We are pausing investment in non-core initiatives to preserve capital and return to profitability by Q4.'"
            },
            {
                "id": "WEB-2",
                "type": "sec_filing",
                "title": "Trey Research 10-K FY2024",
                "date": "2024-07-30",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=trey",
                "excerpt": "Management is focused on cost optimization and operational efficiency in the current fiscal year. The Company has implemented a discretionary spending freeze across all business units. Capital expenditure has been reduced by 40% from prior year levels. All new vendor evaluations have been suspended pending completion of the strategic review expected in Q3 2025."
            },
            {
                "id": "WEB-3",
                "type": "news_article",
                "title": "Trey Research Pauses All Discretionary Spending",
                "date": "2025-02-15",
                "url": "https://consultancy.com/trey-research-spending-freeze-2025",
                "excerpt": "Following its restructuring announcement, Trey Research has implemented a company-wide discretionary spending freeze. Sources familiar with the matter say the firm has cancelled or delayed over $50M in planned technology investments. 'Nothing new is being purchased unless it directly relates to keeping the lights on,' said one senior partner who requested anonymity."
            },
            {
                "id": "WEB-4",
                "type": "news_article",
                "title": "Trey Research Reports Revenue Decline in Q1",
                "date": "2025-04-10",
                "url": "https://ft.com/trey-research-q1-decline",
                "excerpt": "Trey Research reported Q1 revenue of $380M, down 15% year-over-year, as clients delayed consulting engagements amid economic uncertainty. The firm's sustainability practice, which had been a growth area, was among the units affected by the restructuring. Two of three sustainability partners departed in March."
            },
            {
                "id": "SEC-1",
                "type": "sec_filing",
                "title": "Trey Research 10-K — Financial Summary",
                "date": "2024-07-30",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=trey",
                "excerpt": "Revenue: $1.8B (-8% YoY). Operating loss: $(45M). Free cash flow: $120M (down from $380M). Headcount reduced from 10,800 to 9,500. Office footprint reduced from 6 to 4 locations. R&D budget cut 35%. All discretionary programs under review."
            },
            {
                "id": "SEC-2",
                "type": "sec_filing",
                "title": "Trey Research 10-K FY2023",
                "date": "2023-07-30",
                "url": "https://sec.gov/cgi-bin/browse-edgar?action=getcompany&company=trey&year=2023",
                "excerpt": "Revenue: $1.96B (+4% YoY). Operating income: $180M. The Company made strategic investments in sustainability advisory services, hiring 3 senior partners to build the practice. Technology spend: $85M. Outlook positive for continued growth in ESG consulting services. No material regulatory compliance obligations."
            },
            {
                "id": "WEB-5",
                "type": "news_article",
                "title": "Trey Research's Sustainability Practice Faces Uncertain Future",
                "date": "2025-03-20",
                "url": "https://consultancy.com/trey-sustainability-practice-2025",
                "excerpt": "The sustainability advisory team at Trey Research has been decimated by the restructuring. Of 45 consultants in the practice, only 12 remain. Sources say the firm is considering shutting down the practice entirely. Remaining clients have been offered transition to other consulting firms."
            },
            {
                "id": "WEB-6",
                "type": "earnings_call",
                "title": "Trey Research Q3 2024 Earnings Call",
                "date": "2024-04-15",
                "url": "https://seekingalpha.com/trey-q3-2024",
                "excerpt": "Park: We're seeing softness across all practice areas. The pipeline has weakened. We're taking a hard look at cost structure and will announce actions before year-end. On sustainability: it's a good practice but not core to our strategy. We need to focus on what clients will pay for today, not in three years."
            },
            {
                "id": "WEB-7",
                "type": "news_article",
                "title": "Trey Research Credit Rating Downgraded to BBB-",
                "date": "2025-01-10",
                "url": "https://reuters.com/trey-research-downgrade-2025",
                "excerpt": "Moody's downgraded Trey Research's credit rating from A- to BBB-, citing declining revenue, operating losses, and uncertain path to profitability. The downgrade increases borrowing costs and may limit the firm's ability to invest in new capabilities."
            },
            {
                "id": "WEB-8",
                "type": "news_article",
                "title": "Trey Research Sells Sustainability Practice to Deloitte",
                "date": "2025-04-01",
                "url": "https://consultancy.com/trey-sells-sustainability-2025",
                "excerpt": "Trey Research has sold its remaining sustainability advisory practice to Deloitte for an undisclosed sum. The sale includes 12 consultants and approximately $15M in annual client contracts. CEO Park confirmed: 'Sustainability consulting is not part of our go-forward strategy. We wish the team well at Deloitte.'"
            },
            {
                "id": "WEB-9",
                "type": "news_article",
                "title": "Trey Research: 'No New Vendor Contracts Until 2026' — Internal Memo",
                "date": "2025-03-05",
                "url": "https://businessinsider.com/trey-research-vendor-freeze-2025",
                "excerpt": "An internal memo obtained by journalists reveals Trey Research has frozen all new vendor contracts through end of 2025. The memo states: 'No purchase orders for software, consulting, or technology services will be approved regardless of amount. Existing contracts under review for termination or renegotiation.' This extends the prior spending freeze."
            },
            {
                "id": "SEC-3",
                "type": "sec_filing",
                "title": "Trey Research 8-K — Going Concern Warning",
                "date": "2025-03-15",
                "url": "https://sec.gov/trey-8k-march-2025",
                "excerpt": "The Company's auditors have issued a going concern qualification for FY2024, citing sustained operating losses, declining revenue, workforce reductions, and limited cash runway. Management disputes the characterization and states it has 'sufficient liquidity through cost actions already implemented.' Credit facilities remain available but unused."
            },
            {
                "id": "WEB-10",
                "type": "news_article",
                "title": "Trey Research Clients Flee to Competitors Amid Restructuring",
                "date": "2025-02-25",
                "url": "https://ft.com/trey-client-departures-2025",
                "excerpt": "Multiple sources confirm that at least 30% of Trey Research's top 50 clients have moved engagements to competitors since the restructuring announcement. McKinsey, BCG, and Accenture have been the primary beneficiaries. One departing client CEO stated: 'We need partners who are investing in the future, not cutting their way to survival.'"
            }
        ],
        "workiq_signals": {
            "ebook_download": None,
            "webinar": None,
            "meeting": None,
            "crm_note": {"title": "Marketing flagged: Trey Research unlikely — restructuring in progress", "date": "2025-02-20", "source": "Marketing Notes"}
        },
        "expected_fit": "LOW",
        "expected_score": 1,
        "expected_acv": "$50K - $90K (if they buy at all)"
    },

    "northwind traders": {
        "name": "Northwind Traders",
        "industry": "Retail / Distribution",
        "revenue": "$3.1B",
        "headcount": "14,000",
        "hq": "Seattle, WA",
        "country_code": "us",
        "facilities": 8,
        "description": "Regional retail chain and distribution company specializing in sustainable and organic food products.",
        "sources": [
            {
                "id": "WEB-1",
                "type": "company_website",
                "title": "Northwind Traders — Our Sustainability Commitment",
                "date": "2024-06-01",
                "url": "https://northwindtraders.com/sustainability",
                "excerpt": "At Northwind Traders, sustainability is part of who we are. We source 85% of products from certified sustainable suppliers. We publish an annual sustainability report covering Scope 1 and 2 emissions. Scope 3 supply chain emissions remain estimated only and are not independently verified."
            },
            {
                "id": "WEB-2",
                "type": "news_article",
                "title": "Northwind Traders Hires New CFO from Whole Foods",
                "date": "2025-03-10",
                "url": "https://retaildive.com/northwind-new-cfo-2025",
                "excerpt": "Northwind Traders appointed Jennifer Walsh as CFO, previously VP Finance at Whole Foods. Walsh brings experience in retail operations and supply chain optimization. CEO Michael Torres said the hire reflects Northwind's focus on operational excellence and sustainability reporting as the company expands into new markets."
            },
            {
                "id": "WEB-3",
                "type": "press_release",
                "title": "Northwind Traders FY2024 Results",
                "date": "2024-11-01",
                "url": "https://investors.northwindtraders.com/fy2024",
                "excerpt": "Revenue grew 14% to $3.1B driven by new store openings and e-commerce expansion. The company opened 12 new locations and plans 15 more in FY2025. CEO Michael Torres noted: 'Our customers increasingly ask about our environmental practices. We want to have better answers.'"
            },
            {
                "id": "SEC-1",
                "type": "sec_filing",
                "title": "Northwind 10-K — Selected Financials",
                "date": "2024-11-15",
                "url": "https://sec.gov/northwind-10k",
                "excerpt": "Revenue: $3.1B (+14% YoY). Operating income: $280M. Expansion capex: $200M focused on new store openings. Supply chain spans 2,400 suppliers across 18 countries. Environmental disclosure: Scope 1+2 reported annually. Scope 3 estimated but not verified. No dedicated sustainability technology budget in current fiscal plan. Management acknowledges measurement gap in supply chain emissions reporting."
            },
            {
                "id": "SEC-2",
                "type": "sec_filing",
                "title": "Northwind 10-K FY2023",
                "date": "2023-11-15",
                "url": "https://sec.gov/northwind-10k-2023",
                "excerpt": "Revenue: $2.7B (+11% YoY). Operating income: $240M. Opened 10 new locations in FY2023. Supply chain complexity growing — now 2,100 suppliers. Environmental reporting limited to Scope 1 and 2 estimates. No sustainability technology investment planned for FY2024."
            },
            {
                "id": "WEB-4",
                "type": "sustainability_report",
                "title": "Northwind 2023 Sustainability Report",
                "date": "2023-09-01",
                "url": "https://northwindtraders.com/sustainability/2023",
                "excerpt": "We are proud of our sourcing practices: 82% certified sustainable suppliers in 2022. However, we recognize gaps in our quantitative environmental reporting. Our Scope 1+2 data relies on utility bills and fleet fuel records. Scope 3, representing an estimated 85% of our footprint, is calculated using industry averages rather than supplier-specific data."
            },
            {
                "id": "WEB-5",
                "type": "news_article",
                "title": "Retailers Under Pressure to Quantify Supply Chain Emissions",
                "date": "2024-03-20",
                "url": "https://retaildive.com/supply-chain-emissions-retailers-2024",
                "excerpt": "Major retailers including Northwind Traders face growing pressure from investors and regulators to quantify Scope 3 supply chain emissions. Northwind's 2,400-supplier network spans 18 countries, making accurate measurement particularly complex. CEO Torres acknowledged: 'We know directionally where we stand but lack precision.'"
            },
            {
                "id": "WEB-6",
                "type": "earnings_call",
                "title": "Northwind Q2 2024 Earnings Call",
                "date": "2024-05-15",
                "url": "https://seekingalpha.com/northwind-q2-2024",
                "excerpt": "Torres: Revenue momentum continues. We're investing in growth — new stores, e-commerce, supply chain capacity. Sustainability comes up in every investor meeting now. We're looking at it but it's not yet a budgeted line item for technology. We think we can improve reporting without a major platform investment initially."
            },
            {
                "id": "WEB-7",
                "type": "news_article",
                "title": "Northwind Traders Expands Into Southwest US Market",
                "date": "2025-01-15",
                "url": "https://bizjournals.com/northwind-southwest-expansion-2025",
                "excerpt": "Northwind Traders announced plans to open 15 new locations across Arizona, Nevada, and New Mexico in FY2025. The $200M expansion will bring the company's store count to over 100. Environmental groups have asked Northwind to commit to measuring emissions from new stores and distribution centers."
            },
            {
                "id": "WEB-8",
                "type": "news_article",
                "title": "Northwind's Supplier Sustainability Scorecard Program Launch",
                "date": "2024-08-15",
                "url": "https://grocerydive.com/northwind-supplier-scorecard-2024",
                "excerpt": "Northwind Traders launched a supplier sustainability scorecard program requiring its top 200 suppliers to report environmental data quarterly. However, the program currently relies on self-reported spreadsheets. VP Supply Chain Marcus Wong admitted: 'We need a technology platform to make this scalable. Manual collection from 2,400 suppliers isn't realistic.'"
            },
            {
                "id": "WEB-9",
                "type": "news_article",
                "title": "California Climate Disclosure Rules Impact Northwind's Reporting Plans",
                "date": "2025-02-10",
                "url": "https://retaildive.com/california-climate-northwind-2025",
                "excerpt": "New California climate disclosure requirements (SB 253 and SB 261) will require Northwind Traders to report Scope 1, 2, and 3 emissions with third-party assurance beginning 2026. CFO Jennifer Walsh confirmed: 'This changes our timeline. We had considered sustainability tech as a nice-to-have — it's now a must-have. We're starting vendor evaluation in Q2 2025.'"
            },
            {
                "id": "WEB-10",
                "type": "press_release",
                "title": "Northwind Announces 'Zero Waste by 2030' Goal",
                "date": "2024-12-05",
                "url": "https://news.northwindtraders.com/2024/12/zero-waste-commitment",
                "excerpt": "Northwind Traders committed to zero operational waste by 2030 and carbon-neutral operations by 2035. CEO Torres acknowledged: 'These commitments require precise measurement we don't have today. We will invest in the data infrastructure needed to track, verify, and report progress to stakeholders.'"
            },
            {
                "id": "SEC-3",
                "type": "sec_filing",
                "title": "Northwind 10-Q Q1 2025 — Regulatory Risk Update",
                "date": "2025-04-01",
                "url": "https://sec.gov/northwind-10q-q1-2025",
                "excerpt": "Risk Factor Update: Management has identified California Senate Bills 253/261 as a material compliance requirement effective 2026. The Company is initiating a technology evaluation to ensure emissions measurement and disclosure capabilities meet regulatory standards. Estimated implementation cost: $8-15M. Ongoing annual cost: $2-3M."
            },
            {
                "id": "WEB-11",
                "type": "earnings_call",
                "title": "Northwind Q4 2024 Earnings Call",
                "date": "2024-11-20",
                "url": "https://seekingalpha.com/northwind-q4-2024",
                "excerpt": "Walsh (new CFO): Revenue remains strong. Looking ahead, I want to flag sustainability measurement as an emerging priority. The California disclosure rules change our calculus. We're budgeting $10-15M for environmental data infrastructure in FY2025-2026. This wasn't in the prior plan but regulatory reality demands it. We'll provide more detail at Investor Day."
            }
        ],
        "workiq_signals": {
            "ebook_download": {"title": "Downloaded: 'Supply Chain Emissions for Retail'", "date": "2025-03-25", "contact": "Jennifer Walsh, CFO"},
            "webinar": None,
            "meeting": None,
            "crm_note": None
        },
        "expected_fit": "MEDIUM",
        "expected_score": 6,
        "expected_acv": "$120K - $220K"
    }
}


def get_company(name: str):
    """Look up a fictional company by name (case-insensitive)."""
    key = name.lower().strip()
    # Try exact match first
    if key in FICTIONAL_COMPANIES:
        return FICTIONAL_COMPANIES[key]
    # Try partial match
    for k, v in FICTIONAL_COMPANIES.items():
        if key in k or k in key:
            return v
    return None


def list_companies():
    """Return list of available fictional company names."""
    return [v["name"] for v in FICTIONAL_COMPANIES.values()]
