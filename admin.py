from typing import List, Dict
from datetime import datetime
from config import Config
from db import Database
from utils import Utils

class AdminManager:
    """Admin management system"""
    
    def __init__(self, db: Database):
        self.db = db
        self.config = Config()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.config.ADMINS or user_id == self.config.BOT_OWNER_ID
    
    async def get_bot_stats(self) -> str:
        """Get bot statistics"""
        stats = self.db.get_stats()
        
        stats_text = f"""
📊 **বট পরিসংখ্যান:**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 **ইউজার:**
• মোট ইউজার: {stats['total_users']:,}
• অ্যাকটিভ ইউজার: {stats['active_users']:,}

💰 **ইকোনমি:**
• মোট কয়েন: {Utils.format_coins(stats['total_coins'])}
• মোট পেমেন্ট: {stats['total_payments']:,}

🛍️ **শপ:**
• আইটেম সংখ্যা: {stats['shop_items']}

⏰ **সিস্টেম:**
• ব্যাকআপ: {stats['backup_time'][:10]}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        return stats_text
    
    async def broadcast_message(self, admin_id: int, message: str) -> Dict:
        """Broadcast message to all users (simulated)"""
        if not self.is_admin(admin_id):
            return {"success": False, "message": "শুধুমাত্র অ্যাডমিন ব্রডকাস্ট করতে পারবেন!"}
        
        if len(message) < 5:
            return {"success": False, "message": "বার্তাটি খুব ছোট!"}
        
        # In real bot, you would send to all users
        # This is simulation
        total_users = len(self.db.users)
        
        return {
            "success": True,
            "message": f"✅ ব্রডকাস্ট পাঠানো হয়েছে {total_users} জন ইউজারকে!",
            "sent_to": total_users
        }
    
    async def manage_user(self, admin_id: int, target_id: int, action: str, reason: str = "") -> Dict:
        """Manage user (warn/ban/unban)"""
        if not self.is_admin(admin_id):
            return {"success": False, "message": "অনুমতি নেই!"}
        
        user = self.db.get_user(target_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        if action == "warn":
            warnings = user.get("warnings", 0) + 1
            self.db.update_user(target_id, {"warnings": warnings})
            
            if warnings >= 3:
                self.db.update_user(target_id, {"is_banned": True})
                ban_msg = "\n⚠️ ৩টি সতর্কতা পাওয়ায় ব্যান করা হয়েছে!"
            else:
                ban_msg = ""
            
            return {
                "success": True,
                "message": f"⚠️ সতর্কতা দেওয়া হয়েছে {target_id} কে ({warnings}/3){ban_msg}",
                "warnings": warnings
            }
        
        elif action == "ban":
            self.db.update_user(target_id, {"is_banned": True})
            return {
                "success": True,
                "message": f"❌ ইউজার {target_id} ব্যান করা হয়েছে!",
                "banned": True
            }
        
        elif action == "unban":
            self.db.update_user(target_id, {"is_banned": False, "warnings": 0})
            return {
                "success": True,
                "message": f"✅ ইউজার {target_id} আনব্যান করা হয়েছে!",
                "banned": False
            }
        
        elif action == "add_coins":
            if not reason.isdigit():
                return {"success": False, "message": "সঠিক সংখ্যা দিন!"}
            
            amount = int(reason)
            user["coins"] += amount
            self.db.update_user(target_id, {"coins": user["coins"]})
            
            return {
                "success": True,
                "message": f"✅ {target_id} কে {Utils.format_coins(amount)} যোগ করা হয়েছে!",
                "new_balance": user["coins"]
            }
        
        return {"success": False, "message": "অজানা একশন!"}
    
    async def create_backup(self, admin_id: int) -> Dict:
        """Create database backup"""
        if not self.is_admin(admin_id):
            return {"success": False, "message": "অনুমতি নেই!"}
        
        success = self.db.create_backup()
        
        if success:
            return {"success": True, "message": "✅ ডাটাবেস ব্যাকআপ তৈরি হয়েছে!"}
        else:
            return {"success": False, "message": "❌ ব্যাকআপ ব্যর্থ হয়েছে!"}
    
    async def get_user_info(self, user_id: int) -> str:
        """Get detailed user information"""
        user = self.db.get_user(user_id)
        if not user:
            return "❌ ইউজার খুঁজে পাওয়া যায়নি!"
        
        level_info = Utils.calculate_level(user.get("xp", 0))
        
        info = f"""
📋 **ইউজার তথ্য:** #{user_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 **ব্যক্তিগত:**
• নাম: {user.get('first_name', 'N/A')} {user.get('last_name', '')}
• ইউজারনেম: @{user.get('username', 'N/A')}
• জয়েন করেছেন: {user.get('joined', 'N/A')[:10]}

🏆 **স্ট্যাটাস:**
• লেভেল: {level_info['level']}
• XP: {level_info['xp']}/{level_info['xp_needed']}
• প্রোগ্রেস: {Utils.create_progress_bar(level_info['xp'], level_info['xp_needed'])}
• সতর্কতা: {user.get('warnings', 0)}/3

💰 **ইকোনমি:**
• ব্যালেন্স: {Utils.format_currency(user.get('balance', 0))}
• কয়েন: {Utils.format_coins(user.get('coins', 0))}
• ডেইলি স্ট্রীক: {user.get('daily_streak', 0)} দিন

📊 **অ্যাকটিভিটি:**
• মোট মেসেজ: {user.get('total_messages', 0)}
• শেষ দেখা: {user.get('last_seen', 'N/A')[:16]}
• ইনভেন্টরি আইটেম: {len(user.get('inventory', []))}

🚨 **স্ট্যাটাস:** {"❌ ব্যান" if user.get('is_banned') else "✅ অ্যাকটিভ"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        return info