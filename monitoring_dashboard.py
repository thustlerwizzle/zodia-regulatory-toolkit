"""
Standalone Monitoring Dashboard
Shows live tracking status and activity
Enhanced with Streamlit features: tabs, detailed results, sources, news
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import threading
import time
from regulatory_monitor import RegulatoryMonitor
from monitor_service import MonitoringService
from config import JURISDICTIONS, REGULATORY_AREAS
from research_tools import ResearchTools


class MonitoringDashboard:
    """Dashboard to show live monitoring activity"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Live Regulatory Monitoring Dashboard")
        self.root.geometry("1000x700")
        
        self.monitor = RegulatoryMonitor()
        self.monitoring_service = None
        
        self.create_widgets()
        self.update_dashboard()
    
    def create_widgets(self):
        """Create dashboard widgets with tabs (like Streamlit)"""
        # Header
        header = ttk.Label(
            self.root,
            text="🌍 LIVE REGULATORY MONITORING DASHBOARD",
            font=("Arial", 16, "bold")
        )
        header.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.root, text="Monitoring Status", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="🔴 Monitoring: INACTIVE",
            font=("Arial", 12, "bold"),
            foreground="red"
        )
        self.status_label.pack()
        
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
        
        # Create notebook for tabs (like Streamlit)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Activity Log
        self.activity_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.activity_tab, text="📊 Activity Log")
        self.create_activity_tab()
        
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
        
        # Tab 5: Statistics
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="📈 Statistics")
        self.create_stats_tab()
        
        # Controls
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
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
            text="🔄 Run Check Now",
            command=self.run_check_now
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            controls_frame,
            text="🔄 Refresh News",
            command=self.refresh_news
        ).pack(side=tk.LEFT, padx=5)
        
        # Last update
        self.last_update_label = ttk.Label(
            self.root,
            text="Last update: Never",
            font=("Arial", 8),
            foreground="gray"
        )
        self.last_update_label.pack(pady=5)
        
        # Store results and sources
        self.current_results = None
        self.current_sources = []
        self.current_news = []
    
    def create_activity_tab(self):
        """Create activity log tab"""
        log_frame = ttk.LabelFrame(self.activity_tab, text="Live Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.activity_log = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=25
        )
        self.activity_log.pack(fill=tk.BOTH, expand=True)
    
    def create_results_tab(self):
        """Create results tab (like Streamlit Results tab)"""
        results_frame = ttk.Frame(self.results_tab)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=25
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.results_text.insert("1.0", "No results yet. Run a monitoring check to see results here.\n\n"
                                        "Results will show:\n"
                                        "- Regulatory summaries\n"
                                        "- Gap analysis with priority levels\n"
                                        "- Policy updates and implementations\n"
                                        "- Detailed jurisdiction-by-jurisdiction breakdown")
        self.results_text.config(state=tk.DISABLED)
    
    def create_sources_tab(self):
        """Create sources tab (like Streamlit Sources tab)"""
        sources_frame = ttk.Frame(self.sources_tab)
        sources_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sources_text = scrolledtext.ScrolledText(
            sources_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=25
        )
        self.sources_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.sources_text.insert("1.0", "No sources yet. Sources from regulatory analysis will appear here.")
        self.sources_text.config(state=tk.DISABLED)
    
    def create_news_tab(self):
        """Create latest news tab (like Streamlit Latest News tab)"""
        news_frame = ttk.Frame(self.news_tab)
        news_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.news_text = scrolledtext.ScrolledText(
            news_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=25
        )
        self.news_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.news_text.insert("1.0", "Click '🔄 Refresh News' to fetch latest crypto regulation news.")
        self.news_text.config(state=tk.DISABLED)
    
    def create_stats_tab(self):
        """Create statistics tab"""
        stats_frame = ttk.Frame(self.stats_tab)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=25
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial stats
        self.update_statistics_display()
    
    def log_activity(self, message):
        """Log activity to dashboard"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.activity_log.see(tk.END)
        self.root.update()
    
    def start_monitoring(self):
        """Start monitoring"""
        from tkinter.simpledialog import askinteger
        interval = askinteger(
            "Monitoring Interval",
            "Enter monitoring interval in hours:",
            initialvalue=24,
            minvalue=1,
            maxvalue=168
        )
        
        if interval:
            self.monitor.initialize_agent()
            self.monitoring_service = MonitoringService(interval_hours=interval, monitor=self.monitor)
            self.monitoring_service.start()
            self.status_label.config(
                text=f"🟢 Monitoring: ACTIVE (every {interval} hours)",
                foreground="green"
            )
            self.log_activity(f"✅ Monitoring started - Checking every {interval} hours")
            self.log_activity(f"📊 Tracking {len(JURISDICTIONS)} jurisdictions × {len(REGULATORY_AREAS)} topics")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if self.monitoring_service:
            self.monitoring_service.stop()
            self.status_label.config(
                text="🔴 Monitoring: INACTIVE",
                foreground="red"
            )
            self.log_activity("⏹️ Monitoring stopped")
    
    def run_check_now(self):
        """Run immediate check"""
        self.log_activity("🔄 Starting immediate regulatory check...")
        self.status_label.config(text="🔄 Running check...", foreground="blue")
        
        # Clear and prepare results display
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "Running regulatory check...\nThis may take several minutes.\n\n")
        self.results_text.config(state=tk.DISABLED)
        
        def check_thread():
            try:
                self.monitor.initialize_agent()
                total = len(JURISDICTIONS) * len(REGULATORY_AREAS)
                self.log_activity(f"📊 Checking {total} regulations...")
                
                all_results = {}
                total_changes = 0
                all_sources = []
                
                for i, jurisdiction in enumerate(JURISDICTIONS, 1):
                    self.log_activity(f"🌍 [{i}/{len(JURISDICTIONS)}] Checking {jurisdiction}...")
                    all_results[jurisdiction] = {}
                    
                    for topic in REGULATORY_AREAS:
                        result = self.monitor.monitor_regulation(jurisdiction, topic)
                        all_results[jurisdiction][topic] = result
                        
                        if result.get("changes_detected"):
                            self.log_activity(f"  ⚠️  CHANGE DETECTED: {jurisdiction} - {topic}")
                            total_changes += 1
                        elif result.get("success"):
                            self.log_activity(f"  ✅ {topic}: No changes")
                        
                        # Collect sources
                        if result.get("data") and result["data"].get("sources"):
                            all_sources.extend(result["data"]["sources"])
                
                # Store results
                self.current_results = all_results
                self.current_sources = list({s.get("url", ""): s for s in all_sources}.values())  # Deduplicate
                
                # Update results display
                self.root.after(0, lambda: self.display_check_results(all_results, total_changes, total))
                
                self.log_activity("✅ Check complete!")
                self.root.after(0, lambda: self.status_label.config(
                    text="🟢 Check Complete",
                    foreground="green"
                ))
            except Exception as e:
                self.log_activity(f"❌ Error: {str(e)}")
                self.root.after(0, lambda: self.status_label.config(
                    text="🔴 Error occurred",
                    foreground="red"
                ))
                self.root.after(0, lambda: self.display_error(str(e)))
        
        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()
    
    def display_check_results(self, results, total_changes, total_checks):
        """Display detailed check results (like Streamlit Results tab)"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        output = []
        output.append("=" * 70)
        output.append("LIVE REGULATORY MONITORING RESULTS")
        output.append("=" * 70)
        output.append(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.append(f"✅ Successfully checked: {total_checks} regulations\n")
        output.append(f"🌍 Jurisdictions monitored: {len(JURISDICTIONS)}\n")
        output.append(f"📋 Topics monitored: {len(REGULATORY_AREAS)}\n")
        output.append("\n" + "-" * 70)
        
        if total_changes > 0:
            output.append(f"⚠️  REGULATORY CHANGES DETECTED: {total_changes}\n")
            output.append("-" * 70)
            
            # Show which jurisdictions/topics had changes
            for jurisdiction, jur_results in results.items():
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
        
        for jurisdiction, jur_results in list(results.items())[:20]:  # Show first 20
            output.append(f"\n📍 {jurisdiction}:")
            for topic, topic_result in jur_results.items():
                status = "✅" if topic_result.get("success") else "❌"
                change = "🔴 CHANGED" if topic_result.get("changes_detected") else "✅ No change"
                output.append(f"  {status} {topic}: {change}")
        
        if len(results) > 20:
            output.append(f"\n... and {len(results) - 20} more jurisdictions")
        
        self.results_text.insert("1.0", "\n".join(output))
        self.results_text.config(state=tk.DISABLED)
        
        # Update sources tab
        self.update_sources_display()
    
    def display_error(self, error_msg):
        """Display error in results"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", f"ERROR:\n\n{error_msg}")
        self.results_text.config(state=tk.DISABLED)
    
    def update_sources_display(self):
        """Update sources tab (like Streamlit Sources tab)"""
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
        """Refresh latest news (like Streamlit Latest News tab)"""
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
        """Display news articles (like Streamlit Latest News tab)"""
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
    
    def update_statistics_display(self):
        """Update statistics tab"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        
        revisions = self.monitor.get_revision_history()
        notifications = self.monitor.get_recent_notifications(limit=100)
        
        stats = f"""Monitoring Statistics
{'='*70}

Jurisdictions Monitored: {len(JURISDICTIONS)}
{chr(10).join(f'  • {j}' for j in JURISDICTIONS[:20])}
{'  ... and ' + str(len(JURISDICTIONS) - 20) + ' more' if len(JURISDICTIONS) > 20 else ''}

Topics Monitored: {len(REGULATORY_AREAS)}
{chr(10).join(f'  • {t}' for t in REGULATORY_AREAS)}

Total Regulations Tracked: {len(JURISDICTIONS) * len(REGULATORY_AREAS)}

Recent Revisions: {len(revisions)}
Recent Notifications: {len(notifications)}

Data Storage:
  • Regulatory snapshots: regulatory_data/
  • Revision history: regulatory_data/revisions/
  • Notifications: regulatory_data/notifications/
  • Policy files: Desktop/Regulatory_Policies/

Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.stats_text.insert("1.0", stats)
        self.stats_text.config(state=tk.DISABLED)
    
    def update_dashboard(self):
        """Update dashboard periodically"""
        if self.monitoring_service and self.monitoring_service.is_running:
            if self.monitoring_service.last_run:
                last_run_str = self.monitoring_service.last_run.strftime("%Y-%m-%d %H:%M:%S")
                self.last_update_label.config(
                    text=f"Last check: {last_run_str}",
                    foreground="green"
                )
        
        # Update statistics periodically
        self.update_statistics_display()
        
        self.root.after(5000, self.update_dashboard)  # Update every 5 seconds


def main():
    """Run monitoring dashboard"""
    root = tk.Tk()
    dashboard = MonitoringDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()

