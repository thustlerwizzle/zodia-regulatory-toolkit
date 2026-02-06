"""
Background monitoring service for live regulatory tracking
"""
import time
import threading
from datetime import datetime
from regulatory_monitor import RegulatoryMonitor
from config import JURISDICTIONS, REGULATORY_AREAS


class MonitoringService:
    """Background service for continuous regulatory monitoring"""
    
    def __init__(self, interval_hours: int = 24, monitor: RegulatoryMonitor = None):
        self.monitor = monitor or RegulatoryMonitor()
        self.interval_hours = interval_hours
        self.is_running = False
        self.thread = None
        self.last_run = None
    
    def start(self):
        """Start the monitoring service"""
        if self.is_running:
            print("Monitoring service is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print(f"Monitoring service started (checking every {self.interval_hours} hours)")
    
    def stop(self):
        """Stop the monitoring service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Monitoring service stopped")
    
    def _run_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting regulatory monitoring cycle...")
                
                # Ensure agent is initialized
                if self.monitor.agent is None:
                    self.monitor.initialize_agent()
                
                # Monitor all jurisdictions and topics
                results = self.monitor.monitor_all_jurisdictions()
                
                # Count changes
                total_changes = sum(
                    1 for jur_results in results.get("results", {}).values()
                    for topic_result in jur_results.values()
                    if topic_result.get("changes_detected", False)
                )
                
                if total_changes > 0:
                    print(f"⚠️  {total_changes} regulatory changes detected!")
                    print("Check notifications folder for details")
                else:
                    print("✅ No regulatory changes detected")
                
                self.last_run = datetime.now()
                
                # Wait for next interval
                if self.is_running:
                    sleep_seconds = self.interval_hours * 3600
                    print(f"Next check in {self.interval_hours} hours...")
                    time.sleep(sleep_seconds)
                    
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                if self.is_running:
                    time.sleep(3600)  # Wait 1 hour before retrying
    
    def run_once(self):
        """Run monitoring once (for manual trigger)"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running one-time regulatory monitoring...")
        
        # Ensure agent is initialized
        if self.monitor.agent is None:
            self.monitor.initialize_agent()
        
        results = self.monitor.monitor_all_jurisdictions()
        
        total_changes = sum(
            1 for jur_results in results.get("results", {}).values()
            for topic_result in jur_results.values()
            if topic_result.get("changes_detected", False)
        )
        
        return {
            "success": True,
            "changes_detected": total_changes > 0,
            "total_changes": total_changes,
            "results": results
        }

