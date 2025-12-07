import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List
import random

class AutoMessager:
    """Automatic messaging system"""
    
    def __init__(self, db):
        self.db = db
        self.scheduled_messages = {}
        self.greetings = [
            "সুপ্রভাত! 🌅 নতুন দিনের শুভকামনা!",
            "শুভ দুপুর! ☀️ দুপুরের খাবার খেয়েছেন?",
            "শুভ সন্ধ্যা! 🌇 দিনটি কেমন কাটলো?",
            "শুভ রাত্রি! 🌙 ভালো ঘুম হোক!",
            "আপনার দিন শুভ হোক! ✨",
            "সফলতা আপনার হোক! 🎯"
        ]
        
        self.tips = [
            "💡 টিপ: প্রতিদিন ডেইলি বোনাস নিন!",
            "💡 টিপ: গেম খেলে আরও কয়েন জিতুন!",
            "💡 টিপ: শপ থেকে বিশেষ আইটেম কিনুন!",
            "💡 টিপ: বন্ধুদের রেফার করুন বোনাস পেতে!",
            "💡 টিপ: অ্যাকটিভ থাকলে এক্সট্রা বোনাস!",
            "💡 টিপ: কুইজ গেমে জ্ঞান বাড়ান!"
        ]
        
        self.notifications = []
        
    async def schedule_daily_greeting(self, user_id: int):
        """Schedule daily greeting for user"""
        # Random time between 8 AM to 10 PM
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        
        schedule_time = f"{hour:02d}:{minute:02d}"
        
        if user_id not in self.scheduled_messages:
            self.scheduled_messages[user_id] = []
        
        self.scheduled_messages[user_id].append({
            "type": "greeting",
            "time": schedule_time,
            "enabled": True
        })
        
        return schedule_time
    
    async def send_greeting(self, user_id: int):
        """Send greeting message"""
        greeting = random.choice(self.greetings)
        tip = random.choice(self.tips)
        
        message = f"""
{greeting}

{tip}

💰 **ডেইলি বোনাস নিতে ভুলবেন না!** /daily
        """
        
        return message
    
    async def check_birthdays(self):
        """Check for user birthdays"""
        today = datetime.now().strftime("%m-%d")
        birthday_users = []
        
        for user_id_str, user_data in self.db.users.items():
            if user_data.get("birthday", "").endswith(today):
                birthday_users.append(int(user_id_str))
        
        return birthday_users
    
    async def send_birthday_wish(self, user_id: int):
        """Send birthday wish"""
        wish = f"""
🎉 **শুভ জন্মদিন!** 🎂

আপনার বিশেষ দিনে অগ্রীম শুভেচ্ছা!
আপনার জীবন সুখ, শান্তি ও সাফল্যে পূর্ণ হোক!

🎁 **জন্মদিন উপহার:** 500 কয়েন!
এক্সট্রা বোনাসের জন্য /daily কমান্ড দিন।
        """
        
        # Add birthday bonus
        user = self.db.get_user(user_id)
        if user:
            user["coins"] += 500
            self.db.update_user(user_id, {"coins": user["coins"]})
        
        return wish
    
    async def send_inactivity_reminder(self, user_id: int):
        """Send reminder to inactive users"""
        user = self.db.get_user(user_id)
        if not user:
            return None
        
        last_seen = user.get("last_seen")
        if not last_seen:
            return None
        
        try:
            last_active = datetime.fromisoformat(last_seen)
            days_inactive = (datetime.now() - last_active).days
            
            if days_inactive >= 3:
                reminder = f"""
👋 **আমরা আপনাকে মিস করছি!**

আপনি {days_inactive} দিন অ্যাকটিভ নেই।
আসুন আবার গেম খেলি এবং বোনাস উপার্জন করি!

🎁 **রিটার্নিং বোনাস:** {min(days_inactive * 50, 500)} কয়েন!
শুধু /daily কমান্ড দিন।
                """
                return reminder
        
        except:
            return None
        
        return None
    
    async def send_promotional_message(self):
        """Send promotional messages"""
        promotions = [
            "🔥 **নতুন গেম আসছে!** শীঘ্রই এক্সাইটিং গেম যোগ হবে!",
            "🎉 **স্পেশাল অফার!** সীমিত সময়ের জন্য ২x কয়েন!",
            "🏆 **লিডারবোর্ড কন্টেস্ট!** শীর্ষ ১০ জন পাবে পুরস্কার!",
            "🛒 **নতুন আইটেম!** শপে এক্সক্লুসিভ আইটেম যোগ হয়েছে!",
            "🤝 **রেফার প্রোগ্রাম!** বন্ধুকে রেফার করে ২০০ কয়েন বোনাস!"
        ]
        
        return random.choice(promotions)
    
    async def schedule_all_tasks(self):
        """Schedule all automated tasks"""
        print("⏰ Scheduling automated messages...")
        
        # Schedule tasks
        schedule.every().day.at("09:00").do(self._morning_greetings)
        schedule.every().day.at("12:00").do(self._noon_tips)
        schedule.every().day.at("18:00").do(self._evening_reminders)
        schedule.every().day.at("23:00").do(self._nightly_backup_reminder)
        schedule.every(6).hours.do(self._check_inactive_users)
        
        print("✅ Automated messages scheduled!")
    
    def _morning_greetings(self):
        """Morning greetings"""
        print("🌅 Sending morning greetings...")
    
    def _noon_tips(self):
        """Noon tips"""
        print("☀️ Sending noon tips...")
    
    def _evening_reminders(self):
        """Evening reminders"""
        print("🌇 Sending evening reminders...")
    
    def _nightly_backup_reminder(self):
        """Nightly backup reminder"""
        print("🌙 Nightly backup reminder...")
    
    def _check_inactive_users(self):
        """Check inactive users"""
        print("👥 Checking inactive users...")
    
    def run_scheduler(self):
        """Run the scheduler in background"""
        print("⏳ Starting message scheduler...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute