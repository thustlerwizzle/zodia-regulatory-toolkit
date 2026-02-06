"""
Streamlit Application for Regulatory Analysis Agent
"""
import streamlit as st
import json
from datetime import datetime
from regulatory_agent import RegulatoryAgent
from config import REGULATORY_AREAS, JURISDICTIONS, POLICY_CATEGORIES
import time


# Page configuration
st.set_page_config(
    page_title="Regulatory Analysis Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "results" not in st.session_state:
        st.session_state.results = None
    if "current_step" not in st.session_state:
        st.session_state.current_step = "input"
    if "research_progress" not in st.session_state:
        st.session_state.research_progress = 0
    if "news_refreshed" not in st.session_state:
        st.session_state.news_refreshed = False


def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🔍 Regulatory Analysis Agent</div>', unsafe_allow_html=True)
    st.markdown("**Analyze crypto, blockchain, and digital asset regulations. Perform gap analysis and update company policies.**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys (optional, can be set via .env)
        st.subheader("API Keys")
        st.info("Set API keys in .env file or enter below")
        
        deepseek_key = st.text_input("DeepSeek API Key", type="password", value="")
        if deepseek_key:
            import os
            os.environ["DEEPSEEK_API_KEY"] = deepseek_key
        
        newsapi_key = st.text_input("NewsAPI Key (Optional)", type="password", value="")
        if newsapi_key:
            import os
            os.environ["NEWSAPI_KEY"] = newsapi_key
        
        st.divider()
        
        # Research Tools Selection
        st.subheader("Research Tools")
        use_news = st.checkbox("Use NewsAPI", value=True)
        
        st.divider()
        
        # About
        st.subheader("About")
        st.info("""
        This agent analyzes cryptocurrency, blockchain, and digital asset regulations, performs gap analysis, and suggests policy updates.
        
        **Features:**
        - Autonomous web research
        - Regulatory gap analysis
        - Policy update recommendations
        - Source tracking
        """)
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Analysis", "📊 Results", "📄 Report", "📚 Sources", "📰 Latest News"])
    
    with tab1:
        st.markdown('<div class="section-header">Regulatory Analysis</div>', unsafe_allow_html=True)
        
        # Input form
        with st.form("analysis_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                topic = st.text_input(
                    "Topic/Query",
                    placeholder="e.g., stablecoin regulation, DeFi compliance, crypto custody requirements",
                    help="Enter the regulatory topic you want to analyze"
                )
                
                jurisdiction = st.selectbox(
                    "Jurisdiction (Optional)",
                    options=[""] + JURISDICTIONS,
                    help="Select a specific jurisdiction to focus on. Type to search through all countries and territories. Leave empty for global analysis."
                )
            
            with col2:
                regulatory_areas = st.multiselect(
                    "Focus Areas",
                    options=REGULATORY_AREAS,
                    default=REGULATORY_AREAS[:3],
                    help="Select regulatory areas to focus on"
                )
            
            # Current policies input
            st.subheader("Current Company Policies (Optional)")
            current_policies = st.text_area(
                "Paste your current policies here",
                height=200,
                placeholder="Enter your current company policies, standards, or compliance documents...",
                help="This will be used for gap analysis"
            )
            
            submitted = st.form_submit_button("🚀 Start Analysis", use_container_width=True)
        
        if submitted:
            if not topic:
                st.error("Please enter a topic/query to analyze.")
            else:
                # Initialize agent
                if st.session_state.agent is None:
                    with st.spinner("Initializing agent..."):
                        st.session_state.agent = RegulatoryAgent()
                
                # Run analysis
                with st.spinner("Running regulatory analysis... This may take a few minutes."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Update progress
                    status_text.text("🔍 Researching regulatory requirements...")
                    progress_bar.progress(20)
                    
                    try:
                        results = st.session_state.agent.run(
                            query=topic,
                            jurisdiction=jurisdiction if jurisdiction else "",
                            current_policies=current_policies if current_policies else ""
                        )
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Analysis complete!")
                        time.sleep(1)
                        progress_bar.empty()
                        status_text.empty()
                        
                        st.session_state.results = results
                        st.session_state.current_step = "results"
                        st.success("Analysis completed successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
                        progress_bar.empty()
                        status_text.empty()
    
    with tab2:
        st.markdown('<div class="section-header">Analysis Results</div>', unsafe_allow_html=True)
        
        if st.session_state.results:
            results = st.session_state.results
            
            # Regulatory Summary
            if results.get("regulatory_summary"):
                st.subheader("📋 Regulatory Requirements Summary")
                st.markdown(results["regulatory_summary"])
                st.divider()
            
            # Gap Analysis
            if results.get("gap_analysis"):
                st.subheader("🔍 Gap Analysis")
                gap_analysis = results["gap_analysis"]
                
                # Priority levels
                priority_levels = gap_analysis.get("priority_levels", {})
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Critical", len(priority_levels.get("critical", [])))
                with col2:
                    st.metric("High", len(priority_levels.get("high", [])))
                with col3:
                    st.metric("Medium", len(priority_levels.get("medium", [])))
                with col4:
                    st.metric("Low", len(priority_levels.get("low", [])))
                
                # Display gaps by priority
                for priority in ["critical", "high", "medium", "low"]:
                    gaps = priority_levels.get(priority, [])
                    if gaps:
                        with st.expander(f"🔴 {priority.upper()} Priority Gaps ({len(gaps)})", expanded=(priority in ["critical", "high"])):
                            for i, gap in enumerate(gaps, 1):
                                st.markdown(f"### Gap {i}: {gap.get('gap_id', f'GAP-{i:03d}')}")
                                st.markdown(f"**Requirement:** {gap.get('regulatory_requirement', 'N/A')}")
                                st.markdown(f"**Current Status:** {gap.get('current_policy_status', 'N/A')}")
                                st.markdown(f"**Gap:** {gap.get('gap_description', 'N/A')}")
                                st.markdown(f"**Recommendation:** {gap.get('recommendation', 'N/A')}")
                                if i < len(gaps):
                                    st.divider()
                
                st.divider()
            
            # Policy Updates
            if results.get("policy_updates"):
                st.subheader("📝 Policy Updates")
                policy_updates = results["policy_updates"]
                
                new_policies = policy_updates.get("new_policies", [])
                modified_policies = policy_updates.get("modified_policies", [])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("New Policies Required", len(new_policies))
                with col2:
                    st.metric("Policies to Modify", len(modified_policies))
                
                if new_policies:
                    st.markdown("#### New Policies")
                    for policy in new_policies:
                        with st.expander(f"🆕 {policy.get('gap_id', 'N/A')} - {policy.get('policy_category', 'N/A')}"):
                            st.markdown(f"**Regulatory Basis:** {policy.get('regulatory_basis', 'N/A')}")
                            st.markdown(f"**Proposed Change:** {policy.get('proposed_change', 'N/A')}")
                            if policy.get("policy_draft"):
                                st.markdown("**Policy Draft:**")
                                st.markdown(policy["policy_draft"])
                
                if modified_policies:
                    st.markdown("#### Modified Policies")
                    for policy in modified_policies:
                        with st.expander(f"✏️ {policy.get('gap_id', 'N/A')} - {policy.get('policy_category', 'N/A')}"):
                            st.markdown(f"**Current Policy:** {policy.get('current_policy', 'N/A')}")
                            st.markdown(f"**Proposed Change:** {policy.get('proposed_change', 'N/A')}")
                            if policy.get("policy_draft"):
                                st.markdown("**Updated Policy Draft:**")
                                st.markdown(policy["policy_draft"])
        else:
            st.info("👆 Run an analysis in the 'Analysis' tab to see results here.")
    
    with tab3:
        st.markdown('<div class="section-header">Full Report</div>', unsafe_allow_html=True)
        
        if st.session_state.results and st.session_state.results.get("report"):
            report = st.session_state.results["report"]
            
            # Download button
            st.download_button(
                label="📥 Download Report (Markdown)",
                data=report,
                file_name=f"regulatory_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
            
            st.divider()
            
            # Display report
            st.markdown(report)
        else:
            st.info("👆 Run an analysis to generate a report.")
    
    with tab4:
        st.markdown('<div class="section-header">Sources</div>', unsafe_allow_html=True)
        
        if st.session_state.results and st.session_state.results.get("sources"):
            sources = st.session_state.results["sources"]
            
            st.info(f"Found {len(sources)} unique sources")
            
            # Group by source type
            source_types = {}
            for source in sources:
                source_type = source.get("source_type", "unknown")
                if source_type not in source_types:
                    source_types[source_type] = []
                source_types[source_type].append(source)
            
            for source_type, type_sources in source_types.items():
                with st.expander(f"{source_type.upper()} Sources ({len(type_sources)})"):
                    for i, source in enumerate(type_sources, 1):
                        st.markdown(f"{i}. **{source.get('title', 'N/A')}**")
                        st.markdown(f"   🔗 [{source.get('url', 'N/A')}]({source.get('url', '')})")
                        if i < len(type_sources):
                            st.divider()
        else:
            st.info("👆 Run an analysis to see sources.")
    
    with tab5:
        st.markdown('<div class="section-header">Latest Crypto Regulation News</div>', unsafe_allow_html=True)
        
        # Button to fetch latest news
        if st.button("🔄 Refresh Latest News", use_container_width=True):
            st.session_state.news_refreshed = True
        
        # Fetch and display news
        if st.session_state.get("news_refreshed") or st.session_state.get("results"):
            with st.spinner("Fetching latest news articles..."):
                from research_tools import ResearchTools
                tools = ResearchTools()
                
                # Search for latest crypto regulation news
                queries = [
                    "cryptocurrency regulation",
                    "crypto regulation",
                    "digital asset regulation",
                    "stablecoin regulation"
                ]
                
                all_articles = []
                seen_urls = set()
                
                for query in queries:
                    try:
                        articles = tools.search_news(query, days=7)
                        for article in articles:
                            url = article.get('url', '')
                            if url and url not in seen_urls:
                                seen_urls.add(url)
                                all_articles.append(article)
                    except Exception as e:
                        st.warning(f"Error fetching news for '{query}': {str(e)}")
                
                # Sort by published date (newest first)
                all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
                
                if all_articles:
                    st.success(f"📰 Found {len(all_articles)} latest news articles (last 7 days)")
                    st.divider()
                    
                    # Display articles
                    for i, article in enumerate(all_articles, 1):
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"### {i}. {article.get('title', 'N/A')}")
                                
                                # Show description
                                content = article.get('content', '') or article.get('description', '')
                                if content:
                                    st.markdown(content[:300] + "..." if len(content) > 300 else content)
                                
                                # Metadata
                                col_meta1, col_meta2, col_meta3 = st.columns(3)
                                with col_meta1:
                                    st.caption(f"📅 {article.get('published_at', 'N/A')[:10] if article.get('published_at') else 'N/A'}")
                                with col_meta2:
                                    st.caption(f"📰 {article.get('source', 'N/A')}")
                                with col_meta3:
                                    if article.get('author'):
                                        st.caption(f"✍️ {article.get('author', 'N/A')}")
                                
                                # URL
                                st.markdown(f"[🔗 Read full article]({article.get('url', '#')})")
                            
                            with col2:
                                st.markdown("<br>", unsafe_allow_html=True)  # Spacing
                                if article.get('url'):
                                    st.link_button("Open", article.get('url'))
                            
                            if i < len(all_articles):
                                st.divider()
                else:
                    st.warning("⚠️ No news articles found. This might be due to:")
                    st.markdown("- API key issues (check your .env file)")
                    st.markdown("- No recent articles matching the search terms")
                    st.markdown("- Network connectivity issues")
        else:
            st.info("👆 Click 'Refresh Latest News' to fetch the latest crypto regulation news articles from the past 7 days.")


if __name__ == "__main__":
    main()

