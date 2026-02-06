"""
GUI Application for Regulatory Analysis Agent
Unified interface for querying, monitoring, and viewing results
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime
import os
import tempfile
import shutil
from regulatory_agent import RegulatoryAgent
from config import DEEPSEEK_API_KEY, JURISDICTIONS, REGULATORY_AREAS
from file_processor import FileProcessor
from regulatory_monitor import RegulatoryMonitor
from monitor_service import MonitoringService
from research_tools import ResearchTools


class RegulatoryAgentGUI:
    """GUI Application for Regulatory Analysis Agent"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Regulatory Analysis Agent - Unified Dashboard")
        self.root.geometry("1400x900")
        
        # Initialize agent variable
        self.agent = None
        self.monitor = RegulatoryMonitor()
        self.monitoring_service = None
        
        # Store results and sources for tabs
        self.current_results = None
        self.current_sources = []
        self.current_news = []
        
        # Create UI first
        self.create_widgets()
        
        # Then initialize agent
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the regulatory agent"""
        try:
            if not DEEPSEEK_API_KEY:
                self.status_label.config(text="❌ API Key Missing", foreground="red")
                messagebox.showerror(
                    "API Key Missing",
                    "DEEPSEEK_API_KEY not found in .env file.\n\n"
                    "Please set DEEPSEEK_API_KEY in your .env file.\n"
                    "Get your API key from: https://platform.deepseek.com/api_keys"
                )
                return
            
            self.status_label.config(text="🔄 Initializing agent...", foreground="blue")
            self.root.update()  # Update UI to show status
            
            self.agent = RegulatoryAgent()
            self.status_label.config(text="✅ Agent Ready", foreground="green")
            self.run_button.config(state="normal")
        except Exception as e:
            error_msg = f"Failed to initialize agent:\n{str(e)}"
            self.status_label.config(text="❌ Agent Error", foreground="red")
            messagebox.showerror("Initialization Error", error_msg)
            print(f"Initialization error: {error_msg}")
            import traceback
            traceback.print_exc()
    
    def create_widgets(self):
        """Create the unified GUI with tabs"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🔍 Regulatory Analysis Agent - Unified Dashboard",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Initializing...",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tab 1: Analysis (Query Input + Results)
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="🔍 Analysis")
        self.create_analysis_tab()
        
        # Tab 2: Results
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="📋 Results")
        self.create_results_tab()
        
        # Tab 3: Sources
        self.sources_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.sources_tab, text="📚 Sources")
        self.create_sources_tab()
        
        # Tab 4: Latest News
        self.news_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.news_tab, text="📰 Latest News")
        self.create_news_tab()
        
        # Tab 5: Monitoring Dashboard
        self.monitoring_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_tab, text="🌍 Monitoring")
        self.create_monitoring_tab()
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
    
    def create_analysis_tab(self):
        """Create the analysis tab with query input and results"""
        # Split into left (input) and right (results) panels
        paned = ttk.PanedWindow(self.analysis_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Input
        input_frame = ttk.LabelFrame(paned, text="Query Input", padding="10")
        paned.add(input_frame, weight=1)
        
        # Query input
        ttk.Label(input_frame, text="Regulatory Topic/Query:").pack(anchor=tk.W, pady=(0, 5))
        self.query_entry = ttk.Entry(input_frame, width=40)
        self.query_entry.pack(fill=tk.X, pady=(0, 10))
        self.query_entry.insert(0, "stablecoin regulation")
        
        # Jurisdiction
        ttk.Label(input_frame, text="Jurisdiction (Optional):").pack(anchor=tk.W, pady=(0, 5))
        self.jurisdiction_entry = ttk.Entry(input_frame, width=40)
        self.jurisdiction_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Current policies - File upload section
        ttk.Label(input_frame, text="Current Company Policies (Optional):").pack(anchor=tk.W, pady=(0, 5))
        
        # File upload buttons
        file_button_frame = ttk.Frame(input_frame)
        file_button_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.upload_button = ttk.Button(
            file_button_frame,
            text="📁 Upload Policy Files",
            command=self.upload_policy_files
        )
        self.upload_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_files_button = ttk.Button(
            file_button_frame,
            text="🗑️ Clear Files",
            command=self.clear_uploaded_files
        )
        self.clear_files_button.pack(side=tk.LEFT)
        
        # File list display
        self.uploaded_files_label = ttk.Label(
            input_frame,
            text="No files uploaded",
            font=("Arial", 8),
            foreground="gray"
        )
        self.uploaded_files_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Text area for manual input
        ttk.Label(input_frame, text="Or paste policies manually:").pack(anchor=tk.W, pady=(0, 5))
        self.policies_text = scrolledtext.ScrolledText(input_frame, width=40, height=15)
        self.policies_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Store uploaded file paths
        self.uploaded_files = []
        
        # Run button
        self.run_button = ttk.Button(
            input_frame,
            text="🚀 Run Analysis",
            command=self.run_analysis,
            state="normal" if self.agent else "disabled"
        )
        self.run_button.pack(pady=10)
        
        # Right panel - Quick Results
        results_frame = ttk.LabelFrame(paned, text="Quick Results", padding="10")
        paned.add(results_frame, weight=2)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_results_tab(self):
        """Create detailed results tab"""
        results_frame = ttk.Frame(self.results_tab)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.detailed_results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=30
        )
        self.detailed_results_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.detailed_results_text.insert("1.0", "No results yet. Run an analysis to see detailed results here.\n\n"
                                        "Results will show:\n"
                                        "- Regulatory summaries\n"
                                        "- Gap analysis with priority levels\n"
                                        "- Policy updates and implementations\n"
                                        "- Detailed breakdown by jurisdiction")
        self.detailed_results_text.config(state=tk.DISABLED)
    
    def create_sources_tab(self):
        """Create sources tab"""
        sources_frame = ttk.Frame(self.sources_tab)
        sources_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sources_text = scrolledtext.ScrolledText(
            sources_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=30
        )
        self.sources_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.sources_text.insert("1.0", "No sources yet. Sources from regulatory analysis will appear here.")
        self.sources_text.config(state=tk.DISABLED)
    
    def create_news_tab(self):
        """Create latest news tab"""
        news_frame = ttk.Frame(self.news_tab)
        news_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh button
        button_frame = ttk.Frame(news_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="🔄 Refresh Latest News",
            command=self.refresh_news
        ).pack(side=tk.LEFT)
        
        self.news_text = scrolledtext.ScrolledText(
            news_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=30
        )
        self.news_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.news_text.insert("1.0", "Click '🔄 Refresh Latest News' to fetch latest crypto regulation news.")
        self.news_text.config(state=tk.DISABLED)
    
    def create_monitoring_tab(self):
        """Create monitoring dashboard tab"""
        monitoring_frame = ttk.Frame(self.monitoring_tab)
        monitoring_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(monitoring_frame, text="Monitoring Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.monitoring_status_label = ttk.Label(
            status_frame,
            text="🔴 Monitoring: INACTIVE",
            font=("Arial", 12, "bold"),
            foreground="red"
        )
        self.monitoring_status_label.pack()
        
        # Stats frame
        stats_frame = ttk.Frame(status_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.jurisdictions_label = ttk.Label(
            stats_frame,
            text=f"🌍 Jurisdictions: {len(JURISDICTIONS)}",
            font=("Arial", 10)
        )
        self.jurisdictions_label.pack(side=tk.LEFT, padx=10)
        
        self.topics_label = ttk.Label(
            stats_frame,
            text=f"📋 Topics: {len(REGULATORY_AREAS)}",
            font=("Arial", 10)
        )
        self.topics_label.pack(side=tk.LEFT, padx=10)
        
        total = len(JURISDICTIONS) * len(REGULATORY_AREAS)
        self.total_label = ttk.Label(
            stats_frame,
            text=f"📊 Total Regulations: {total}",
            font=("Arial", 10, "bold")
        )
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        # Controls
        controls_frame = ttk.Frame(monitoring_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            controls_frame,
            text="▶️ Start Monitoring",
            command=self.start_monitoring
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="⏹️ Stop Monitoring",
            command=self.stop_monitoring
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="🔄 Check Now",
            command=self.run_monitor_once
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="📬 View Notifications",
            command=self.view_notifications
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="📋 View Revisions",
            command=self.view_revisions
        ).pack(side=tk.LEFT, padx=5)
        
        # Activity log
        log_frame = ttk.LabelFrame(monitoring_frame, text="Live Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.activity_log = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=20
        )
        self.activity_log.pack(fill=tk.BOTH, expand=True)
        
        # Last update
        self.last_update_label = ttk.Label(
            monitoring_frame,
            text="Last update: Never",
            font=("Arial", 8),
            foreground="gray"
        )
        self.last_update_label.pack(pady=5)
    
    def run_analysis(self):
        """Run the regulatory analysis"""
        if not self.agent:
            messagebox.showerror("Error", "Agent not initialized. Please check your API keys.")
            return
        
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showerror("Error", "Please enter a query.")
            return
        
        jurisdiction = self.jurisdiction_entry.get().strip()
        current_policies = self.get_policies_content()
        
        # Disable button and start progress
        self.run_button.config(state="disabled")
        self.progress.start()
        self.status_label.config(text="🔄 Running analysis...", foreground="blue")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "Running analysis...\nThis may take a few minutes.\n\n")
        
        # Run in separate thread to avoid freezing GUI
        thread = threading.Thread(
            target=self._run_analysis_thread,
            args=(query, jurisdiction, current_policies)
        )
        thread.daemon = True
        thread.start()
    
    def _run_analysis_thread(self, query, jurisdiction, current_policies):
        """Run analysis in background thread"""
        try:
            results = self.agent.run(
                query=query,
                jurisdiction=jurisdiction,
                current_policies=current_policies
            )
            
            # Update UI in main thread
            self.root.after(0, self._display_results, results)
            
        except Exception as e:
            error_msg = f"Error during analysis:\n{str(e)}"
            self.root.after(0, self._display_error, error_msg)
    
    def _display_results(self, results):
        """Display results in the text area"""
        self.progress.stop()
        self.run_button.config(state="normal")
        self.status_label.config(text="✅ Analysis Complete", foreground="green")
        
        # Store results for other tabs
        self.current_results = results
        if results.get("sources"):
            self.current_sources = results["sources"]
        
        # Clear and display results in quick results
        self.results_text.delete("1.0", tk.END)
        
        # Also update detailed results tab
        self.detailed_results_text.config(state=tk.NORMAL)
        self.detailed_results_text.delete("1.0", tk.END)
        
        # Update sources tab
        self.update_sources_display()
        
        output = []
        output.append("=" * 70)
        output.append("REGULATORY ANALYSIS RESULTS")
        output.append("=" * 70)
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Regulatory Summary
        if results.get("regulatory_summary"):
            output.append("\n" + "-" * 70)
            output.append("REGULATORY REQUIREMENTS SUMMARY")
            output.append("-" * 70)
            output.append(results["regulatory_summary"])
            output.append("")
        
        # Gap Analysis
        if results.get("gap_analysis"):
            gap_analysis = results["gap_analysis"]
            output.append("\n" + "-" * 70)
            output.append("GAP ANALYSIS")
            output.append("-" * 70)
            
            priority_levels = gap_analysis.get("priority_levels", {})
            if priority_levels:
                output.append(f"\nCritical Gaps: {len(priority_levels.get('critical', []))}")
                output.append(f"High Priority Gaps: {len(priority_levels.get('high', []))}")
                output.append(f"Medium Priority Gaps: {len(priority_levels.get('medium', []))}")
                output.append(f"Low Priority Gaps: {len(priority_levels.get('low', []))}")
                
                # Show critical gaps
                critical = priority_levels.get("critical", [])
                if critical:
                    output.append("\n### Critical Priority Gaps:")
                    for i, gap in enumerate(critical[:5], 1):  # Show first 5
                        output.append(f"\n{i}. {gap.get('gap_id', f'GAP-{i:03d}')}")
                        output.append(f"   Requirement: {gap.get('regulatory_requirement', 'N/A')[:100]}...")
                        output.append(f"   Recommendation: {gap.get('recommendation', 'N/A')[:100]}...")
            output.append("")
        
        # Policy Updates
        if results.get("policy_updates"):
            policy_updates = results["policy_updates"]
            output.append("\n" + "-" * 70)
            output.append("POLICY UPDATES")
            output.append("-" * 70)
            output.append(f"New Policies Required: {len(policy_updates.get('new_policies', []))}")
            output.append(f"Policies to Modify: {len(policy_updates.get('modified_policies', []))}")
            output.append("")
        
        # Policy Implementation
        if results.get("policy_implementation") and results["policy_implementation"].get("files_created"):
            impl = results["policy_implementation"]
            output.append("\n" + "-" * 70)
            output.append("✅ POLICY IMPLEMENTATION")
            output.append("-" * 70)
            output.append(f"✅ Successfully implemented {len(impl.get('implemented_policies', []))} policies")
            output.append(f"📁 Saved to: {impl.get('output_directory', 'N/A')}")
            output.append(f"📄 Summary: {impl.get('summary_file', 'N/A')}")
            output.append("\nImplemented Policies:")
            for policy in impl.get("implemented_policies", []):
                output.append(f"  • {policy.get('gap_id', 'N/A')} - {policy.get('filename', 'N/A')}")
            output.append("")
        
        # Sources
        if results.get("sources"):
            sources = results["sources"]
            output.append("\n" + "-" * 70)
            output.append(f"SOURCES ({len(sources)} total)")
            output.append("-" * 70)
            for i, source in enumerate(sources[:10], 1):  # Show first 10
                output.append(f"{i}. {source.get('title', 'N/A')}")
                output.append(f"   {source.get('url', 'N/A')}")
            output.append("")
        
        # Full Report
        if results.get("report"):
            output.append("\n" + "=" * 70)
            output.append("FULL REPORT")
            output.append("=" * 70)
            output.append(results["report"])
        
        # Errors
        if results.get("error"):
            output.append("\n" + "=" * 70)
            output.append("ERRORS")
            output.append("=" * 70)
            output.append(results["error"])
        
        # Display in text widget (quick results)
        self.results_text.insert("1.0", "\n".join(output))
        
        # Display in detailed results tab
        self.detailed_results_text.insert("1.0", "\n".join(output))
        self.detailed_results_text.config(state=tk.DISABLED)
        
        # Save report to file and show implementation results
        success_msg = "Analysis complete!"
        
        if results.get("policy_implementation") and results["policy_implementation"].get("files_created"):
            impl = results["policy_implementation"]
            success_msg += f"\n\n✅ Implemented {len(impl.get('implemented_policies', []))} policies"
            success_msg += f"\n📁 Policies saved to Desktop/Regulatory_Policies/"
            success_msg += f"\n📄 See: {impl.get('summary_file', 'N/A')}"
        
        if results.get("report"):
            filename = f"regulatory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(results["report"])
                success_msg += f"\n\n📊 Report saved to: {filename}"
            except Exception as e:
                success_msg += f"\n\n⚠️ Failed to save report: {str(e)}"
        
        messagebox.showinfo("Success", success_msg)
    
    def _display_error(self, error_msg):
        """Display error message"""
        self.progress.stop()
        self.run_button.config(state="normal")
        self.status_label.config(text="❌ Analysis Failed", foreground="red")
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"ERROR:\n\n{error_msg}")
        messagebox.showerror("Analysis Error", error_msg)
    
    def upload_policy_files(self):
        """Upload policy files"""
        filetypes = [
            ("All supported files", "*.pdf;*.docx;*.doc;*.txt;*.md;*.xlsx;*.xls;*.csv"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx;*.doc"),
            ("Text files", "*.txt;*.md"),
            ("Excel files", "*.xlsx;*.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Policy Files",
            filetypes=filetypes
        )
        
        if files:
            self.uploaded_files.extend(files)
            file_names = [os.path.basename(f) for f in self.uploaded_files]
            if len(file_names) <= 3:
                self.uploaded_files_label.config(
                    text=f"Files: {', '.join(file_names)}",
                    foreground="green"
                )
            else:
                self.uploaded_files_label.config(
                    text=f"{len(file_names)} files uploaded",
                    foreground="green"
                )
    
    def clear_uploaded_files(self):
        """Clear uploaded files"""
        self.uploaded_files = []
        self.uploaded_files_label.config(text="No files uploaded", foreground="gray")
        self.policies_text.delete("1.0", tk.END)
    
    def get_policies_content(self) -> str:
        """Get combined content from uploaded files and text area"""
        content_parts = []
        
        # Process uploaded files
        if self.uploaded_files:
            try:
                file_content = FileProcessor.process_multiple_files(self.uploaded_files)
                content_parts.append(file_content)
            except Exception as e:
                messagebox.showwarning("File Processing Warning", f"Error processing some files: {str(e)}")
        
        # Get text from text area
        text_content = self.policies_text.get("1.0", tk.END).strip()
        if text_content:
            if content_parts:
                content_parts.append("\n\n--- Manual Input ---\n\n")
            content_parts.append(text_content)
        
        return "\n".join(content_parts) if content_parts else ""
    
    def update_sources_display(self):
        """Update sources tab"""
        self.sources_text.config(state=tk.NORMAL)
        self.sources_text.delete("1.0", tk.END)
        
        if not self.current_sources:
            self.sources_text.insert("1.0", "No sources available yet.")
        else:
            output = []
            output.append(f"Found {len(self.current_sources)} unique sources\n")
            output.append("=" * 70 + "\n")
            
            # Group by source type
            source_types = {}
            for source in self.current_sources:
                source_type = source.get("source_type", "unknown")
                if source_type not in source_types:
                    source_types[source_type] = []
                source_types[source_type].append(source)
            
            for source_type, type_sources in source_types.items():
                output.append(f"\n{source_type.upper()} Sources ({len(type_sources)}):")
                output.append("-" * 70)
                for i, source in enumerate(type_sources[:20], 1):  # Show first 20 per type
                    output.append(f"\n{i}. {source.get('title', 'N/A')}")
                    output.append(f"   🔗 {source.get('url', 'N/A')}")
                    if source.get('published_at'):
                        output.append(f"   📅 {source.get('published_at', '')[:10]}")
                if len(type_sources) > 20:
                    output.append(f"\n... and {len(type_sources) - 20} more {source_type} sources")
                output.append("")
            
            self.sources_text.insert("1.0", "\n".join(output))
        
        self.sources_text.config(state=tk.DISABLED)
    
    def refresh_news(self):
        """Refresh latest news"""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete("1.0", tk.END)
        self.news_text.insert("1.0", "Fetching latest news articles...\nThis may take a moment.\n")
        self.news_text.config(state=tk.DISABLED)
        
        def fetch_news():
            try:
                tools = ResearchTools()
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
                        self.log_activity(f"⚠️ Error fetching news for '{query}': {str(e)}")
                
                # Sort by published date (newest first)
                all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
                self.current_news = all_articles
                
                self.root.after(0, lambda: self.display_news(all_articles))
            except Exception as e:
                self.root.after(0, lambda: self.display_news_error(str(e)))
        
        thread = threading.Thread(target=fetch_news, daemon=True)
        thread.start()
    
    def display_news(self, articles):
        """Display news articles"""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete("1.0", tk.END)
        
        if not articles:
            self.news_text.insert("1.0", 
                "⚠️ No news articles found. This might be due to:\n"
                "- API key issues (check your .env file)\n"
                "- No recent articles matching the search terms\n"
                "- Network connectivity issues"
            )
        else:
            output = []
            output.append(f"📰 Found {len(articles)} latest news articles (last 7 days)\n")
            output.append("=" * 70 + "\n")
            
            for i, article in enumerate(articles[:30], 1):  # Show first 30
                output.append(f"\n{i}. {article.get('title', 'N/A')}")
                output.append("-" * 70)
                
                content = article.get('content', '') or article.get('description', '')
                if content:
                    preview = content[:300] + "..." if len(content) > 300 else content
                    output.append(f"\n{preview}\n")
                
                output.append(f"\n📅 {article.get('published_at', 'N/A')[:10] if article.get('published_at') else 'N/A'}")
                output.append(f"📰 Source: {article.get('source', 'N/A')}")
                if article.get('author'):
                    output.append(f"✍️ Author: {article.get('author', 'N/A')}")
                output.append(f"🔗 {article.get('url', 'N/A')}")
                output.append("")
            
            if len(articles) > 30:
                output.append(f"\n... and {len(articles) - 30} more articles")
            
            self.news_text.insert("1.0", "\n".join(output))
        
        self.news_text.config(state=tk.DISABLED)
    
    def display_news_error(self, error_msg):
        """Display news error"""
        self.news_text.config(state=tk.NORMAL)
        self.news_text.delete("1.0", tk.END)
        self.news_text.insert("1.0", f"ERROR fetching news:\n\n{error_msg}")
        self.news_text.config(state=tk.DISABLED)
    
    def log_activity(self, message):
        """Log activity to monitoring dashboard"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_log.see(tk.END)
        self.root.update()
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        if not self.agent:
            messagebox.showerror("Error", "Agent not initialized. Please check your API keys.")
            return
        
        if self.monitoring_service and self.monitoring_service.is_running:
            messagebox.showinfo("Info", "Monitoring is already running")
            return
        
        # Ask for monitoring interval
        from tkinter.simpledialog import askinteger
        interval = askinteger(
            "Monitoring Interval",
            "Enter monitoring interval in hours (default: 24):",
            initialvalue=24,
            minvalue=1,
            maxvalue=168
        )
        
        if interval:
            self.monitor.initialize_agent()
            self.monitoring_service = MonitoringService(interval_hours=interval, monitor=self.monitor)
            self.monitoring_service.start()
            self.monitoring_status_label.config(
                text=f"🟢 Monitoring: ACTIVE (checking every {interval} hours)",
                foreground="green"
            )
            self.log_activity(f"✅ Monitoring started - Checking every {interval} hours")
            self.log_activity(f"📊 Tracking {len(JURISDICTIONS)} jurisdictions × {len(REGULATORY_AREAS)} topics")
            self.update_monitoring_dashboard()
            messagebox.showinfo(
                "Monitoring Started", 
                f"✅ Live monitoring ACTIVE!\n\n"
                f"Tracking:\n"
                f"• {len(JURISDICTIONS)} jurisdictions\n"
                f"• {len(REGULATORY_AREAS)} regulatory topics\n"
                f"• Checking every {interval} hours\n\n"
                f"Monitoring crypto, stablecoin, and digital asset regulations globally."
            )
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if self.monitoring_service:
            self.monitoring_service.stop()
            self.monitoring_status_label.config(
                text="🔴 Monitoring: INACTIVE",
                foreground="red"
            )
            self.log_activity("⏹️ Monitoring stopped")
            messagebox.showinfo("Monitoring Stopped", "Monitoring service has been stopped.")
    
    def update_monitoring_dashboard(self):
        """Update monitoring dashboard with current status"""
        if self.monitoring_service and self.monitoring_service.is_running:
            last_run = self.monitoring_service.last_run
            last_run_str = last_run.strftime("%Y-%m-%d %H:%M:%S") if last_run else "Not yet run"
            self.last_update_label.config(
                text=f"Last check: {last_run_str}",
                foreground="green"
            )
            
            # Schedule next update
            self.root.after(60000, self.update_monitoring_dashboard)  # Update every minute
        else:
            self.last_update_label.config(text="Last update: Never", foreground="gray")
    
    def run_monitor_once(self):
        """Run monitoring check once"""
        if not self.agent:
            messagebox.showerror("Error", "Agent not initialized.")
            return
        
        from config import JURISDICTIONS, REGULATORY_AREAS
        total_checks = len(JURISDICTIONS) * len(REGULATORY_AREAS)
        
        self.status_label.config(
            text=f"🔄 Checking {total_checks} regulations across {len(JURISDICTIONS)} jurisdictions...",
            foreground="blue"
        )
        self.progress.start()
        self.log_activity(f"🔄 Starting regulatory check of {total_checks} regulations...")
        self.detailed_results_text.config(state=tk.NORMAL)
        self.detailed_results_text.delete("1.0", tk.END)
        self.detailed_results_text.insert("1.0", 
            f"Running live regulatory check...\n\n"
            f"Monitoring:\n"
            f"• {len(JURISDICTIONS)} Jurisdictions: {', '.join(JURISDICTIONS[:5])}...\n"
            f"• {len(REGULATORY_AREAS)} Topics: {', '.join(REGULATORY_AREAS[:5])}...\n"
            f"• Total: {total_checks} regulations being checked\n\n"
            f"This may take several minutes...\n"
        )
        self.detailed_results_text.config(state=tk.DISABLED)
        
        def monitor_thread():
            try:
                self.monitor.initialize_agent()
                
                # Update status as we go
                self.root.after(0, lambda: self.log_activity(f"[{datetime.now().strftime('%H:%M:%S')}] Starting global regulatory scan..."))
                
                result = self.monitor.monitor_all_jurisdictions()
                total_changes = sum(
                    1 for jur_results in result.get("results", {}).values()
                    for topic_result in jur_results.values()
                    if topic_result.get("changes_detected", False)
                )
                
                # Count successful checks
                successful_checks = sum(
                    1 for jur_results in result.get("results", {}).values()
                    for topic_result in jur_results.values()
                    if topic_result.get("success", False)
                )
                
                self.root.after(0, self._display_monitoring_results, result, total_changes, successful_checks, total_checks)
            except Exception as e:
                self.root.after(0, self._display_monitoring_error, str(e))
        
        thread = threading.Thread(target=monitor_thread, daemon=True)
        thread.start()
    
    def _display_monitoring_results(self, results, total_changes, successful_checks, total_checks):
        """Display monitoring results"""
        self.progress.stop()
        self.status_label.config(text="✅ Monitoring Complete", foreground="green")
        
        # Show detailed results in results tab
        self.detailed_results_text.config(state=tk.NORMAL)
        self.detailed_results_text.delete("1.0", tk.END)
        output = []
        output.append("=" * 70)
        output.append("LIVE REGULATORY MONITORING RESULTS")
        output.append("=" * 70)
        output.append(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.append(f"✅ Successfully checked: {successful_checks}/{total_checks} regulations\n")
        output.append(f"🌍 Jurisdictions monitored: {len(JURISDICTIONS)}\n")
        output.append(f"📋 Topics monitored: {len(REGULATORY_AREAS)}\n")
        output.append("\n" + "-" * 70)
        
        if total_changes > 0:
            output.append(f"⚠️  REGULATORY CHANGES DETECTED: {total_changes}\n")
            output.append("-" * 70)
            
            # Show which jurisdictions/topics had changes
            for jurisdiction, jur_results in results.get("results", {}).items():
                for topic, topic_result in jur_results.items():
                    if topic_result.get("changes_detected"):
                        output.append(f"\n🔴 {jurisdiction} - {topic}")
                        if topic_result.get("notification_file"):
                            output.append(f"   📬 Notification: {topic_result['notification_file']}")
                        if topic_result.get("revision_file"):
                            output.append(f"   📋 Revision: {topic_result['revision_file']}")
        else:
            output.append("✅ NO REGULATORY CHANGES DETECTED")
            output.append("\nAll regulations are up to date across all monitored jurisdictions.")
        
        output.append("\n" + "=" * 70)
        output.append("\nDetailed Results by Jurisdiction:\n")
        output.append("-" * 70)
        
        for jurisdiction, jur_results in results.get("results", {}).items():
            output.append(f"\n📍 {jurisdiction}:")
            for topic, topic_result in jur_results.items():
                status = "✅" if topic_result.get("success") else "❌"
                change = "🔴 CHANGED" if topic_result.get("changes_detected") else "✅ No change"
                output.append(f"  {status} {topic}: {change}")
        
        self.results_text.insert("1.0", "\n".join(output))
        
        if total_changes > 0:
            messagebox.showwarning(
                "Regulatory Changes Detected",
                f"⚠️ {total_changes} regulatory changes detected!\n\n"
                f"✅ Checked {successful_checks}/{total_checks} regulations\n"
                f"📬 Check notifications folder for details\n"
                f"📋 Policies have been automatically updated\n\n"
                f"View detailed results in the results panel."
            )
        else:
            messagebox.showinfo(
                "Monitoring Complete",
                f"✅ Regulatory monitoring complete!\n\n"
                f"✅ Checked {successful_checks}/{total_checks} regulations\n"
                f"🌍 Across {len(JURISDICTIONS)} jurisdictions\n"
                f"📋 {len(REGULATORY_AREAS)} topics monitored\n\n"
                f"No regulatory changes detected.\nAll regulations are up to date."
            )
    
    def _display_monitoring_error(self, error_msg):
        """Display monitoring error"""
        self.progress.stop()
        self.status_label.config(text="❌ Monitoring Error", foreground="red")
        messagebox.showerror("Monitoring Error", f"Error during monitoring:\n{error_msg}")
    
    def view_notifications(self):
        """View recent notifications"""
        notifications = self.monitor.get_recent_notifications(limit=20)
        
        if not notifications:
            messagebox.showinfo("Notifications", "No notifications available.")
            return
        
        # Create notification viewer window
        notif_window = tk.Toplevel(self.root)
        notif_window.title("Regulatory Change Notifications")
        notif_window.geometry("800x600")
        
        text_widget = scrolledtext.ScrolledText(notif_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        content = f"Recent Regulatory Change Notifications\n{'='*70}\n\n"
        for notif_file in notifications:
            try:
                with open(notif_file, 'r', encoding='utf-8') as f:
                    content += f.read() + "\n\n" + "="*70 + "\n\n"
            except Exception as e:
                content += f"Error reading {notif_file}: {e}\n\n"
        
        text_widget.insert("1.0", content)
        text_widget.config(state=tk.DISABLED)
    
    def view_revisions(self):
        """View revision history"""
        revisions = self.monitor.get_revision_history()
        
        if not revisions:
            messagebox.showinfo("Revisions", "No revision history available.")
            return
        
        # Create revision viewer window
        rev_window = tk.Toplevel(self.root)
        rev_window.title("Regulatory Revision History")
        rev_window.geometry("900x700")
        
        text_widget = scrolledtext.ScrolledText(rev_window, wrap=tk.WORD, font=("Consolas", 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        content = f"Regulatory Revision History\n{'='*80}\n\n"
        for revision in revisions[:50]:  # Show last 50 revisions
            content += f"Date: {revision.get('timestamp', 'N/A')}\n"
            content += f"Jurisdiction: {revision.get('jurisdiction', 'N/A')}\n"
            content += f"Topic: {revision.get('topic', 'N/A')}\n"
            changes = revision.get('changes', {})
            if changes.get('changes_detected'):
                content += "⚠️ Changes Detected:\n"
                if changes.get('summary_changes'):
                    content += f"  - Summary changes: {len(changes['summary_changes'])}\n"
                if changes.get('gap_changes'):
                    content += f"  - Gap analysis changes: {len(changes['gap_changes'])}\n"
                if changes.get('new_regulations'):
                    content += f"  - New regulations: {len(changes['new_regulations'])}\n"
            else:
                content += "✅ No changes\n"
            content += "\n" + "-"*80 + "\n\n"
        
        text_widget.insert("1.0", content)
        text_widget.config(state=tk.DISABLED)


def main():
    """Main function to run the GUI"""
    try:
        root = tk.Tk()
        root.lift()  # Bring window to front
        root.attributes('-topmost', True)  # Make it appear on top
        root.after_idle(lambda: root.attributes('-topmost', False))  # Then allow it to go behind other windows
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

