"""
Zodia Markets Regulatory Intelligence Toolkit
Unified GUI for regulatory analysis, country-specific research,
VASP/stablecoin regulation tracking, and policy management.
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List

from regulatory_agent import RegulatoryAgent
from config import DEEPSEEK_API_KEY, JURISDICTIONS, REGULATORY_AREAS
from file_processor import FileProcessor
from regulatory_monitor import RegulatoryMonitor
from monitor_service import MonitoringService
from research_tools import ResearchTools
from zodia_config import (
    COMPANY_NAME,
    COMPANY_DESCRIPTION,
    ZODIA_REGISTERED_JURISDICTIONS,
    ZODIA_EU_MICA_JURISDICTIONS,
    ZODIA_ALL_RELEVANT_JURISDICTIONS,
    ZODIA_REGULATORY_FOCUS,
    ZODIA_REPORT_SECTIONS
)
from zodia_research import ZodiaResearchEngine


class RegulatoryAgentGUI:
    """Zodia Markets Regulatory Intelligence Toolkit"""

    def __init__(self, root):
        self.root = root
        self.root.title("Zodia Markets - Regulatory Intelligence Toolkit")
        self.root.geometry("1500x950")

        # Agent and services
        self.agent = None
        self.zodia_engine = None
        self.monitor = RegulatoryMonitor()
        self.monitoring_service = None

        # State
        self.current_results = None
        self.current_sources = []
        self.current_news = []
        self.uploaded_files = []

        # Build UI first, then init agent
        self.create_widgets()
        self.initialize_agent()

    # ========================================================================
    # INITIALIZATION
    # ========================================================================

    def initialize_agent(self):
        """Initialize the regulatory agent and Zodia research engine."""
        try:
            if not DEEPSEEK_API_KEY:
                self.status_label.config(text="API Key Missing", foreground="red")
                messagebox.showerror(
                    "API Key Missing",
                    "DEEPSEEK_API_KEY not found in .env file.\n\n"
                    "Please set DEEPSEEK_API_KEY in your .env file.\n"
                    "Get your API key from: https://platform.deepseek.com/api_keys"
                )
                return

            self.status_label.config(text="Initializing agent...", foreground="blue")
            self.root.update()

            self.agent = RegulatoryAgent()
            self.zodia_engine = ZodiaResearchEngine()
            self.status_label.config(text="Agent Ready | Zodia Markets Toolkit Active", foreground="green")
            self.run_button.config(state="normal")
            self.zodia_run_button.config(state="normal")
        except Exception as e:
            error_msg = f"Failed to initialize agent:\n{str(e)}"
            self.status_label.config(text="Agent Error", foreground="red")
            messagebox.showerror("Initialization Error", error_msg)
            print(f"Initialization error: {error_msg}")
            import traceback
            traceback.print_exc()

    # ========================================================================
    # WIDGET CREATION
    # ========================================================================

    def create_widgets(self):
        """Create the unified Zodia Markets GUI with tabs."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        title_label = ttk.Label(
            header_frame,
            text="Zodia Markets - Regulatory Intelligence Toolkit",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # Status
        self.status_label = ttk.Label(
            header_frame,
            text="Initializing...",
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Notebook tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Tab 1: Zodia Regulatory Research (main feature)
        self.zodia_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.zodia_tab, text="Zodia Regulatory Research")
        self.create_zodia_tab()

        # Tab 2: General Analysis
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="General Analysis")
        self.create_analysis_tab()

        # Tab 3: Results
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Results")
        self.create_results_tab()

        # Tab 4: Sources
        self.sources_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sources_tab, text="Sources")
        self.create_sources_tab()

        # Tab 5: Latest News
        self.news_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.news_tab, text="Latest News")
        self.create_news_tab()

        # Tab 6: Monitoring
        self.monitoring_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_tab, text="Monitoring")
        self.create_monitoring_tab()

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))

    # ========================================================================
    # TAB 1: ZODIA REGULATORY RESEARCH
    # ========================================================================

    def create_zodia_tab(self):
        """Create the Zodia Markets-specific regulatory research tab."""
        # Top: controls
        controls_frame = ttk.LabelFrame(self.zodia_tab, text="Zodia Markets Regulatory Research", padding="10")
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Row 1: Company info
        info_frame = ttk.Frame(controls_frame)
        info_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(
            info_frame,
            text="Zodia Markets | Standard Chartered-backed | VASP & Stablecoin Focus",
            font=("Arial", 10, "bold"),
            foreground="navy"
        ).pack(side=tk.LEFT)

        registered_count = len(ZODIA_REGISTERED_JURISDICTIONS)
        reg_names = ", ".join(ZODIA_REGISTERED_JURISDICTIONS.keys())
        ttk.Label(
            info_frame,
            text=f"Registered in {registered_count} jurisdictions: {reg_names}",
            font=("Arial", 9),
            foreground="green"
        ).pack(side=tk.RIGHT)

        # Row 2: Country selection
        country_frame = ttk.Frame(controls_frame)
        country_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(country_frame, text="Select Country:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))

        # Build sorted jurisdiction list with registered ones first
        registered_list = sorted(ZODIA_REGISTERED_JURISDICTIONS.keys())
        eu_list = sorted(set(ZODIA_EU_MICA_JURISDICTIONS) - set(registered_list))
        other_list = sorted(set(JURISDICTIONS) - set(registered_list) - set(eu_list))
        
        all_options = (
            ["-- All Registered Jurisdictions --", "-- All EU/MiCA Jurisdictions --", "-- All Jurisdictions --"]
            + [f"[REGISTERED] {j}" for j in registered_list]
            + [f"[EU/MiCA] {j}" for j in eu_list]
            + other_list
        )

        self.zodia_country_var = tk.StringVar(value=all_options[0])
        self.zodia_country_combo = ttk.Combobox(
            country_frame,
            textvariable=self.zodia_country_var,
            values=all_options,
            width=55,
            state="readonly"
        )
        self.zodia_country_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Search filter
        ttk.Label(country_frame, text="Quick filter:").pack(side=tk.LEFT, padx=(10, 5))
        self.zodia_filter_var = tk.StringVar()
        self.zodia_filter_entry = ttk.Entry(country_frame, textvariable=self.zodia_filter_var, width=20)
        self.zodia_filter_entry.pack(side=tk.LEFT)
        self.zodia_filter_var.trace_add("write", self._filter_countries)

        # Row 3: Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, pady=(0, 5))

        self.zodia_run_button = ttk.Button(
            button_frame,
            text="Run Zodia Regulatory Research",
            command=self.run_zodia_research,
            state="disabled"
        )
        self.zodia_run_button.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="Research All Registered",
            command=self.run_zodia_all_registered
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="Export Report",
            command=self.export_zodia_report
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Status labels for Zodia research
        self.zodia_status = ttk.Label(
            controls_frame,
            text="Select a country and click 'Run Zodia Regulatory Research'",
            font=("Arial", 9),
            foreground="gray"
        )
        self.zodia_status.pack(anchor=tk.W)

        # Bottom: Results area with structured sections
        results_paned = ttk.PanedWindow(self.zodia_tab, orient=tk.HORIZONTAL)
        results_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Left: Section navigator
        nav_frame = ttk.LabelFrame(results_paned, text="Report Sections", padding="5")
        results_paned.add(nav_frame, weight=1)

        self.zodia_section_listbox = tk.Listbox(nav_frame, font=("Arial", 10), width=35)
        self.zodia_section_listbox.pack(fill=tk.BOTH, expand=True)

        sections = [
            "1. Regulatory Regime Summary",
            "2. High-Level Risk Points",
            "3. Regulatory Framework",
            "4. Virtual Asset Trading Platforms",
            "5. Stablecoin & Fiat-Backed Tokens",
            "6. Store of Value Facility Rules",
            "7. Licensing Triggers & Expectations",
            "8. Reverse Solicitation & Direct Market Access",
            "9. Cross-Border Client Advisory",
            "10. Compliance Guidance & Recommendations",
            "11. Recent News & Developments",
            "FULL REPORT"
        ]
        for s in sections:
            self.zodia_section_listbox.insert(tk.END, s)
        
        self.zodia_section_listbox.bind("<<ListboxSelect>>", self._on_section_select)

        # Registration info panel
        reg_frame = ttk.LabelFrame(nav_frame, text="Zodia Registration Status", padding="5")
        reg_frame.pack(fill=tk.X, pady=(10, 0))

        self.zodia_reg_label = ttk.Label(
            reg_frame,
            text="Select a country to see registration status",
            font=("Arial", 9),
            wraplength=250
        )
        self.zodia_reg_label.pack(fill=tk.X)

        # Right: Content display
        content_frame = ttk.LabelFrame(results_paned, text="Regulatory Intelligence", padding="5")
        results_paned.add(content_frame, weight=3)

        self.zodia_content_text = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.zodia_content_text.pack(fill=tk.BOTH, expand=True)

        # Welcome message
        self.zodia_content_text.insert("1.0", self._get_welcome_message())

    def _get_welcome_message(self) -> str:
        """Return the welcome/instructions message."""
        lines = []
        lines.append("=" * 70)
        lines.append("ZODIA MARKETS REGULATORY INTELLIGENCE TOOLKIT")
        lines.append("=" * 70)
        lines.append("")
        lines.append("This toolkit is specifically designed for Zodia Markets to research")
        lines.append("VASP licensing, stablecoin regulation, and virtual asset trading")
        lines.append("platform rules across jurisdictions.")
        lines.append("")
        lines.append("HOW TO USE:")
        lines.append("-" * 40)
        lines.append("1. Select a country from the dropdown (or use the filter)")
        lines.append("2. Click 'Run Zodia Regulatory Research'")
        lines.append("3. Browse report sections in the left panel")
        lines.append("4. Export reports to Desktop")
        lines.append("")
        lines.append("REGISTERED JURISDICTIONS:")
        lines.append("-" * 40)
        for jur, info in ZODIA_REGISTERED_JURISDICTIONS.items():
            lines.append(f"  {jur}")
            lines.append(f"    Entity: {info['entity']}")
            lines.append(f"    Regulator: {info['regulator']}")
            lines.append(f"    License: {info['license_type']} ({info['reference']})")
            lines.append(f"    Granted: {info['date_granted']}")
            lines.append("")
        lines.append("REPORT FOCUS:")
        lines.append("-" * 40)
        lines.append("  - Only ENACTED / ENFORCED / FINAL regulations")
        lines.append("  - VASP licensing & authorization requirements")
        lines.append("  - Stablecoin issuance & fiat-backed token rules")
        lines.append("  - Store of value facility rules")
        lines.append("  - Virtual asset trading platform regulation")
        lines.append("  - Regulatory expectations & licensing triggers")
        lines.append("  - Risk points specific to Zodia Markets")
        lines.append("")
        lines.append("ADVISORY & COMPLIANCE GUIDANCE:")
        lines.append("-" * 40)
        lines.append("  - Cross-border client onboarding advisory")
        lines.append("  - Can Zodia serve a client from this jurisdiction?")
        lines.append("  - Does the country require a local VASP license?")
        lines.append("  - Reverse solicitation exemptions")
        lines.append("  - EU/MiCA passporting analysis (via Ireland)")
        lines.append("  - Which Zodia entity should serve the client?")
        lines.append("  - Actionable compliance recommendations")
        lines.append("  - SERVE / SERVE WITH CONDITIONS / DECLINE guidance")
        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)

    def _filter_countries(self, *args):
        """Filter the country dropdown based on text input."""
        filter_text = self.zodia_filter_var.get().lower()
        if not filter_text:
            return

        registered_list = sorted(ZODIA_REGISTERED_JURISDICTIONS.keys())
        eu_list = sorted(set(ZODIA_EU_MICA_JURISDICTIONS) - set(registered_list))
        other_list = sorted(set(JURISDICTIONS) - set(registered_list) - set(eu_list))

        all_countries = registered_list + eu_list + other_list
        matches = [c for c in all_countries if filter_text in c.lower()]

        if matches:
            # Update combobox values
            display = []
            for c in matches:
                if c in ZODIA_REGISTERED_JURISDICTIONS:
                    display.append(f"[REGISTERED] {c}")
                elif c in ZODIA_EU_MICA_JURISDICTIONS:
                    display.append(f"[EU/MiCA] {c}")
                else:
                    display.append(c)
            self.zodia_country_combo['values'] = display
            if display:
                self.zodia_country_var.set(display[0])

    def _get_selected_country(self) -> str:
        """Extract the actual country name from the combo selection."""
        selection = self.zodia_country_var.get()
        # Strip prefixes
        for prefix in ["[REGISTERED] ", "[EU/MiCA] "]:
            if selection.startswith(prefix):
                return selection[len(prefix):]
        return selection

    def _on_section_select(self, event):
        """Handle section selection in the listbox."""
        if not hasattr(self, '_current_zodia_report'):
            return
        
        selection = self.zodia_section_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        report = self._current_zodia_report
        
        section_keys = [
            "summary",
            "high_level_risk_points",
            "regulatory_framework",
            "virtual_asset_trading_platforms",
            "stablecoin_regulation",
            "store_of_value_facility_rules",
            "regulatory_expectations_and_licensing_triggers",
            "reverse_solicitation_and_direct_market_access",
            "cross_border_client_advisory",
            "compliance_guidance_and_recommendations",
            "_news",
            "_full"
        ]
        
        if idx >= len(section_keys):
            return
        
        key = section_keys[idx]
        
        self.zodia_content_text.config(state=tk.NORMAL)
        self.zodia_content_text.delete("1.0", tk.END)
        
        if key == "_full":
            # Show full markdown report
            if hasattr(self, '_current_zodia_result'):
                md = self.zodia_engine.format_report_markdown(self._current_zodia_result)
                self.zodia_content_text.insert("1.0", md)
            else:
                self.zodia_content_text.insert("1.0", "Run a research first.")
        elif key == "_news":
            # Show news
            if hasattr(self, '_current_zodia_result'):
                news = self._current_zodia_result.get("news_articles", [])
                if news:
                    lines = [f"Recent News for {self._current_zodia_result.get('jurisdiction', '')}",
                             "=" * 60, ""]
                    for i, a in enumerate(news, 1):
                        lines.append(f"{i}. {a.get('title', 'N/A')}")
                        lines.append(f"   Date: {a.get('published_at', 'N/A')[:10]}")
                        lines.append(f"   Source: {a.get('source', 'N/A')}")
                        lines.append(f"   URL: {a.get('url', 'N/A')}")
                        content = a.get('content', '') or a.get('description', '')
                        if content:
                            lines.append(f"   {content[:200]}...")
                        lines.append("")
                    self.zodia_content_text.insert("1.0", "\n".join(lines))
                else:
                    self.zodia_content_text.insert("1.0", "No recent news articles found.")
            else:
                self.zodia_content_text.insert("1.0", "Run a research first.")
        else:
            # Show specific section
            value = report.get(key, "Not available.")
            section_name = self.zodia_section_listbox.get(idx)
            
            lines = [section_name, "=" * len(section_name), ""]
            if isinstance(value, list):
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(str(value))
            
            self.zodia_content_text.insert("1.0", "\n".join(lines))

    # ========================================================================
    # ZODIA RESEARCH ACTIONS
    # ========================================================================

    def run_zodia_research(self):
        """Run Zodia-specific regulatory research for selected country."""
        if not self.zodia_engine:
            messagebox.showerror("Error", "Zodia research engine not initialized.")
            return

        selection = self._get_selected_country()

        if selection.startswith("-- All Registered"):
            self.run_zodia_all_registered()
            return
        elif selection.startswith("-- All EU"):
            self._run_zodia_batch(ZODIA_EU_MICA_JURISDICTIONS, "EU/MiCA")
            return
        elif selection.startswith("-- All Jurisdictions"):
            self._run_zodia_batch(JURISDICTIONS, "All")
            return

        country = selection
        if not country:
            messagebox.showwarning("Warning", "Please select a country.")
            return

        self.zodia_run_button.config(state="disabled")
        self.progress.start()
        self.zodia_status.config(text=f"Researching {country}...", foreground="blue")
        self.zodia_content_text.config(state=tk.NORMAL)
        self.zodia_content_text.delete("1.0", tk.END)
        self.zodia_content_text.insert("1.0", f"Researching {country}...\n\nThis may take 30-60 seconds.\n\n"
                                        f"The research will cover:\n"
                                        f"- VASP licensing requirements\n"
                                        f"- Stablecoin regulation\n"
                                        f"- Virtual asset trading platform rules\n"
                                        f"- Store of value facility rules\n"
                                        f"- Licensing triggers\n"
                                        f"- Recent news\n")

        def do_research():
            try:
                result = self.zodia_engine.research_jurisdiction(
                    country,
                    include_news=True,
                    progress_callback=lambda msg: self.root.after(
                        0, lambda m=msg: self.zodia_status.config(text=m, foreground="blue")
                    )
                )
                self.root.after(0, lambda: self._display_zodia_result(result))
            except Exception as e:
                self.root.after(0, lambda: self._display_zodia_error(str(e)))

        thread = threading.Thread(target=do_research, daemon=True)
        thread.start()

    def run_zodia_all_registered(self):
        """Research all registered jurisdictions."""
        self._run_zodia_batch(
            list(ZODIA_REGISTERED_JURISDICTIONS.keys()),
            "Registered"
        )

    def _run_zodia_batch(self, jurisdictions: list, label: str):
        """Run batch research across multiple jurisdictions."""
        if not self.zodia_engine:
            messagebox.showerror("Error", "Engine not initialized.")
            return

        total = len(jurisdictions)
        if total > 30:
            if not messagebox.askyesno(
                "Large Batch",
                f"This will research {total} jurisdictions.\n"
                f"Estimated time: {total * 45 // 60} minutes.\n\nContinue?"
            ):
                return

        self.zodia_run_button.config(state="disabled")
        self.progress.start()

        def do_batch():
            results = {}
            for i, jur in enumerate(jurisdictions, 1):
                self.root.after(
                    0,
                    lambda j=jur, n=i: self.zodia_status.config(
                        text=f"[{n}/{total}] Researching {j}...", foreground="blue"
                    )
                )
                try:
                    results[jur] = self.zodia_engine.research_jurisdiction(jur, include_news=True)
                except Exception as e:
                    results[jur] = {"jurisdiction": jur, "status": "error", "error": str(e)}

                if i < total:
                    import time
                    time.sleep(3)

            self.root.after(0, lambda: self._display_zodia_batch_results(results, label))

        thread = threading.Thread(target=do_batch, daemon=True)
        thread.start()

    def _display_zodia_result(self, result: Dict):
        """Display a single jurisdiction result."""
        self.progress.stop()
        self.zodia_run_button.config(state="normal")

        jurisdiction = result.get("jurisdiction", "Unknown")
        report = result.get("report", {})

        self._current_zodia_result = result
        self._current_zodia_report = report

        # Update registration status label
        if result.get("is_registered"):
            reg = result["registration_info"]
            self.zodia_reg_label.config(
                text=f"REGISTERED\n{reg.get('entity', '')}\n"
                     f"{reg.get('regulator', '')} | {reg.get('reference', '')}\n"
                     f"Granted: {reg.get('date_granted', '')}",
                foreground="green"
            )
        else:
            self.zodia_reg_label.config(
                text="NOT REGISTERED in this jurisdiction",
                foreground="red"
            )

        self.zodia_status.config(
            text=f"Research complete for {jurisdiction} | "
                 f"News: {result.get('news_articles_found', 0)} articles | "
                 f"Duration: {result.get('duration_seconds', 0):.1f}s",
            foreground="green"
        )

        # Display full report by default
        md = self.zodia_engine.format_report_markdown(result)
        self.zodia_content_text.config(state=tk.NORMAL)
        self.zodia_content_text.delete("1.0", tk.END)
        self.zodia_content_text.insert("1.0", md)

        # Auto-save
        try:
            filepath = self.zodia_engine.save_report(result)
            self.zodia_status.config(
                text=self.zodia_status.cget("text") + f" | Saved: {filepath}",
                foreground="green"
            )
        except Exception as e:
            print(f"Save warning: {e}")

    def _display_zodia_batch_results(self, results: Dict, label: str):
        """Display batch research results."""
        self.progress.stop()
        self.zodia_run_button.config(state="normal")

        success = sum(1 for r in results.values() if r.get("status") == "success")
        errors = sum(1 for r in results.values() if r.get("status") == "error")

        self.zodia_status.config(
            text=f"Batch complete ({label}): {success} success, {errors} errors out of {len(results)}",
            foreground="green" if errors == 0 else "orange"
        )

        # Build summary
        lines = []
        lines.append(f"{'=' * 70}")
        lines.append(f"ZODIA MARKETS BATCH REGULATORY RESEARCH ({label})")
        lines.append(f"{'=' * 70}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Jurisdictions: {len(results)} | Success: {success} | Errors: {errors}")
        lines.append("")

        for jur, result in results.items():
            lines.append(f"\n{'=' * 70}")
            if result.get("status") == "success":
                md = self.zodia_engine.format_report_markdown(result)
                lines.append(md)
            else:
                lines.append(f"# {jur} - ERROR")
                lines.append(f"Error: {result.get('error', 'Unknown error')}")
            lines.append("")

        self.zodia_content_text.config(state=tk.NORMAL)
        self.zodia_content_text.delete("1.0", tk.END)
        self.zodia_content_text.insert("1.0", "\n".join(lines))

        # Save all reports
        try:
            for jur, result in results.items():
                if result.get("status") == "success":
                    self.zodia_engine.save_report(result)
            messagebox.showinfo(
                "Batch Complete",
                f"Research complete for {success} jurisdictions.\n"
                f"Reports saved to Desktop/Zodia_Markets_Regulatory_Reports/"
            )
        except Exception as e:
            print(f"Batch save warning: {e}")

    def _display_zodia_error(self, error_msg: str):
        """Display Zodia research error."""
        self.progress.stop()
        self.zodia_run_button.config(state="normal")
        self.zodia_status.config(text=f"Error: {error_msg[:80]}", foreground="red")
        self.zodia_content_text.config(state=tk.NORMAL)
        self.zodia_content_text.delete("1.0", tk.END)
        self.zodia_content_text.insert("1.0", f"ERROR\n{'=' * 40}\n\n{error_msg}")

    def export_zodia_report(self):
        """Export current Zodia report to file."""
        content = self.zodia_content_text.get("1.0", tk.END).strip()
        if not content or content.startswith("="):
            messagebox.showwarning("Warning", "No report to export. Run a research first.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All", "*.*")],
            initialfile=f"Zodia_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Exported", f"Report saved to:\n{filepath}")

    # ========================================================================
    # TAB 2: GENERAL ANALYSIS
    # ========================================================================

    def create_analysis_tab(self):
        """Create the general analysis tab with query input and results."""
        paned = ttk.PanedWindow(self.analysis_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Input
        input_frame = ttk.LabelFrame(paned, text="Query Input", padding="10")
        paned.add(input_frame, weight=1)

        ttk.Label(input_frame, text="Regulatory Topic/Query:").pack(anchor=tk.W, pady=(0, 5))
        self.query_entry = ttk.Entry(input_frame, width=40)
        self.query_entry.pack(fill=tk.X, pady=(0, 10))
        self.query_entry.insert(0, "stablecoin regulation")

        ttk.Label(input_frame, text="Jurisdiction (Optional):").pack(anchor=tk.W, pady=(0, 5))
        self.jurisdiction_entry = ttk.Entry(input_frame, width=40)
        self.jurisdiction_entry.pack(fill=tk.X, pady=(0, 10))

        # File upload
        ttk.Label(input_frame, text="Current Company Policies (Optional):").pack(anchor=tk.W, pady=(0, 5))

        file_button_frame = ttk.Frame(input_frame)
        file_button_frame.pack(fill=tk.X, pady=(0, 5))

        self.upload_button = ttk.Button(file_button_frame, text="Upload Policy Files", command=self.upload_policy_files)
        self.upload_button.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_files_button = ttk.Button(file_button_frame, text="Clear Files", command=self.clear_uploaded_files)
        self.clear_files_button.pack(side=tk.LEFT)

        self.uploaded_files_label = ttk.Label(input_frame, text="No files uploaded", font=("Arial", 8), foreground="gray")
        self.uploaded_files_label.pack(anchor=tk.W, pady=(0, 5))

        ttk.Label(input_frame, text="Or paste policies manually:").pack(anchor=tk.W, pady=(0, 5))
        self.policies_text = scrolledtext.ScrolledText(input_frame, width=40, height=15)
        self.policies_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.run_button = ttk.Button(
            input_frame, text="Run Analysis", command=self.run_analysis,
            state="normal" if self.agent else "disabled"
        )
        self.run_button.pack(pady=10)

        # Right panel - Quick Results
        results_frame = ttk.LabelFrame(paned, text="Quick Results", padding="10")
        paned.add(results_frame, weight=2)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)

    # ========================================================================
    # TAB 3: RESULTS
    # ========================================================================

    def create_results_tab(self):
        """Create detailed results tab."""
        results_frame = ttk.Frame(self.results_tab)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.detailed_results_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, font=("Consolas", 9), height=30
        )
        self.detailed_results_text.pack(fill=tk.BOTH, expand=True)
        self.detailed_results_text.insert("1.0",
            "No results yet. Run an analysis to see detailed results here.\n\n"
            "Results will show:\n"
            "- Regulatory summaries\n"
            "- Gap analysis with priority levels\n"
            "- Policy updates and implementations\n"
            "- Detailed breakdown by jurisdiction"
        )
        self.detailed_results_text.config(state=tk.DISABLED)

    # ========================================================================
    # TAB 4: SOURCES
    # ========================================================================

    def create_sources_tab(self):
        """Create sources tab."""
        sources_frame = ttk.Frame(self.sources_tab)
        sources_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.sources_text = scrolledtext.ScrolledText(
            sources_frame, wrap=tk.WORD, font=("Consolas", 9), height=30
        )
        self.sources_text.pack(fill=tk.BOTH, expand=True)
        self.sources_text.insert("1.0", "No sources yet. Sources from regulatory analysis will appear here.")
        self.sources_text.config(state=tk.DISABLED)

    # ========================================================================
    # TAB 5: LATEST NEWS
    # ========================================================================

    def create_news_tab(self):
        """Create latest news tab."""
        news_frame = ttk.Frame(self.news_tab)
        news_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(news_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="Refresh Latest News", command=self.refresh_news).pack(side=tk.LEFT)

        self.news_text = scrolledtext.ScrolledText(
            news_frame, wrap=tk.WORD, font=("Consolas", 9), height=30
        )
        self.news_text.pack(fill=tk.BOTH, expand=True)
        self.news_text.insert("1.0", "Click 'Refresh Latest News' to fetch latest crypto regulation news.")
        self.news_text.config(state=tk.DISABLED)

    # ========================================================================
    # TAB 6: MONITORING
    # ========================================================================

    def create_monitoring_tab(self):
        """Create monitoring dashboard tab."""
        monitoring_frame = ttk.Frame(self.monitoring_tab)
        monitoring_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status
        status_frame = ttk.LabelFrame(monitoring_frame, text="Monitoring Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.monitoring_status_label = ttk.Label(
            status_frame, text="Monitoring: INACTIVE",
            font=("Arial", 12, "bold"), foreground="red"
        )
        self.monitoring_status_label.pack()

        stats_frame = ttk.Frame(status_frame)
        stats_frame.pack(fill=tk.X, pady=5)

        self.jurisdictions_label = ttk.Label(
            stats_frame, text=f"Jurisdictions: {len(JURISDICTIONS)}", font=("Arial", 10)
        )
        self.jurisdictions_label.pack(side=tk.LEFT, padx=10)

        self.topics_label = ttk.Label(
            stats_frame, text=f"Topics: {len(REGULATORY_AREAS)}", font=("Arial", 10)
        )
        self.topics_label.pack(side=tk.LEFT, padx=10)

        total = len(JURISDICTIONS) * len(REGULATORY_AREAS)
        self.total_label = ttk.Label(
            stats_frame, text=f"Total Regulations: {total}", font=("Arial", 10, "bold")
        )
        self.total_label.pack(side=tk.LEFT, padx=10)

        # Controls
        controls_frame = ttk.Frame(monitoring_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(controls_frame, text="Start Monitoring", command=self.start_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Stop Monitoring", command=self.stop_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Check Now", command=self.run_monitor_once).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="View Notifications", command=self.view_notifications).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="View Revisions", command=self.view_revisions).pack(side=tk.LEFT, padx=5)

        # Activity log
        log_frame = ttk.LabelFrame(monitoring_frame, text="Live Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.activity_log = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, font=("Consolas", 9), height=20
        )
        self.activity_log.pack(fill=tk.BOTH, expand=True)

        self.last_update_label = ttk.Label(
            monitoring_frame, text="Last update: Never", font=("Arial", 8), foreground="gray"
        )
        self.last_update_label.pack(pady=5)

    # ========================================================================
    # GENERAL ANALYSIS ACTIONS
    # ========================================================================

    def run_analysis(self):
        """Run the general regulatory analysis."""
        if not self.agent:
            messagebox.showerror("Error", "Agent not initialized.")
            return

        query = self.query_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a query.")
            return

        jurisdiction = self.jurisdiction_entry.get().strip()
        current_policies = self.get_policies_content()

        self.run_button.config(state="disabled")
        self.progress.start()
        self.status_label.config(text="Running analysis...", foreground="blue")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "Running analysis...\nThis may take a few minutes.\n\n")

        thread = threading.Thread(
            target=self._run_analysis_thread,
            args=(query, jurisdiction, current_policies),
            daemon=True
        )
        thread.start()

    def _run_analysis_thread(self, query, jurisdiction, current_policies):
        """Run analysis in background thread."""
        try:
            results = self.agent.run(
                query=query, jurisdiction=jurisdiction, current_policies=current_policies
            )
            self.root.after(0, self._display_results, results)
        except Exception as e:
            self.root.after(0, self._display_error, f"Error during analysis:\n{str(e)}")

    def _display_results(self, results):
        """Display analysis results."""
        self.progress.stop()
        self.run_button.config(state="normal")
        self.status_label.config(text="Analysis Complete", foreground="green")

        self.current_results = results
        if results.get("sources"):
            self.current_sources = results["sources"]

        self.results_text.delete("1.0", tk.END)
        self.detailed_results_text.config(state=tk.NORMAL)
        self.detailed_results_text.delete("1.0", tk.END)
        self.update_sources_display()

        output = []
        output.append("=" * 70)
        output.append("REGULATORY ANALYSIS RESULTS")
        output.append("=" * 70)
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        if results.get("regulatory_summary"):
            output.extend(["\n" + "-" * 70, "REGULATORY REQUIREMENTS SUMMARY", "-" * 70,
                          results["regulatory_summary"], ""])

        if results.get("gap_analysis"):
            gap_analysis = results["gap_analysis"]
            output.extend(["\n" + "-" * 70, "GAP ANALYSIS", "-" * 70])
            priority_levels = gap_analysis.get("priority_levels", {})
            if priority_levels:
                output.append(f"\nCritical: {len(priority_levels.get('critical', []))}")
                output.append(f"High: {len(priority_levels.get('high', []))}")
                output.append(f"Medium: {len(priority_levels.get('medium', []))}")
                output.append(f"Low: {len(priority_levels.get('low', []))}")
                critical = priority_levels.get("critical", [])
                if critical:
                    output.append("\nCritical Priority Gaps:")
                    for i, gap in enumerate(critical[:5], 1):
                        output.append(f"\n{i}. {gap.get('gap_id', f'GAP-{i:03d}')}")
                        output.append(f"   Requirement: {gap.get('regulatory_requirement', 'N/A')[:100]}...")
                        output.append(f"   Recommendation: {gap.get('recommendation', 'N/A')[:100]}...")
            output.append("")

        if results.get("policy_updates"):
            policy_updates = results["policy_updates"]
            output.extend(["\n" + "-" * 70, "POLICY UPDATES", "-" * 70])
            output.append(f"New Policies Required: {len(policy_updates.get('new_policies', []))}")
            output.append(f"Policies to Modify: {len(policy_updates.get('modified_policies', []))}")
            output.append("")

        if results.get("policy_implementation") and results["policy_implementation"].get("files_created"):
            impl = results["policy_implementation"]
            output.extend(["\n" + "-" * 70, "POLICY IMPLEMENTATION", "-" * 70])
            output.append(f"Implemented {len(impl.get('implemented_policies', []))} policies")
            output.append(f"Saved to: {impl.get('output_directory', 'N/A')}")
            output.append(f"Summary: {impl.get('summary_file', 'N/A')}")
            output.append("\nImplemented Policies:")
            for policy in impl.get("implemented_policies", []):
                output.append(f"  - {policy.get('gap_id', 'N/A')} - {policy.get('filename', 'N/A')}")
            output.append("")

        if results.get("sources"):
            sources = results["sources"]
            output.extend(["\n" + "-" * 70, f"SOURCES ({len(sources)} total)", "-" * 70])
            for i, source in enumerate(sources[:10], 1):
                output.append(f"{i}. {source.get('title', 'N/A')}")
                output.append(f"   {source.get('url', 'N/A')}")
            output.append("")

        if results.get("report"):
            output.extend(["\n" + "=" * 70, "FULL REPORT", "=" * 70, results["report"]])

        if results.get("error"):
            output.extend(["\n" + "=" * 70, "ERRORS", "=" * 70, results["error"]])

        self.results_text.insert("1.0", "\n".join(output))
        self.detailed_results_text.insert("1.0", "\n".join(output))
        self.detailed_results_text.config(state=tk.DISABLED)

        success_msg = "Analysis complete!"
        if results.get("policy_implementation") and results["policy_implementation"].get("files_created"):
            impl = results["policy_implementation"]
            success_msg += f"\n\nImplemented {len(impl.get('implemented_policies', []))} policies"
            success_msg += f"\nPolicies saved to Desktop/Regulatory_Policies/"

        if results.get("report"):
            filename = f"regulatory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(results["report"])
                success_msg += f"\n\nReport saved to: {filename}"
            except Exception as e:
                success_msg += f"\n\nFailed to save report: {str(e)}"

        messagebox.showinfo("Success", success_msg)

    def _display_error(self, error_msg):
        """Display error message."""
        self.progress.stop()
        self.run_button.config(state="normal")
        self.status_label.config(text="Analysis Failed", foreground="red")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"ERROR:\n\n{error_msg}")
        messagebox.showerror("Analysis Error", error_msg)

    # ========================================================================
    # FILE UPLOAD
    # ========================================================================

    def upload_policy_files(self):
        """Upload policy files."""
        filetypes = [
            ("All supported", "*.pdf;*.docx;*.doc;*.txt;*.md;*.xlsx;*.xls;*.csv"),
            ("PDF", "*.pdf"), ("Word", "*.docx;*.doc"), ("Text", "*.txt;*.md"),
            ("Excel", "*.xlsx;*.xls"), ("CSV", "*.csv"), ("All", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Select Policy Files", filetypes=filetypes)
        if files:
            self.uploaded_files.extend(files)
            file_names = [os.path.basename(f) for f in self.uploaded_files]
            if len(file_names) <= 3:
                self.uploaded_files_label.config(text=f"Files: {', '.join(file_names)}", foreground="green")
            else:
                self.uploaded_files_label.config(text=f"{len(file_names)} files uploaded", foreground="green")

    def clear_uploaded_files(self):
        """Clear uploaded files."""
        self.uploaded_files = []
        self.uploaded_files_label.config(text="No files uploaded", foreground="gray")
        self.policies_text.delete("1.0", tk.END)

    def get_policies_content(self) -> str:
        """Get combined content from uploaded files and text area."""
        content_parts = []
        if self.uploaded_files:
            try:
                file_content = FileProcessor.process_multiple_files(self.uploaded_files)
                content_parts.append(file_content)
            except Exception as e:
                messagebox.showwarning("File Processing Warning", f"Error processing files: {str(e)}")

        text_content = self.policies_text.get("1.0", tk.END).strip()
        if text_content:
            if content_parts:
                content_parts.append("\n\n--- Manual Input ---\n\n")
            content_parts.append(text_content)

        return "\n".join(content_parts) if content_parts else ""

    # ========================================================================
    # SOURCES & NEWS
    # ========================================================================

    def update_sources_display(self):
        """Update sources tab."""
        self.sources_text.config(state=tk.NORMAL)
        self.sources_text.delete("1.0", tk.END)

        if not self.current_sources:
            self.sources_text.insert("1.0", "No sources available yet.")
        else:
            output = [f"Found {len(self.current_sources)} unique sources\n", "=" * 70 + "\n"]
            source_types = {}
            for source in self.current_sources:
                st = source.get("source_type", "unknown")
                source_types.setdefault(st, []).append(source)
            for st, sources in source_types.items():
                output.append(f"\n{st.upper()} Sources ({len(sources)}):")
                output.append("-" * 70)
                for i, source in enumerate(sources[:20], 1):
                    output.append(f"\n{i}. {source.get('title', 'N/A')}")
                    output.append(f"   {source.get('url', 'N/A')}")
                if len(sources) > 20:
                    output.append(f"\n... and {len(sources) - 20} more")
                output.append("")
            self.sources_text.insert("1.0", "\n".join(output))

        self.sources_text.config(state=tk.DISABLED)

    def refresh_news(self):
        """Refresh latest news."""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete("1.0", tk.END)
        self.news_text.insert("1.0", "Fetching latest news...\n")
        self.news_text.config(state=tk.DISABLED)

        def fetch_news():
            try:
                tools = ResearchTools()
                queries = ["cryptocurrency regulation", "crypto regulation",
                          "digital asset regulation", "stablecoin regulation",
                          "VASP regulation", "Zodia Markets"]
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
                    except Exception:
                        pass
                all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
                self.current_news = all_articles
                self.root.after(0, lambda: self.display_news(all_articles))
            except Exception as e:
                self.root.after(0, lambda: self.display_news_error(str(e)))

        thread = threading.Thread(target=fetch_news, daemon=True)
        thread.start()

    def display_news(self, articles):
        """Display news articles."""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete("1.0", tk.END)

        if not articles:
            self.news_text.insert("1.0",
                "No news articles found. Check:\n- API key in .env\n- Network connectivity"
            )
        else:
            output = [f"Found {len(articles)} latest news articles (last 7 days)\n", "=" * 70 + "\n"]
            for i, article in enumerate(articles[:30], 1):
                output.append(f"\n{i}. {article.get('title', 'N/A')}")
                output.append("-" * 70)
                content = article.get('content', '') or article.get('description', '')
                if content:
                    output.append(f"\n{content[:300]}{'...' if len(content) > 300 else ''}\n")
                output.append(f"Date: {article.get('published_at', 'N/A')[:10] if article.get('published_at') else 'N/A'}")
                output.append(f"Source: {article.get('source', 'N/A')}")
                if article.get('author'):
                    output.append(f"Author: {article.get('author', 'N/A')}")
                output.append(f"URL: {article.get('url', 'N/A')}")
                output.append("")
            if len(articles) > 30:
                output.append(f"\n... and {len(articles) - 30} more articles")
            self.news_text.insert("1.0", "\n".join(output))

        self.news_text.config(state=tk.DISABLED)

    def display_news_error(self, error_msg):
        """Display news error."""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete("1.0", tk.END)
        self.news_text.insert("1.0", f"ERROR fetching news:\n\n{error_msg}")
        self.news_text.config(state=tk.DISABLED)

    # ========================================================================
    # MONITORING
    # ========================================================================

    def log_activity(self, message):
        """Log activity to monitoring dashboard."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_log.see(tk.END)

    def start_monitoring(self):
        """Start continuous monitoring."""
        if not self.agent:
            messagebox.showerror("Error", "Agent not initialized.")
            return
        if self.monitoring_service and self.monitoring_service.is_running:
            messagebox.showinfo("Info", "Monitoring is already running")
            return

        from tkinter.simpledialog import askinteger
        interval = askinteger("Monitoring Interval",
                             "Enter monitoring interval in hours (default: 24):",
                             initialvalue=24, minvalue=1, maxvalue=168)
        if interval:
            self.monitor.initialize_agent()
            self.monitoring_service = MonitoringService(interval_hours=interval, monitor=self.monitor)
            self.monitoring_service.start()
            self.monitoring_status_label.config(
                text=f"Monitoring: ACTIVE (every {interval}h)", foreground="green"
            )
            self.log_activity(f"Monitoring started - every {interval} hours")
            self.log_activity(f"Tracking {len(JURISDICTIONS)} jurisdictions x {len(REGULATORY_AREAS)} topics")
            self.update_monitoring_dashboard()

    def stop_monitoring(self):
        """Stop continuous monitoring."""
        if self.monitoring_service:
            self.monitoring_service.stop()
            self.monitoring_status_label.config(text="Monitoring: INACTIVE", foreground="red")
            self.log_activity("Monitoring stopped")

    def update_monitoring_dashboard(self):
        """Update monitoring dashboard status."""
        if self.monitoring_service and self.monitoring_service.is_running:
            last_run = self.monitoring_service.last_run
            last_str = last_run.strftime("%Y-%m-%d %H:%M:%S") if last_run else "Not yet run"
            self.last_update_label.config(text=f"Last check: {last_str}", foreground="green")
            self.root.after(60000, self.update_monitoring_dashboard)
        else:
            self.last_update_label.config(text="Last update: Never", foreground="gray")

    def run_monitor_once(self):
        """Run monitoring check once."""
        if not self.agent:
            messagebox.showerror("Error", "Agent not initialized.")
            return

        total_checks = len(JURISDICTIONS) * len(REGULATORY_AREAS)
        self.status_label.config(
            text=f"Checking {total_checks} regulations across {len(JURISDICTIONS)} jurisdictions...",
            foreground="blue"
        )
        self.progress.start()
        self.log_activity(f"Starting regulatory check of {total_checks} regulations...")

        def monitor_thread():
            try:
                self.monitor.initialize_agent()
                result = self.monitor.monitor_all_jurisdictions()
                total_changes = sum(
                    1 for jur_results in result.get("results", {}).values()
                    for topic_result in jur_results.values()
                    if topic_result.get("changes_detected", False)
                )
                successful = sum(
                    1 for jur_results in result.get("results", {}).values()
                    for topic_result in jur_results.values()
                    if topic_result.get("success", False)
                )
                self.root.after(0, self._display_monitoring_results, result, total_changes, successful, total_checks)
            except Exception as e:
                self.root.after(0, self._display_monitoring_error, str(e))

        thread = threading.Thread(target=monitor_thread, daemon=True)
        thread.start()

    def _display_monitoring_results(self, results, total_changes, successful, total_checks):
        """Display monitoring results."""
        self.progress.stop()
        self.status_label.config(text="Monitoring Complete", foreground="green")

        self.detailed_results_text.config(state=tk.NORMAL)
        self.detailed_results_text.delete("1.0", tk.END)

        output = ["=" * 70, "LIVE REGULATORY MONITORING RESULTS", "=" * 70,
                  f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                  f"Checked: {successful}/{total_checks}\n",
                  f"Jurisdictions: {len(JURISDICTIONS)}\n",
                  f"Topics: {len(REGULATORY_AREAS)}\n", "-" * 70]

        if total_changes > 0:
            output.append(f"REGULATORY CHANGES DETECTED: {total_changes}\n")
            for jur, jur_results in results.get("results", {}).items():
                for topic, topic_result in jur_results.items():
                    if topic_result.get("changes_detected"):
                        output.append(f"\n  {jur} - {topic}")
        else:
            output.append("NO REGULATORY CHANGES DETECTED\nAll regulations are up to date.")

        self.detailed_results_text.insert("1.0", "\n".join(output))
        self.detailed_results_text.config(state=tk.DISABLED)

    def _display_monitoring_error(self, error_msg):
        """Display monitoring error."""
        self.progress.stop()
        self.status_label.config(text="Monitoring Error", foreground="red")
        messagebox.showerror("Monitoring Error", f"Error:\n{error_msg}")

    def view_notifications(self):
        """View recent notifications."""
        notifications = self.monitor.get_recent_notifications(limit=20)
        if not notifications:
            messagebox.showinfo("Notifications", "No notifications available.")
            return

        win = tk.Toplevel(self.root)
        win.title("Regulatory Change Notifications")
        win.geometry("800x600")

        text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        content = f"Recent Notifications\n{'=' * 70}\n\n"
        for nf in notifications:
            try:
                with open(nf, 'r', encoding='utf-8') as f:
                    content += f.read() + "\n\n" + "=" * 70 + "\n\n"
            except Exception as e:
                content += f"Error reading {nf}: {e}\n\n"
        text.insert("1.0", content)
        text.config(state=tk.DISABLED)

    def view_revisions(self):
        """View revision history."""
        revisions = self.monitor.get_revision_history()
        if not revisions:
            messagebox.showinfo("Revisions", "No revision history available.")
            return

        win = tk.Toplevel(self.root)
        win.title("Regulatory Revision History")
        win.geometry("900x700")

        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Consolas", 9))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        content = f"Revision History\n{'=' * 80}\n\n"
        for rev in revisions[:50]:
            content += f"Date: {rev.get('timestamp', 'N/A')}\n"
            content += f"Jurisdiction: {rev.get('jurisdiction', 'N/A')}\n"
            content += f"Topic: {rev.get('topic', 'N/A')}\n"
            changes = rev.get('changes', {})
            if changes.get('changes_detected'):
                content += "Changes Detected:\n"
                if changes.get('summary_changes'):
                    content += f"  Summary changes: {len(changes['summary_changes'])}\n"
                if changes.get('gap_changes'):
                    content += f"  Gap changes: {len(changes['gap_changes'])}\n"
            else:
                content += "No changes\n"
            content += "\n" + "-" * 80 + "\n\n"
        text.insert("1.0", content)
        text.config(state=tk.DISABLED)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main function to run the Zodia Markets Regulatory Intelligence Toolkit."""
    try:
        root = tk.Tk()
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(lambda: root.attributes('-topmost', False))
        app = RegulatoryAgentGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGUI closed by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
