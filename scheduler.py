import schedule
import time
import threading
from datetime import datetime, timedelta
from db import Database

class TaskScheduler:
    """Background task scheduler"""
    
    def __init__(self, db: Database):
        self.db = db
        self.running = False
        self.thread = None
        
        # Tasks registry
        self.tasks = {
            "daily_reset": {
                "function": self.daily_reset,
                "schedule": "00:00",
                "enabled": True,
                "last_run": None
            },
            "weekly_reset": {
                "function": self.weekly_reset,
                "schedule": "00:00",
                "enabled": True,
                "last_run": None
            },
            "backup": {
                "function": self.backup_task,
                "schedule": "03:00",
                "enabled": True,
                "last_run": None
            },
            "cleanup": {
                "function": self.cleanup_task,
                "schedule": "04:00",
                "enabled": True,
                "last_run": None
            },
            "notifications": {
                "function": self.notification_task,
                "schedule": "09:00",
                "enabled": True,
                "last_run": None
            }
        }
    
    def daily_reset(self):
        """Daily reset task"""
        print(f"[{datetime.now()}] 🔄 Running daily reset...")
        
        # Reset daily limits
        # In production, you would reset user daily limits here
        
        print(f"[{datetime.now()}] ✅ Daily reset completed")
        self.tasks["daily_reset"]["last_run"] = datetime.now()
    
    def weekly_reset(self):
        """Weekly reset task"""
        today = datetime.now()
        if today.weekday() == 0:  # Monday
            print(f"[{datetime.now()}] 🔄 Running weekly reset...")
            
            # Reset weekly leaderboard
            # In production, you would reset weekly stats here
            
            print(f"[{datetime.now()}] ✅ Weekly reset completed")
            self.tasks["weekly_reset"]["last_run"] = datetime.now()
    
    def backup_task(self):
        """Backup task"""
        print(f"[{datetime.now()}] 💾 Running backup...")
        
        # Create backup
        success = self.db.create_backup()
        
        if success:
            print(f"[{datetime.now()}] ✅ Backup completed")
        else:
            print(f"[{datetime.now()}] ❌ Backup failed")
        
        self.tasks["backup"]["last_run"] = datetime.now()
    
    def cleanup_task(self):
        """Cleanup old data"""
        print(f"[{datetime.now()}] 🧹 Running cleanup...")
        
        # Clean old temporary data
        # This is a placeholder for actual cleanup logic
        
        print(f"[{datetime.now()}] ✅ Cleanup completed")
        self.tasks["cleanup"]["last_run"] = datetime.now()
    
    def notification_task(self):
        """Send notifications"""
        print(f"[{datetime.now()}] 📢 Sending notifications...")
        
        # Send daily notifications
        # This would send notifications to users
        
        print(f"[{datetime.now()}] ✅ Notifications sent")
        self.tasks["notifications"]["last_run"] = datetime.now()
    
    def setup_schedule(self):
        """Setup scheduled tasks"""
        print("⏰ Setting up scheduled tasks...")
        
        # Schedule daily reset at midnight
        schedule.every().day.at("00:00").do(self.daily_reset)
        
        # Schedule weekly reset on Monday at midnight
        schedule.every().monday.at("00:00").do(self.weekly_reset)
        
        # Schedule daily backup at 3 AM
        schedule.every().day.at("03:00").do(self.backup_task)
        
        # Schedule cleanup at 4 AM
        schedule.every().day.at("04:00").do(self.cleanup_task)
        
        # Schedule notifications at 9 AM
        schedule.every().day.at("09:00").do(self.notification_task)
        
        # Add immediate test task
        schedule.every(1).minutes.do(self._heartbeat)
        
        print("✅ Scheduled tasks setup completed")
    
    def _heartbeat(self):
        """Heartbeat to show scheduler is alive"""
        print(f"[{datetime.now()}] 💓 Scheduler heartbeat")
    
    def run(self):
        """Run the scheduler"""
        self.setup_schedule()
        self.running = True
        
        print("🚀 Starting task scheduler...")
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start(self):
        """Start scheduler in background thread"""
        if not self.thread:
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            print("✅ Scheduler started in background")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("🛑 Scheduler stopped")
    
    def get_status(self):
        """Get scheduler status"""
        status = {
            "running": self.running,
            "tasks": {}
        }
        
        for task_name, task_info in self.tasks.items():
            status["tasks"][task_name] = {
                "enabled": task_info["enabled"],
                "last_run": task_info["last_run"].isoformat() if task_info["last_run"] else None,
                "next_run": self._get_next_run(task_name)
            }
        
        return status
    
    def _get_next_run(self, task_name):
        """Get next run time for a task"""
        job = None
        
        if task_name == "daily_reset":
            job = schedule.get_jobs("daily_reset")
        elif task_name == "weekly_reset":
            job = schedule.get_jobs("weekly_reset")
        elif task_name == "backup":
            job = schedule.get_jobs("backup")
        elif task_name == "cleanup":
            job = schedule.get_jobs("cleanup")
        elif task_name == "notifications":
            job = schedule.get_jobs("notifications")
        
        if job:
            return job[0].next_run.isoformat() if job[0].next_run else None
        
        return None
    
    def run_task_now(self, task_name: str):
        """Run a task immediately"""
        if task_name in self.tasks:
            print(f"🚀 Running {task_name} now...")
            self.tasks[task_name]["function"]()
            return True
        return False