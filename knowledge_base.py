"""
Zodia Markets Local Regulatory Knowledge Base
Loads previously scraped and analyzed regulatory data from 257 jurisdictions.
Provides this data as context to the LLM, eliminating dependency on live news APIs.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class RegulatoryKnowledgeBase:
    """
    Local knowledge base built from previously scraped regulatory analysis.
    Contains data from 257 jurisdictions analyzed in the stablecoin regulation sweep.
    Used as context for the LLM when generating Zodia-specific reports.
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            base = Path(__file__).parent
            data_dir = base / "stablecoin_analysis_all_jurisdictions"
        else:
            data_dir = Path(data_dir)

        self.data_dir = data_dir
        self.jurisdiction_data: Dict[str, Dict] = {}
        self.jurisdiction_names: List[str] = []
        self._loaded = False

    def load(self, progress_callback=None) -> int:
        """Load all jurisdiction analysis files into memory."""
        if self._loaded:
            return len(self.jurisdiction_data)

        if not self.data_dir.exists():
            if progress_callback:
                progress_callback("Knowledge base directory not found.")
            return 0

        json_files = sorted(self.data_dir.glob("*_analysis.json"))
        loaded = 0

        for f in json_files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)

                jurisdiction = data.get("jurisdiction", "")
                if not jurisdiction:
                    # Extract from filename
                    jurisdiction = f.stem.replace("_analysis", "").replace("_", " ")

                self.jurisdiction_data[jurisdiction] = data
                loaded += 1

            except (json.JSONDecodeError, IOError) as e:
                if progress_callback:
                    progress_callback(f"  Warning: Could not load {f.name}: {e}")

        self.jurisdiction_names = sorted(self.jurisdiction_data.keys())
        self._loaded = True

        if progress_callback:
            progress_callback(f"Knowledge base loaded: {loaded} jurisdictions")

        return loaded

    def get_jurisdiction_context(self, jurisdiction: str) -> Optional[str]:
        """
        Get the previously analyzed regulatory context for a jurisdiction.
        Returns a formatted string suitable for injecting into the LLM prompt.
        """
        if not self._loaded:
            self.load()

        # Try exact match first
        data = self.jurisdiction_data.get(jurisdiction)

        # Try fuzzy matching
        if not data:
            jur_lower = jurisdiction.lower().strip()
            for name, d in self.jurisdiction_data.items():
                if name.lower().strip() == jur_lower:
                    data = d
                    break

        if not data:
            # Try partial match
            for name, d in self.jurisdiction_data.items():
                if jur_lower in name.lower() or name.lower() in jur_lower:
                    data = d
                    break

        if not data:
            return None

        # Build context string from the data
        parts = []
        parts.append(f"=== PREVIOUSLY RESEARCHED DATA FOR {jurisdiction.upper()} ===")
        parts.append(f"(Scraped: {data.get('timestamp', 'Unknown date')})\n")

        # Regulatory summary
        reg_summary = data.get("regulatory_summary", "")
        if reg_summary and len(reg_summary) > 50:
            # Truncate very long summaries to fit in context window
            if len(reg_summary) > 3000:
                reg_summary = reg_summary[:3000] + "... [truncated]"
            parts.append("REGULATORY SUMMARY:")
            parts.append(reg_summary)
            parts.append("")

        # Gap analysis
        gap = data.get("gap_analysis", {})
        if isinstance(gap, dict) and gap:
            gaps = gap.get("identified_gaps", [])
            if gaps:
                parts.append("IDENTIFIED REGULATORY GAPS:")
                for g in gaps[:5]:
                    parts.append(f"  - [{g.get('priority', 'N/A').upper()}] {g.get('regulatory_requirement', 'N/A')}")
                    parts.append(f"    Impact: {g.get('impact', 'N/A')[:200]}")
                parts.append("")

        # Recommendations
        recommendations = data.get("recommendations", [])
        if recommendations:
            parts.append("POLICY RECOMMENDATIONS:")
            for r in recommendations[:5]:
                if isinstance(r, dict):
                    parts.append(f"  - {r.get('title', 'N/A')}: {r.get('description', 'N/A')[:200]}")
                elif isinstance(r, str):
                    parts.append(f"  - {r[:200]}")
            parts.append("")

        # News that was captured
        news = data.get("news_articles", [])
        if not news:
            news = data.get("research_results", [])
        if news:
            parts.append(f"NEWS CAPTURED AT TIME OF SCRAPE ({len(news)} articles):")
            for n in news[:5]:
                if isinstance(n, dict):
                    parts.append(f"  - {n.get('title', 'N/A')} ({n.get('published_at', n.get('timestamp', 'N/A'))[:10]})")
                    url = n.get('url', '')
                    if url:
                        parts.append(f"    URL: {url}")
            parts.append("")

        result = "\n".join(parts)
        return result if len(result) > 100 else None

    def get_all_jurisdiction_names(self) -> List[str]:
        """Get all jurisdiction names in the knowledge base."""
        if not self._loaded:
            self.load()
        return self.jurisdiction_names

    def get_stats(self) -> Dict:
        """Get knowledge base statistics."""
        if not self._loaded:
            self.load()

        rich_count = 0
        thin_count = 0
        for name, data in self.jurisdiction_data.items():
            summary = data.get("regulatory_summary", "")
            if summary and len(summary) > 200 and "Limited research results" not in summary:
                rich_count += 1
            else:
                thin_count += 1

        return {
            "total_jurisdictions": len(self.jurisdiction_data),
            "rich_data": rich_count,
            "thin_data": thin_count,
            "data_dir": str(self.data_dir),
            "loaded": self._loaded
        }

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Simple keyword search across the knowledge base.
        Returns matching jurisdiction data.
        """
        if not self._loaded:
            self.load()

        query_lower = query.lower()
        results = []

        for name, data in self.jurisdiction_data.items():
            score = 0
            summary = data.get("regulatory_summary", "").lower()

            # Score based on keyword matches
            for word in query_lower.split():
                if word in name.lower():
                    score += 10
                if word in summary:
                    score += summary.count(word)

            if score > 0:
                results.append({
                    "jurisdiction": name,
                    "score": score,
                    "data": data
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
