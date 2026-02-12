"""
Zodia Markets - Regulatory Intelligence Toolkit
Web Application (Streamlit)
Deployed version with server-side API key security.
"""
import streamlit as st
import json
import os
import time
from datetime import datetime
from pathlib import Path

# ============================================================================
# SECURE API KEY LOADING - Keys are server-side ONLY, never exposed to users
# ============================================================================
def load_secrets():
    """Load API keys from Streamlit secrets (deployed) or .env (local dev)."""
    # Priority 1: Streamlit Cloud secrets (most secure for deployment)
    try:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
        os.environ["NEWSAPI_KEY"] = st.secrets["NEWSAPI_KEY"]
        if "LANGSMITH_API_KEY" in st.secrets:
            os.environ["LANGSMITH_API_KEY"] = st.secrets["LANGSMITH_API_KEY"]
        return True
    except Exception:
        pass

    # Priority 2: Environment variables (Docker / cloud platform)
    if os.environ.get("DEEPSEEK_API_KEY"):
        return True

    # Priority 3: .env file (local development only)
    try:
        from dotenv import load_dotenv
        load_dotenv()
        if os.environ.get("DEEPSEEK_API_KEY"):
            return True
    except Exception:
        pass

    return False

# Load secrets BEFORE importing any modules that use them
secrets_loaded = load_secrets()

from config import DEEPSEEK_API_KEY, JURISDICTIONS, REGULATORY_AREAS
from zodia_config import (
    COMPANY_NAME, COMPANY_DESCRIPTION,
    ZODIA_REGISTERED_JURISDICTIONS, ZODIA_EU_MICA_JURISDICTIONS,
    ZODIA_REPORT_SECTIONS
)
from zodia_research import ZodiaResearchEngine
from research_tools import ResearchTools
from regulatory_agent import RegulatoryAgent
from file_processor import FileProcessor

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Zodia Markets - Regulatory Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #555;
        margin-top: 0;
    }
    .status-registered {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px 15px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .status-not-registered {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px 15px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .advisory-serve {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 4px;
    }
    .advisory-caution {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 4px;
    }
    .advisory-decline {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 15px;
        border-radius: 4px;
    }
    .section-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .metric-card {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================
if "zodia_engine" not in st.session_state:
    st.session_state.zodia_engine = None
if "agent" not in st.session_state:
    st.session_state.agent = None
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "batch_results" not in st.session_state:
    st.session_state.batch_results = None
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# ============================================================================
# INITIALIZATION
# ============================================================================
def initialize():
    """Initialize the engines (cached in session state)."""
    if not st.session_state.initialized:
        if not secrets_loaded or not DEEPSEEK_API_KEY:
            st.error("API keys not configured. Please set up Streamlit secrets.")
            st.stop()
        try:
            st.session_state.zodia_engine = ZodiaResearchEngine()
            st.session_state.agent = RegulatoryAgent()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"Failed to initialize: {str(e)}")
            st.stop()

initialize()

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("### Zodia Markets")
    st.markdown("**Regulatory Intelligence Toolkit**")
    st.markdown("---")

    # Registration status
    st.markdown("#### Licensed Jurisdictions")
    for jur, info in ZODIA_REGISTERED_JURISDICTIONS.items():
        with st.expander(f"✅ {jur}"):
            st.markdown(f"**Entity:** {info['entity']}")
            st.markdown(f"**Regulator:** {info['regulator']}")
            st.markdown(f"**License:** {info['license_type']}")
            st.markdown(f"**Ref:** {info['reference']}")
            st.markdown(f"**Granted:** {info['date_granted']}")

    st.markdown("---")
    st.markdown("#### Report Scope")
    st.markdown("- Only **enacted/enforced** regulations")
    st.markdown("- VASP & stablecoin licensing")
    st.markdown("- Cross-border client advisory")
    st.markdown("- Compliance guidance")

    st.markdown("---")
    st.caption(f"Jurisdictions: {len(JURISDICTIONS)}")
    st.caption(f"Regulatory Topics: {len(REGULATORY_AREAS)}")

# ============================================================================
# HEADER
# ============================================================================
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<p class="main-header">🏛️ Zodia Markets</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Regulatory Intelligence Toolkit | VASP & Stablecoin Compliance</p>', unsafe_allow_html=True)
with col_status:
    if st.session_state.initialized:
        st.success("Engine Ready")
    else:
        st.warning("Initializing...")

# ============================================================================
# TABS
# ============================================================================
tab_zodia, tab_analysis, tab_news = st.tabs([
    "🏛️ Zodia Regulatory Research",
    "📋 General Analysis",
    "📰 Latest News"
])

# ============================================================================
# TAB 1: ZODIA REGULATORY RESEARCH
# ============================================================================
with tab_zodia:
    st.markdown("### Country-Specific Regulatory Research")
    st.markdown("Select a country to get a full regulatory intelligence report with cross-border advisory and compliance guidance.")

    # Country selection
    col_country, col_filter = st.columns([3, 1])

    # Build country list
    registered_list = sorted(ZODIA_REGISTERED_JURISDICTIONS.keys())
    eu_list = sorted(set(ZODIA_EU_MICA_JURISDICTIONS) - set(registered_list))
    other_list = sorted(set(JURISDICTIONS) - set(registered_list) - set(eu_list))

    country_options = (
        [f"🟢 {j} [REGISTERED]" for j in registered_list]
        + [f"🔵 {j} [EU/MiCA]" for j in eu_list]
        + [f"⚪ {j}" for j in other_list]
    )

    with col_country:
        selected_display = st.selectbox(
            "Select Country",
            country_options,
            index=0,
            help="Green = Zodia is registered, Blue = EU/MiCA passporting possible, White = Not registered"
        )

    # Extract actual country name
    country_name = selected_display
    for prefix in ["🟢 ", "🔵 ", "⚪ "]:
        if country_name.startswith(prefix):
            country_name = country_name[len(prefix):]
    for suffix in [" [REGISTERED]", " [EU/MiCA]"]:
        if country_name.endswith(suffix):
            country_name = country_name[:-len(suffix)]

    with col_filter:
        research_mode = st.radio(
            "Mode",
            ["Single Country", "All Registered (4)", "All EU/MiCA"],
            index=0
        )

    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        run_research = st.button("🔍 Run Research", type="primary", use_container_width=True)
    with col_btn2:
        export_btn = st.button("📥 Export Report", use_container_width=True)

    # Registration status display
    if country_name in ZODIA_REGISTERED_JURISDICTIONS:
        reg = ZODIA_REGISTERED_JURISDICTIONS[country_name]
        st.markdown(f"""<div class="status-registered">
            <strong>✅ ZODIA IS REGISTERED IN {country_name.upper()}</strong><br>
            {reg['entity']} | {reg['regulator']} | {reg['license_type']} ({reg['reference']})
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="status-not-registered">
            <strong>⚠️ ZODIA IS NOT REGISTERED IN {country_name.upper()}</strong><br>
            Zodia Markets is only licensed in: UK (FCA), Ireland (CBI), Abu Dhabi (ADGM), Jersey (JFSC)
        </div>""", unsafe_allow_html=True)

    # Run research
    if run_research:
        engine = st.session_state.zodia_engine

        if research_mode == "Single Country":
            with st.spinner(f"Researching {country_name}... This may take 30-60 seconds."):
                try:
                    result = engine.research_jurisdiction(country_name, include_news=True)
                    st.session_state.current_result = result
                    st.session_state.batch_results = None
                except Exception as e:
                    st.error(f"Research failed: {str(e)}")

        elif research_mode == "All Registered (4)":
            jurisdictions_to_research = list(ZODIA_REGISTERED_JURISDICTIONS.keys())
            results = {}
            progress_bar = st.progress(0, text="Starting batch research...")
            for i, jur in enumerate(jurisdictions_to_research):
                progress_bar.progress(
                    (i + 1) / len(jurisdictions_to_research),
                    text=f"Researching {jur}... ({i+1}/{len(jurisdictions_to_research)})"
                )
                try:
                    results[jur] = engine.research_jurisdiction(jur, include_news=True)
                except Exception as e:
                    results[jur] = {"jurisdiction": jur, "status": "error", "error": str(e)}
                time.sleep(2)
            st.session_state.batch_results = results
            st.session_state.current_result = None
            progress_bar.empty()

        elif research_mode == "All EU/MiCA":
            results = {}
            progress_bar = st.progress(0, text="Starting EU/MiCA batch...")
            for i, jur in enumerate(ZODIA_EU_MICA_JURISDICTIONS):
                progress_bar.progress(
                    (i + 1) / len(ZODIA_EU_MICA_JURISDICTIONS),
                    text=f"Researching {jur}... ({i+1}/{len(ZODIA_EU_MICA_JURISDICTIONS)})"
                )
                try:
                    results[jur] = engine.research_jurisdiction(jur, include_news=True)
                except Exception as e:
                    results[jur] = {"jurisdiction": jur, "status": "error", "error": str(e)}
                time.sleep(3)
            st.session_state.batch_results = results
            st.session_state.current_result = None
            progress_bar.empty()

        st.rerun()

    # Display single result
    if st.session_state.current_result:
        result = st.session_state.current_result
        report = result.get("report", {})
        jurisdiction = result.get("jurisdiction", "Unknown")

        st.markdown(f"## {jurisdiction} - Regulatory Intelligence Report")
        st.caption(f"Generated: {result.get('timestamp', 'N/A')} | Duration: {result.get('duration_seconds', 0):.1f}s | News Articles: {result.get('news_articles_found', 0)}")

        # Metrics
        risks = report.get("high_level_risk_points", [])
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Status", "REGISTERED" if result.get("is_registered") else "NOT REGISTERED")
        mc2.metric("Risk Points", len(risks) if isinstance(risks, list) else "N/A")
        mc3.metric("News Articles", result.get("news_articles_found", 0))
        mc4.metric("Analysis Time", f"{result.get('duration_seconds', 0):.0f}s")

        # Report sections as expandable cards
        st.markdown("---")

        with st.expander("📋 1. Regulatory Regime Summary", expanded=True):
            st.markdown(report.get("summary", "Not available."))

        with st.expander("⚠️ 2. High-Level Risk Points for Zodia Markets"):
            risks = report.get("high_level_risk_points", [])
            if isinstance(risks, list):
                for r in risks:
                    st.markdown(f"- {r}")
            else:
                st.markdown(str(risks))

        with st.expander("📜 3. Regulatory Framework"):
            st.markdown(report.get("regulatory_framework", "Not available."))

        with st.expander("💱 4. Virtual Asset Trading Platforms"):
            st.markdown(report.get("virtual_asset_trading_platforms", "Not available."))

        with st.expander("🪙 5. Stablecoin & Fiat-Backed Token Regulation"):
            st.markdown(report.get("stablecoin_regulation", "Not available."))

        with st.expander("🏦 6. Store of Value Facility Rules"):
            st.markdown(report.get("store_of_value_facility_rules", "Not available."))

        with st.expander("🔑 7. Licensing Triggers & Expectations"):
            st.markdown(report.get("regulatory_expectations_and_licensing_triggers", "Not available."))

        # THE KEY ADVISORY SECTIONS
        st.markdown("---")
        st.markdown("### Advisory & Compliance Guidance")

        with st.expander("🎯 8. Territorial Scope & Perimeter Test", expanded=True):
            st.markdown("**If Zodia has ZERO presence and ZERO solicitation - is it outside scope?**\n")
            st.markdown(report.get("territorial_scope_and_perimeter_test", "Not available."))

        with st.expander("🔄 9. Reverse Solicitation & Direct Market Access", expanded=True):
            st.markdown("**Deep dive: conditions, documentation, what breaks it, enforcement risk**\n")
            st.markdown(report.get("reverse_solicitation_and_direct_market_access", "Not available."))

        with st.expander("🌍 10. Cross-Border Client Advisory", expanded=True):
            st.markdown(f"**Can Zodia Markets serve a client from {jurisdiction}?**\n")
            if result.get("is_registered"):
                st.success(f"Zodia IS licensed in {jurisdiction}.")
            else:
                st.warning(f"Zodia is NOT licensed in {jurisdiction}. See advisory below.")
            st.markdown(report.get("cross_border_client_advisory", "Not available."))

        with st.expander("✅ 11. Compliance Guidance & Verdict", expanded=True):
            st.markdown("**Verdict and actionable advice for Zodia Markets compliance team:**\n")
            st.markdown(report.get("compliance_guidance_and_recommendations", "Not available."))

        # Sources & References
        with st.expander("📚 12. Sources & References"):
            st.markdown("**Official regulatory sources cited in this analysis:**\n")
            sources = report.get("sources_and_references", [])
            if isinstance(sources, list) and sources:
                for i, src in enumerate(sources, 1):
                    st.markdown(f"{i}. {src}")
            elif isinstance(sources, str) and sources:
                st.markdown(sources)
            else:
                st.info("No specific source URLs provided. Refer to the regulatory body's website for official texts.")

        # Live News Feed
        news = result.get("news_articles", [])
        with st.expander(f"📡 13. Live News Feed ({len(news)} articles - LIVE)", expanded=False):
            st.markdown(f"**Data Source:** NewsAPI (live scraping)")
            st.markdown(f"**Scraped at:** {result.get('timestamp', 'N/A')[:19]}")
            st.markdown(f"**Coverage:** Last 30 days | VASP, crypto, stablecoin, digital asset regulation\n")
            if news:
                for i, a in enumerate(news[:15], 1):
                    st.markdown(f"### {i}. {a.get('title', 'N/A')}")
                    col1, col2, col3 = st.columns(3)
                    col1.caption(f"Date: {a.get('published_at', 'N/A')[:10]}")
                    col2.caption(f"Source: {a.get('source', 'N/A')}")
                    author = a.get('author', '')
                    if author:
                        col3.caption(f"Author: {author}")
                    url = a.get('url', '')
                    if url:
                        st.markdown(f"[Read Full Article]({url})")
                    content = a.get('content', '') or a.get('description', '')
                    if content:
                        st.markdown(f"> {content[:300]}...")
                    st.markdown("---")
            else:
                st.info("No recent news articles found for this jurisdiction in the last 30 days.")
            
            st.markdown("---")
            st.markdown("**How new regulations are detected:**")
            st.markdown("- NewsAPI continuously scrapes global news sources")
            st.markdown("- New regulatory developments appear as soon as reported by any news outlet")
            st.markdown("- The LLM analysis incorporates live news articles as context")
            st.markdown("- **Recommendation:** Cross-reference with official regulator websites")

        # Export
        if export_btn:
            engine = st.session_state.zodia_engine
            md = engine.format_report_markdown(result)
            st.download_button(
                "📥 Download Report (Markdown)",
                md,
                f"Zodia_{jurisdiction.replace(' ', '_')}_Report.md",
                "text/markdown"
            )

    # Display batch results
    if st.session_state.batch_results:
        results = st.session_state.batch_results
        success = sum(1 for r in results.values() if r.get("status") == "success")
        errors = sum(1 for r in results.values() if r.get("status") == "error")

        st.markdown(f"## Batch Research Results")
        st.markdown(f"**{success} completed** | **{errors} errors** | **{len(results)} total**")

        for jur, result in results.items():
            if result.get("status") == "success":
                report = result.get("report", {})
                with st.expander(f"{'✅' if result.get('is_registered') else '⚪'} {jur}", expanded=False):
                    st.markdown(f"**Summary:** {report.get('summary', 'N/A')[:300]}...")
                    st.markdown("**Cross-Border Advisory:**")
                    st.markdown(report.get("cross_border_client_advisory", "N/A")[:500])
                    st.markdown("**Compliance Guidance:**")
                    st.markdown(report.get("compliance_guidance_and_recommendations", "N/A")[:500])
            else:
                with st.expander(f"❌ {jur} - Error"):
                    st.error(result.get("error", "Unknown error"))

# ============================================================================
# TAB 2: GENERAL ANALYSIS
# ============================================================================
with tab_analysis:
    st.markdown("### General Regulatory Analysis")
    st.markdown("Run a full regulatory analysis with gap analysis, policy updates, and implementation.")

    col_input, col_results = st.columns([1, 2])

    with col_input:
        query = st.text_input("Regulatory Topic", value="stablecoin regulation")
        jurisdiction_input = st.text_input("Jurisdiction (optional)")

        # File upload
        uploaded_files = st.file_uploader(
            "Upload Company Policies (optional)",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt", "md", "xlsx", "csv"]
        )

        policies_text = st.text_area("Or paste policies manually", height=150)

        run_analysis = st.button("🚀 Run Full Analysis", type="primary")

    with col_results:
        if run_analysis:
            agent = st.session_state.agent
            if not agent:
                st.error("Agent not initialized.")
            else:
                # Process uploaded files
                current_policies = policies_text or ""
                if uploaded_files:
                    for f in uploaded_files:
                        try:
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f.name) as tmp:
                                tmp.write(f.read())
                                tmp_path = tmp.name
                            text = FileProcessor.extract_text_from_file(tmp_path)
                            current_policies += f"\n\n--- {f.name} ---\n\n{text}"
                            os.unlink(tmp_path)
                        except Exception as e:
                            st.warning(f"Could not process {f.name}: {e}")

                with st.spinner("Running full analysis... This may take several minutes."):
                    try:
                        results = agent.run(
                            query=query,
                            jurisdiction=jurisdiction_input,
                            current_policies=current_policies
                        )

                        if results.get("regulatory_summary"):
                            st.markdown("#### Regulatory Summary")
                            st.markdown(results["regulatory_summary"])

                        if results.get("gap_analysis"):
                            st.markdown("#### Gap Analysis")
                            gap = results["gap_analysis"]
                            pl = gap.get("priority_levels", {})
                            if pl:
                                gc1, gc2, gc3, gc4 = st.columns(4)
                                gc1.metric("Critical", len(pl.get("critical", [])))
                                gc2.metric("High", len(pl.get("high", [])))
                                gc3.metric("Medium", len(pl.get("medium", [])))
                                gc4.metric("Low", len(pl.get("low", [])))

                        if results.get("policy_updates"):
                            pu = results["policy_updates"]
                            st.markdown("#### Policy Updates")
                            st.markdown(f"New: {len(pu.get('new_policies', []))} | Modified: {len(pu.get('modified_policies', []))}")

                        if results.get("report"):
                            with st.expander("Full Report"):
                                st.markdown(results["report"])

                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")

# ============================================================================
# TAB 3: LATEST NEWS
# ============================================================================
with tab_news:
    st.markdown("### Latest Crypto & Digital Asset Regulation News")

    if st.button("🔄 Refresh News"):
        with st.spinner("Fetching latest news..."):
            try:
                tools = ResearchTools()
                queries = ["cryptocurrency regulation", "stablecoin regulation",
                          "VASP regulation", "digital asset regulation", "Zodia Markets"]
                all_articles = []
                seen_urls = set()
                for q in queries:
                    try:
                        articles = tools.search_news(q, days=7)
                        for a in articles:
                            url = a.get("url", "")
                            if url and url not in seen_urls:
                                seen_urls.add(url)
                                all_articles.append(a)
                    except Exception:
                        pass
                all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)

                if all_articles:
                    st.success(f"Found {len(all_articles)} articles")
                    for i, a in enumerate(all_articles[:25], 1):
                        with st.container():
                            st.markdown(f"**{i}. {a.get('title', 'N/A')}**")
                            content = a.get("content", "") or a.get("description", "")
                            if content:
                                st.markdown(content[:300] + ("..." if len(content) > 300 else ""))
                            col_d, col_s, col_l = st.columns([1, 1, 2])
                            col_d.caption(a.get("published_at", "N/A")[:10])
                            col_s.caption(a.get("source", "N/A"))
                            col_l.markdown(f"[Read Article]({a.get('url', '#')})")
                            st.markdown("---")
                else:
                    st.warning("No articles found. Check API key configuration.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption("Zodia Markets Regulatory Intelligence Toolkit | Powered by DeepSeek AI | API keys secured server-side")
