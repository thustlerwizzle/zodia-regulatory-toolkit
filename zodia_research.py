"""
Zodia Markets Regulatory Research Engine
Performs deep regulatory research specifically tailored for Zodia Markets' business model.
Walks through each business activity and maps to relevant regulations.
Covers reverse solicitation, direct market access, and cross-border advisory.
Only returns enacted/enforced/final regulations.
"""

import json
import os
import hashlib
import time
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from langchain_deepseek import ChatDeepSeek
try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    from langchain.schema import HumanMessage, SystemMessage

from research_tools import ResearchTools
from knowledge_base import RegulatoryKnowledgeBase
from config import DEEPSEEK_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from zodia_config import (
    COMPANY_NAME,
    COMPANY_DESCRIPTION,
    COMPANY_ENTITY_TYPE,
    ZODIA_REGISTERED_JURISDICTIONS,
    ZODIA_EU_MICA_JURISDICTIONS,
    ZODIA_BUSINESS_ACTIVITIES,
    ZODIA_SERVICES,
    ZODIA_REGULATORY_FOCUS,
    REGULATION_STATUS_FILTER,
    REGULATION_STATUS_EXCLUDE,
    ZODIA_REPORT_SECTIONS,
    ZODIA_LICENSED_ENTITIES_CONTEXT,
    ZODIA_PERIMETER_TEST,
    ZODIA_REVERSE_SOLICITATION_FRAMEWORK
)


class ZodiaResearchEngine:
    """
    Research engine designed for Zodia Markets regulatory analysis.
    Uses DeepSeek LLM + NewsAPI to produce structured regulatory intelligence.
    Walks through each Zodia business activity and maps to relevant regulations.
    """

    def __init__(self):
        self.llm = None
        self._llm_error = None
        if DEEPSEEK_API_KEY:
            try:
                self.llm = ChatDeepSeek(
                    model=LLM_MODEL,
                    temperature=LLM_TEMPERATURE,
                    max_tokens=None,
                    timeout=120,
                    max_retries=3
                )
                print(f"[LLM] DeepSeek initialized (model={LLM_MODEL})")
            except Exception as e:
                self._llm_error = str(e)
                print(f"[LLM] ERROR: Could not initialize DeepSeek: {e}")
        else:
            self._llm_error = "DEEPSEEK_API_KEY is empty or not set"
            print(f"[LLM] WARNING: No DEEPSEEK_API_KEY found - LLM analysis will NOT work")

        self.research_tools = ResearchTools()
        self.results_cache = {}

        # Persistent cache directory - shared across all sessions/users
        self._cache_dir = Path(__file__).parent / "report_cache"
        try:
            self._cache_dir.mkdir(exist_ok=True)
        except Exception:
            # Fallback for cloud environments
            self._cache_dir = Path("/tmp") / "zodia_report_cache"
            self._cache_dir.mkdir(exist_ok=True)
        # Cache TTL: 24 hours (in seconds)
        self._cache_ttl = 86400
        print(f"[CACHE] Report cache directory: {self._cache_dir}")

        # Load local regulatory knowledge base (257 jurisdictions previously scraped)
        self.knowledge_base = RegulatoryKnowledgeBase()
        try:
            kb_count = self.knowledge_base.load()
            print(f"[KB] Loaded regulatory knowledge base: {kb_count} jurisdictions from {self.knowledge_base.data_dir}")
        except Exception as e:
            print(f"[KB] Warning: Could not load knowledge base: {e}")

        # Check if NewsAPI is available
        self.newsapi_available = False
        try:
            from config import NEWSAPI_KEY
            if NEWSAPI_KEY and self.research_tools.newsapi_client:
                self.newsapi_available = True
                print("[NEWS] NewsAPI is available - live news scraping enabled")
            else:
                print("[NEWS] NewsAPI not configured - using knowledge base only")
        except Exception:
            print("[NEWS] NewsAPI not available - using knowledge base only")

    # =========================================================================
    # CACHING - ensures all users see identical results for the same query
    # =========================================================================
    def _cache_key(self, jurisdiction: str) -> str:
        """Generate a deterministic cache key for a jurisdiction."""
        safe = jurisdiction.lower().strip().replace(" ", "_").replace("/", "_")
        return safe

    def _get_cached_result(self, jurisdiction: str) -> Optional[Dict]:
        """Load a cached result if it exists and is fresh (within TTL)."""
        key = self._cache_key(jurisdiction)
        cache_file = self._cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
            # Check TTL
            cached_time = datetime.fromisoformat(cached.get("timestamp", "2000-01-01"))
            age_seconds = (datetime.now() - cached_time).total_seconds()
            if age_seconds > self._cache_ttl:
                print(f"[CACHE] Expired for {jurisdiction} (age: {age_seconds:.0f}s > {self._cache_ttl}s)")
                return None
            print(f"[CACHE] HIT for {jurisdiction} (age: {age_seconds:.0f}s)")
            cached["_from_cache"] = True
            cached["_cache_age_seconds"] = age_seconds
            return cached
        except Exception as e:
            print(f"[CACHE] Error reading cache for {jurisdiction}: {e}")
            return None

    def _save_to_cache(self, jurisdiction: str, result: Dict):
        """Save a result to the persistent cache."""
        key = self._cache_key(jurisdiction)
        cache_file = self._cache_dir / f"{key}.json"
        try:
            # Don't cache fallback/error reports
            if result.get("report", {}).get("_fallback"):
                print(f"[CACHE] Skipping cache for {jurisdiction} (fallback report)")
                return
            # Remove non-serializable or transient fields
            clean = {k: v for k, v in result.items() if not k.startswith("_")}
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(clean, f, indent=2, ensure_ascii=False, default=str)
            print(f"[CACHE] SAVED for {jurisdiction}")
        except Exception as e:
            print(f"[CACHE] Error saving cache for {jurisdiction}: {e}")

    def clear_cache(self, jurisdiction: str = None):
        """Clear cached results. If jurisdiction is None, clear all."""
        if jurisdiction:
            key = self._cache_key(jurisdiction)
            cache_file = self._cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
                print(f"[CACHE] Cleared for {jurisdiction}")
        else:
            for f in self._cache_dir.glob("*.json"):
                f.unlink()
            print("[CACHE] All cache cleared")

    # =========================================================================
    # MAIN RESEARCH METHOD
    # =========================================================================
    def research_jurisdiction(
        self,
        jurisdiction: str,
        include_news: bool = True,
        progress_callback=None,
        force_refresh: bool = False
    ) -> Dict:
        """
        Perform comprehensive regulatory research for a single jurisdiction.
        Uses persistent caching so all users see identical results.
        Uses: (1) Cache check, (2) Local knowledge base, (3) Live NewsAPI if available,
        (4) DeepSeek LLM analysis with both as context.
        """
        # Step 0: Check persistent cache first (unless force refresh)
        if not force_refresh:
            cached = self._get_cached_result(jurisdiction)
            if cached:
                if progress_callback:
                    age = cached.get("_cache_age_seconds", 0)
                    progress_callback(
                        f"Using cached analysis for {jurisdiction} "
                        f"(generated {age/3600:.1f} hours ago). "
                        f"Click 'Force Refresh' for a new analysis."
                    )
                return cached
        elif progress_callback:
            progress_callback(f"Force refresh requested for {jurisdiction}...")

        start_time = datetime.now()

        if progress_callback:
            progress_callback(f"Researching {jurisdiction}...")

        # Step 1: Load context from local knowledge base (always available)
        kb_context = None
        if progress_callback:
            progress_callback(f"Loading knowledge base data for {jurisdiction}...")
        kb_context = self.knowledge_base.get_jurisdiction_context(jurisdiction)
        if kb_context:
            if progress_callback:
                progress_callback(f"  Found existing regulatory data for {jurisdiction}")
        else:
            if progress_callback:
                progress_callback(f"  No prior data for {jurisdiction} in knowledge base")

        # Step 2: Gather live news (if NewsAPI is available)
        news_articles = []
        if include_news and self.newsapi_available:
            if progress_callback:
                progress_callback(f"Fetching live news for {jurisdiction}...")
            news_articles = self._fetch_news(jurisdiction, progress_callback)
            if progress_callback:
                progress_callback(f"  Found {len(news_articles)} live news articles")
        elif include_news and not self.newsapi_available:
            if progress_callback:
                progress_callback(f"  NewsAPI not available - using knowledge base data only")

        # Step 3: Check registration status
        registration_info = ZODIA_REGISTERED_JURISDICTIONS.get(jurisdiction, None)

        # Step 4: Generate structured report via DeepSeek (with KB + news as context)
        if progress_callback:
            progress_callback(f"Analyzing {jurisdiction} regulations for Zodia's business activities...")

        report = self._generate_structured_report(
            jurisdiction=jurisdiction,
            news_articles=news_articles,
            registration_info=registration_info,
            kb_context=kb_context
        )

        # Step 5: Compile result
        data_sources = []
        if kb_context:
            data_sources.append("Local Knowledge Base (257 jurisdictions)")
        if news_articles:
            data_sources.append(f"Live NewsAPI ({len(news_articles)} articles)")
        data_sources.append("DeepSeek LLM Analysis (temperature=0, deterministic)")

        result = {
            "jurisdiction": jurisdiction,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "is_registered": registration_info is not None,
            "registration_info": registration_info,
            "news_articles_found": len(news_articles),
            "news_articles": news_articles[:15],
            "data_sources": data_sources,
            "kb_data_available": kb_context is not None,
            "newsapi_available": self.newsapi_available,
            "report": report,
            "status": "success"
        }

        # Save to persistent cache (so next user gets identical result)
        self._save_to_cache(jurisdiction, result)

        self.results_cache[jurisdiction] = result
        return result

    def research_all_registered_jurisdictions(self, progress_callback=None) -> Dict:
        """Research all jurisdictions where Zodia is registered."""
        results = {}
        jurisdictions = list(ZODIA_REGISTERED_JURISDICTIONS.keys())

        for i, jurisdiction in enumerate(jurisdictions, 1):
            if progress_callback:
                progress_callback(f"[{i}/{len(jurisdictions)}] {jurisdiction}")
            try:
                results[jurisdiction] = self.research_jurisdiction(
                    jurisdiction, progress_callback=progress_callback
                )
            except Exception as e:
                results[jurisdiction] = {
                    "jurisdiction": jurisdiction, "status": "error", "error": str(e)
                }
            if i < len(jurisdictions):
                time.sleep(2)

        return results

    def _fetch_news(self, jurisdiction: str, progress_callback=None) -> List[Dict]:
        """
        Fetch relevant LIVE news for a jurisdiction.
        Gracefully handles API expiration or errors.
        """
        if not self.newsapi_available:
            return []

        all_articles = []
        seen_urls = set()

        # Broad set of queries to catch all relevant regulatory news
        queries = [
            f"VASP regulation {jurisdiction}",
            f"crypto regulation {jurisdiction} 2025 2026",
            f"virtual asset regulation {jurisdiction}",
            f"crypto licensing {jurisdiction}",
            f"digital asset exchange license {jurisdiction}",
            f"crypto broker regulation {jurisdiction}",
            f"stablecoin regulation {jurisdiction}",
            f"stablecoin law {jurisdiction}",
            f"institutional crypto {jurisdiction}",
            f"cross-border crypto services {jurisdiction}",
            f"crypto enforcement {jurisdiction}",
            f"AML crypto {jurisdiction}",
        ]

        api_failed = False
        for query in queries:
            if api_failed:
                break  # Stop if API is down
            try:
                articles = self.research_tools.search_news(query, days=30)
                for article in articles:
                    url = article.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_articles.append(article)
            except Exception as e:
                error_str = str(e).lower()
                if "401" in error_str or "403" in error_str or "expired" in error_str or "unauthorized" in error_str:
                    # API key expired or invalid
                    if progress_callback:
                        progress_callback(f"  NewsAPI key expired/invalid - switching to knowledge base only")
                    self.newsapi_available = False
                    api_failed = True
                else:
                    if progress_callback:
                        progress_callback(f"  News warning: {str(e)[:60]}")

        all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return all_articles[:30]

    def _generate_structured_report(
        self,
        jurisdiction: str,
        news_articles: List[Dict],
        registration_info: Optional[Dict],
        kb_context: Optional[str] = None
    ) -> Dict:
        """
        Use DeepSeek to generate a structured regulatory report.
        Injects local knowledge base data + live news as context.
        """
        if not self.llm:
            return self._generate_fallback_report(jurisdiction, news_articles, registration_info)

        # News context
        news_context = ""
        if news_articles:
            news_items = []
            for a in news_articles[:10]:
                news_items.append(
                    f"- {a.get('title', 'N/A')} ({a.get('published_at', 'N/A')[:10]})\n"
                    f"  {a.get('content', '')[:200]}"
                )
            news_context = "\n".join(news_items)
        else:
            news_context = "No recent news articles found."

        # Registration context
        if registration_info:
            reg_context = (
                f"ZODIA IS REGISTERED in {jurisdiction}:\n"
                f"- Entity: {registration_info.get('entity', 'N/A')}\n"
                f"- Regulator: {registration_info.get('regulator', 'N/A')}\n"
                f"- License: {registration_info.get('license_type', 'N/A')}\n"
                f"- Reference: {registration_info.get('reference', 'N/A')}\n"
                f"- Granted: {registration_info.get('date_granted', 'N/A')}\n"
                f"- Scope: {registration_info.get('scope', 'N/A')}"
            )
        else:
            reg_context = f"Zodia Markets is NOT registered in {jurisdiction}."

        # EU/MiCA note
        mica_note = ""
        if jurisdiction in ZODIA_EU_MICA_JURISDICTIONS:
            mica_note = (
                f"\nIMPORTANT: {jurisdiction} is an EU/EEA member. Under MiCA, "
                "Zodia may passport from Ireland once CASP-authorized. Analyze availability."
            )

        # Business activities context
        activities_text = "\n".join(
            f"  {i+1}. {act['name']}: {act['description']}"
            for i, act in enumerate(ZODIA_BUSINESS_ACTIVITIES.values())
        )
        services_text = "\n".join(f"  - {s}" for s in ZODIA_SERVICES)

        # Section descriptions
        sections_desc = "\n".join(
            f"  - **{key}**: {desc}" for key, desc in ZODIA_REPORT_SECTIONS.items()
        )

        prompt = f"""You are a senior regulatory compliance analyst and cross-border legal advisor. Prepare a regulatory intelligence report for **Zodia Markets** focused ONLY on regulations that DIRECTLY affect its specific business activities.

===========================================================================
CRITICAL: INSTITUTIONAL CLIENTS ONLY
===========================================================================
Zodia Markets serves ONLY institutional and professional clients:
- Corporations and corporate treasuries
- Banks and financial institutions
- Hedge funds and asset managers
- Family offices
- Professional investors meeting qualified/sophisticated investor thresholds
Zodia does NOT serve retail clients, individuals, or consumers. NEVER.

This distinction is CRITICAL because many jurisdictions:
- EXEMPT services to institutional/professional/qualified investors from licensing
- Have LIGHTER regulatory requirements for institutional-only business
- Apply BROADER reverse solicitation exemptions for institutional clients
- Have HIGHER thresholds before cross-border rules apply to institutional services
- Distinguish between "retail" VASP licensing and "wholesale/institutional" licensing

YOUR ENTIRE ANALYSIS must be through the lens of INSTITUTIONAL clients ONLY.
Do NOT analyze retail/consumer protection rules unless they also catch institutional services.

===========================================================================
ZODIA MARKETS - WHAT THE BUSINESS ACTUALLY DOES
===========================================================================
{COMPANY_DESCRIPTION}

SPECIFIC BUSINESS ACTIVITIES (map each to local regulations):
{activities_text}

SERVICES:
{services_text}

Entity type: {COMPANY_ENTITY_TYPE}

===========================================================================
ZODIA'S LICENSING FOOTPRINT (ONLY 4 JURISDICTIONS)
===========================================================================
{ZODIA_LICENSED_ENTITIES_CONTEXT}

===========================================================================
ZODIA'S CROSS-BORDER LEGAL APPROACH - THE PERIMETER TEST
===========================================================================
{ZODIA_PERIMETER_TEST}

===========================================================================
REVERSE SOLICITATION ANALYSIS FRAMEWORK
===========================================================================
{ZODIA_REVERSE_SOLICITATION_FRAMEWORK}

===========================================================================
STATUS IN {jurisdiction.upper()}
===========================================================================
{reg_context}
{mica_note}

===========================================================================
PREVIOUSLY RESEARCHED DATA (LOCAL KNOWLEDGE BASE)
===========================================================================
{kb_context if kb_context else f"No prior research data available for {jurisdiction} in the knowledge base."}

===========================================================================
LIVE NEWS (from NewsAPI - if available)
===========================================================================
{news_context}

===========================================================================
YOUR TASK
===========================================================================

Analyze {jurisdiction}'s regulations ONLY as they relate to Zodia's actual business of serving INSTITUTIONAL clients. Do NOT include retail/consumer-focused rules unless they also catch institutional services.

PART 1 - BUSINESS ACTIVITY MAPPING (INSTITUTIONAL ONLY):
Walk through EACH of Zodia's business activities and identify which regulations apply when serving INSTITUTIONAL clients specifically:

1. OTC BROKERAGE FOR INSTITUTIONS: What license does Zodia need to broker OTC digital asset trades for institutional/professional clients in {jurisdiction}? Is there a carve-out or lighter regime for institutional-only OTC? Cite the specific law/regulation.

2. ELECTRONIC EXCHANGE FOR INSTITUTIONS: What license for operating an electronic trading platform for institutional clients? Do MTF/OTF/market operator rules apply differently for institutional-only platforms?

3. FIAT-TO-CRYPTO FOR INSTITUTIONS: What regulations govern fiat-to-crypto conversion when the client is an institution (not an individual)? Is the licensing requirement different?

4. NON-CUSTODIAL MODEL: How does {jurisdiction} regulate custody delegation when serving institutional clients who have their own custody arrangements?

5. INSTITUTIONAL CLIENT EXEMPTIONS: 
   - Does {jurisdiction} define "professional client", "qualified investor", "accredited investor", or "eligible counterparty"?
   - What are the thresholds/criteria?
   - Are VASPs/CASPs serving ONLY such clients exempt from full licensing?
   - Are there lighter AML/KYC requirements for institutional clients?
   - Does serving only institutions affect whether a foreign VASP needs a local license?

PART 2 - THE PERIMETER TEST (INSTITUTIONAL CONTEXT):
Zodia's legal position: if it has NO establishment, NO operational presence, and NO active solicitation in {jurisdiction}, it may be OUTSIDE the scope of {jurisdiction}'s law.

6. TERRITORIAL SCOPE OF THE LAW: 
   - Does {jurisdiction}'s crypto/VASP law apply based on where the SERVICE PROVIDER is located, or where the CLIENT is located?
   - Quote or cite the specific statutory language defining the law's territorial scope.
   - If Zodia has ZERO presence in {jurisdiction}, does the law still catch it?
   - Is there a "directed at" or "targeting" test?
   - IMPORTANTLY: Does the scope analysis differ when the client is an institution vs a retail consumer? (Many laws specifically target retail investor protection and don't catch institutional cross-border services.)
   - CONCLUSION: Can Zodia credibly argue it is OUTSIDE the regulatory perimeter of {jurisdiction} when serving only institutional clients?

7. REVERSE SOLICITATION (INSTITUTIONAL CONTEXT):
   - Is reverse solicitation recognized in {jurisdiction}? In STATUTE, REGULATION, or just GUIDANCE? Cite the exact source.
   - Is the reverse solicitation exemption BROADER for institutional/professional clients? (In many jurisdictions it is.)
   - Exact conditions when an institutional client initiates: documentation requirements, one-off vs ongoing relationship?
   - What BREAKS reverse solicitation? (marketing, local website, agents, conferences, proactive outreach)
   - Can Zodia provide ADDITIONAL services after initial reverse solicitation from an institutional client?
   - Enforcement: does the regulator pursue foreign VASPs serving institutional clients, or focus enforcement on retail?
   - Does {jurisdiction} have SPECIFIC crypto/VASP reverse solicitation rules, or only traditional finance rules? Do the traditional finance rules (which often have institutional exemptions) apply to VASPs?

8. DIRECT MARKET ACCESS FOR INSTITUTIONS: Can Zodia provide its electronic platform directly to institutional clients in {jurisdiction} from UK/Ireland/ADGM/Jersey? Rules on cross-border electronic access for professional/institutional participants?

PART 3 - ADVISORY (INSTITUTIONAL FOCUS):
9. CROSS-BORDER: Given that Zodia serves ONLY institutional clients, which approach for {jurisdiction}?
   - OUTSIDE PERIMETER (zero presence + institutional-only = likely outside scope)
   - REVERSE SOLICITATION (institutional clients have broader exemptions)
   - PASSPORTING (EU/MiCA from Ireland, if applicable)
   - LOCAL LICENSE NEEDED (even for institutional-only service?)
   - Which Zodia entity (UK, Ireland, ADGM, Jersey) is best positioned?

10. COMPLIANCE GUIDANCE: Clear, actionable verdict with one of:
    - SERVE (OUTSIDE PERIMETER) - Zodia is outside scope: zero presence + institutional-only + reverse solicitation
    - SERVE VIA REVERSE SOLICITATION ONLY - in scope but exemption available for institutional clients
    - SERVE VIA PASSPORTING - use Ireland entity under MiCA
    - SERVE WITH CONDITIONS - can serve institutional clients with specific restrictions
    - DECLINE - too risky even for institutional clients, local license required
    
    Plus: what must Zodia NEVER do to preserve its position?
    What triggers would bring Zodia INTO scope even for institutional services?

ONLY include ENACTED, ENFORCED, FINAL, IN FORCE regulations (as of February 2026).

11. SOURCES AND REFERENCES:
    For EVERY regulation, law, or guidance you cite, provide:
    - Full official name of the legislation/regulation
    - The regulatory body that issued it
    - Date enacted/effective
    - URL to the official government/regulator source where the text can be found (if known)
    - URL to the gazette, official journal, or regulatory register
    List ALL sources used in your analysis. Include URLs to regulator websites, official gazettes,
    and any publicly accessible regulatory texts. This is critical for verification.

---

**Format as JSON with these exact keys:**
{{
    "summary": "...",
    "high_level_risk_points": ["risk 1", "risk 2", ...],
    "regulatory_framework": "...",
    "virtual_asset_trading_platforms": "...",
    "stablecoin_regulation": "...",
    "store_of_value_facility_rules": "...",
    "regulatory_expectations_and_licensing_triggers": "...",
    "territorial_scope_and_perimeter_test": "...",
    "reverse_solicitation_and_direct_market_access": "...",
    "cross_border_client_advisory": "...",
    "compliance_guidance_and_recommendations": "...",
    "sources_and_references": ["source 1 with URL", "source 2 with URL", ...]
}}

Section details:
{sections_desc}

REMEMBER: Every answer must be through the lens of serving INSTITUTIONAL clients only. If a rule only applies to retail services, say so and explain why it does NOT apply to Zodia.

Be SPECIFIC. Cite laws by name and article. Quote the statutory scope. For the verdict, be unambiguous. For EVERY regulation cited, provide the URL to the official source where the text can be read."""

        try:
            messages = [
                SystemMessage(content=(
                    "You are a senior regulatory compliance analyst and cross-border legal advisor for Zodia Markets. "
                    "CRITICAL CONTEXT: Zodia serves ONLY INSTITUTIONAL clients (corporations, banks, funds, "
                    "professional investors). It does NOT serve retail individuals. "
                    "This means: (1) many retail-focused VASP/crypto rules may NOT apply, "
                    "(2) institutional/professional client exemptions may be available, "
                    "(3) reverse solicitation exemptions are often BROADER for institutional clients. "
                    "Your PRIMARY task is the PERIMETER TEST: determine if Zodia (with zero local presence, "
                    "zero solicitation, serving institutions only) falls OUTSIDE the territorial scope "
                    "of each jurisdiction's law. "
                    "Analyze: territorial scope (provider-location vs client-location test), "
                    "institutional exemptions, reverse solicitation (broader for institutions?), "
                    "what Zodia must NEVER do to stay outside scope. "
                    "Only reference enacted/enforced regulations. Cite specific legislation by name and article. "
                    "Give clear verdicts: SERVE (OUTSIDE PERIMETER) / SERVE VIA REVERSE SOLICITATION ONLY / "
                    "SERVE VIA PASSPORTING / SERVE WITH CONDITIONS / DECLINE. "
                    "Zodia is licensed ONLY in UK (FCA), Ireland (CBI), Abu Dhabi (ADGM), Jersey (JFSC)."
                )),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            response_text = response.content

            report = self._parse_json_response(response_text)
            if report:
                report["_raw_response"] = response_text[:500]
                report["_regulation_status"] = "enacted_enforced_only"
                # Ensure sources key exists
                if "sources_and_references" not in report:
                    report["sources_and_references"] = []
                return report
            else:
                return {
                    "summary": response_text[:2000],
                    "high_level_risk_points": [],
                    "regulatory_framework": "See summary",
                    "virtual_asset_trading_platforms": "See summary",
                    "stablecoin_regulation": "See summary",
                    "store_of_value_facility_rules": "See summary",
                    "regulatory_expectations_and_licensing_triggers": "See summary",
                    "territorial_scope_and_perimeter_test": "See summary",
                    "reverse_solicitation_and_direct_market_access": "See summary",
                    "cross_border_client_advisory": "See summary",
                    "compliance_guidance_and_recommendations": "See summary",
                    "sources_and_references": [],
                    "_raw_response": response_text[:500],
                    "_parse_error": "Could not parse structured JSON"
                }

        except Exception as e:
            return self._generate_fallback_report(jurisdiction, news_articles, registration_info, str(e))

    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """Extract and parse JSON from LLM response."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        for marker in ["```json", "```"]:
            if marker in text:
                start = text.find(marker) + len(marker)
                end = text.find("```", start)
                if end > start:
                    try:
                        return json.loads(text[start:end].strip())
                    except json.JSONDecodeError:
                        pass

        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start >= 0 and brace_end > brace_start:
            try:
                return json.loads(text[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass

        return None

    def _generate_fallback_report(
        self,
        jurisdiction: str,
        news_articles: List[Dict],
        registration_info: Optional[Dict],
        error: str = ""
    ) -> Dict:
        """Generate a basic report when LLM is unavailable."""
        news_summary = ""
        if news_articles:
            news_summary = "; ".join(a.get("title", "") for a in news_articles[:5])

        is_registered = registration_info is not None

        error_notice = (
            f"**ANALYSIS INCOMPLETE - FALLBACK REPORT**\n\n"
            f"The AI-powered analysis could not be completed for {jurisdiction}.\n\n"
            f"**Reason:** {error if error else 'LLM (DeepSeek) is unavailable or did not return a valid response.'}\n\n"
            f"**What this means:** This report contains only basic placeholder information, "
            f"NOT the full regulatory intelligence you would normally receive.\n\n"
            f"**To fix:** Ensure the DEEPSEEK_API_KEY is correctly configured in the app settings, "
            f"then try again."
        )

        return {
            "summary": error_notice,
            "high_level_risk_points": [
                "ANALYSIS INCOMPLETE - This is a fallback report, not a full analysis",
                f"Regulatory status in {jurisdiction} requires manual review",
                f"Error: {error[:200]}" if error else "LLM-powered analysis was unavailable"
            ],
            "regulatory_framework": f"**Requires full AI analysis.** Retry with a working DeepSeek API key.",
            "virtual_asset_trading_platforms": "**Requires full AI analysis.** Retry with a working DeepSeek API key.",
            "stablecoin_regulation": "**Requires full AI analysis.** Retry with a working DeepSeek API key.",
            "store_of_value_facility_rules": "**Requires full AI analysis.** Retry with a working DeepSeek API key.",
            "regulatory_expectations_and_licensing_triggers": "**Requires full AI analysis.** Retry with a working DeepSeek API key.",
            "territorial_scope_and_perimeter_test": (
                f"**UNKNOWN - Full AI analysis required.**\n\n"
                f"Manual legal review needed to determine whether {jurisdiction}'s law "
                "uses a provider-location test or client-location test, and whether Zodia with zero "
                "local presence falls outside the regulatory perimeter."
            ),
            "reverse_solicitation_and_direct_market_access": (
                f"**UNKNOWN - Full AI analysis required.**\n\n"
                f"Manual legal review needed for {jurisdiction}. "
                "Determine if reverse solicitation is permitted, whether in statute or guidance, "
                "and what conditions apply."
            ),
            "cross_border_client_advisory": (
                f"Zodia Markets {'IS' if is_registered else 'is NOT'} licensed in {jurisdiction}. "
                + (
                    "Clients can be onboarded under the existing registration."
                    if is_registered else
                    "**Full AI analysis required for cross-border advisory.** "
                    "Apply the perimeter test: with zero presence and zero solicitation, "
                    "determine if Zodia is outside scope. If not, assess reverse solicitation path."
                )
            ),
            "compliance_guidance_and_recommendations": (
                f"Standard onboarding applies." if is_registered else
                f"**VERDICT UNAVAILABLE - Full AI analysis required.**\n\n"
                f"RECOMMENDATION: Retry this analysis with a valid DeepSeek API key to get "
                f"a proper SERVE/DECLINE verdict for {jurisdiction}."
            ),
            "sources_and_references": [],
            "_news_headlines": news_summary,
            "_registration_info": registration_info,
            "_fallback": True,
            "_error": error
        }

    def format_report_markdown(self, result: Dict) -> str:
        """Format a jurisdiction result as a readable Markdown report."""
        jurisdiction = result.get("jurisdiction", "Unknown")
        report = result.get("report", {})
        reg_info = result.get("registration_info")

        lines = []
        lines.append(f"# {jurisdiction} - Zodia Markets Regulatory Intelligence")
        lines.append(f"*Generated: {result.get('timestamp', 'N/A')}*")
        
        # Data sources badge
        data_sources = result.get("data_sources", [])
        if data_sources:
            lines.append(f"*Data Sources: {" | ".join(data_sources)}*\n")
        else:
            lines.append("")

        # Registration badge
        if result.get("is_registered"):
            lines.append(f"**STATUS: REGISTERED** - {reg_info.get('entity', '')} ({reg_info.get('license_type', '')})")
            lines.append(f"Regulator: {reg_info.get('regulator', '')} | Ref: {reg_info.get('reference', '')}")
            lines.append(f"Granted: {reg_info.get('date_granted', '')} | Scope: {reg_info.get('scope', '')}\n")
        else:
            lines.append("**STATUS: NOT REGISTERED**\n")

        # 1. Summary
        lines.append("## 1. Regulatory Regime Summary")
        lines.append(report.get("summary", "Not available."))
        lines.append("")

        # 2. Risk Points
        lines.append("## 2. High-Level Risk Points for Zodia Markets")
        risks = report.get("high_level_risk_points", [])
        if isinstance(risks, list):
            for r in risks:
                lines.append(f"- {r}")
        else:
            lines.append(str(risks))
        lines.append("")

        # 3. Regulatory Framework
        lines.append("## 3. Regulatory Framework")
        lines.append(report.get("regulatory_framework", "Not available."))
        lines.append("")

        # 4. Trading Platforms
        lines.append("## 4. Virtual Asset Trading Platforms")
        lines.append(report.get("virtual_asset_trading_platforms", "Not available."))
        lines.append("")

        # 5. Stablecoin
        lines.append("## 5. Stablecoin & Fiat-Backed Token Regulation")
        lines.append(report.get("stablecoin_regulation", "Not available."))
        lines.append("")

        # 6. Store of Value
        lines.append("## 6. Store of Value Facility Rules")
        lines.append(report.get("store_of_value_facility_rules", "Not available."))
        lines.append("")

        # 7. Licensing Triggers
        lines.append("## 7. Regulatory Expectations & Licensing Triggers")
        lines.append(report.get("regulatory_expectations_and_licensing_triggers", "Not available."))
        lines.append("")

        # 8. Territorial Scope & Perimeter Test
        lines.append("## 8. Territorial Scope & Perimeter Test")
        lines.append("*If Zodia has ZERO presence and ZERO solicitation - is it outside scope?*\n")
        lines.append(report.get("territorial_scope_and_perimeter_test", "Not available."))
        lines.append("")

        # 9. Reverse Solicitation & Direct Market Access
        lines.append("## 9. Reverse Solicitation & Direct Market Access")
        lines.append("*Deep dive: conditions, documentation, what breaks it, enforcement risk*\n")
        lines.append(report.get("reverse_solicitation_and_direct_market_access", "Not available."))
        lines.append("")

        # 10. Cross-Border Client Advisory
        lines.append("## 10. Cross-Border Client Advisory")
        lines.append(f"*Can Zodia serve a client from {jurisdiction}?*\n")
        if result.get("is_registered"):
            lines.append(f"**ZODIA IS LICENSED HERE** - {reg_info.get('entity', '')}\n")
        else:
            lines.append(f"**ZODIA IS NOT LICENSED IN {jurisdiction.upper()}**\n")
        lines.append(report.get("cross_border_client_advisory", "Not available."))
        lines.append("")

        # 11. Compliance Guidance
        lines.append("## 11. Compliance Guidance & Recommendations")
        lines.append("*Verdict and actionable advice for Zodia Markets compliance team*\n")
        lines.append(report.get("compliance_guidance_and_recommendations", "Not available."))
        lines.append("")

        # 12. Sources & References (from LLM analysis)
        lines.append("## 12. Sources & References")
        lines.append("*Official regulatory sources cited in this analysis*\n")
        sources = report.get("sources_and_references", [])
        if isinstance(sources, list) and sources:
            for i, src in enumerate(sources, 1):
                lines.append(f"{i}. {src}")
        elif isinstance(sources, str) and sources:
            lines.append(sources)
        else:
            lines.append("No specific source URLs provided by analysis engine.")
        lines.append("")

        # 13. Live News Feed (from NewsAPI - LIVE data)
        news = result.get("news_articles", [])
        lines.append("## 13. Live Regulatory News Feed")
        lines.append(f"*LIVE data from NewsAPI - scraped at time of analysis ({result.get('timestamp', 'N/A')[:10]})*")
        lines.append(f"*{len(news)} articles found in the last 30 days*\n")
        if news:
            for i, article in enumerate(news[:15], 1):
                title = article.get('title', 'N/A')
                date = article.get('published_at', '')[:10]
                source = article.get('source', 'Unknown')
                url = article.get('url', '')
                author = article.get('author', '')
                content_preview = article.get('content', '')[:150]

                lines.append(f"### {i}. {title}")
                lines.append(f"**Source:** {source} | **Date:** {date}" + (f" | **Author:** {author}" if author else ""))
                if url:
                    lines.append(f"**URL:** {url}")
                if content_preview:
                    lines.append(f"> {content_preview}...")
                lines.append("")
        else:
            lines.append("No recent news articles found for this jurisdiction in the last 30 days.")
            lines.append("")

        # Data freshness disclaimer
        lines.append("---")
        lines.append("## Data Freshness & Methodology")
        lines.append("")
        lines.append("| Component | Source | Freshness |")
        lines.append("|-----------|--------|-----------|")
        kb_status = "Loaded" if result.get("kb_data_available") else "No data for this jurisdiction"
        news_status = f"{result.get('news_articles_found', 0)} articles" if result.get("newsapi_available") else "API expired/unavailable"
        lines.append(f"| Local Knowledge Base | 257 jurisdictions previously scraped | {kb_status} |")
        lines.append(f"| Live News Feed | NewsAPI | {news_status} |")
        lines.append("| Regulatory Analysis | DeepSeek LLM + KB + news context | LLM training data + injected context |")
        lines.append("| Source URLs | LLM-provided + NewsAPI URLs | Verify independently |")
        lines.append("")
        lines.append("**How this analysis works:**")
        lines.append("1. **Local Knowledge Base**: Previously scraped regulatory data from 257 jurisdictions is loaded and injected into the LLM as context")
        lines.append("2. **Live News** (if NewsAPI available): Real-time news articles are scraped and also injected as context")
        lines.append("3. **DeepSeek LLM**: Analyzes the jurisdiction using its training knowledge + both injected data sources")
        lines.append("4. The LLM's own knowledge covers regulations up to its training cutoff")
        lines.append("5. The knowledge base extends this with your previously researched data")
        lines.append("6. Live news (when available) catches the most recent developments")
        lines.append("- **Recommendation:** Cross-reference this report with official regulator websites for the most current information")
        lines.append("")
        lines.append(f"*Report generated: {result.get('timestamp', 'N/A')} | Duration: {result.get('duration_seconds', 0):.1f}s | Only enacted/enforced/final regulations*")

        return "\n".join(lines)

    def save_report(self, result: Dict, output_dir: str = None) -> str:
        """Save a jurisdiction report to file."""
        from pathlib import Path

        if output_dir is None:
            desktop = Path.home() / "Desktop"
            output_dir = desktop / "Zodia_Markets_Regulatory_Reports"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        jurisdiction = result.get("jurisdiction", "Unknown")
        safe_name = jurisdiction.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
        filename = f"Zodia_{safe_name}_Regulatory_Report.md"
        filepath = output_dir / filename

        markdown = self.format_report_markdown(result)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)

        # Also save raw JSON
        json_filepath = output_dir / f"Zodia_{safe_name}_data.json"
        with open(json_filepath, "w", encoding="utf-8") as f:
            clean_result = {k: v for k, v in result.items() if not k.startswith("_")}
            json.dump(clean_result, f, indent=2, ensure_ascii=False, default=str)

        return str(filepath)
