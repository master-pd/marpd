from typing import Dict, List, Optional
from datetime import datetime, timedelta
from db import Database

class Moderation:
    """Chat moderation system"""
    
    def __init__(self, db: Database):
        self.db = db
        self.warn_reasons = {
            "spam": "স্প্যাম মেসেজ",
            "bad_words": "অপমানজনক ভাষা",
            "links": "অনুমোদনহীন লিংক",
            "harassment": "হ্যারাসমেন্ট",
            "scam": "স্ক্যাম প্রচেষ্টা",
            "other": "অন্যান্য"
        }
        
        self.ban_durations = {
            1: 1,    # 1 warning = 1 hour mute
            2: 6,    # 2 warnings = 6 hours mute
            3: 24,   # 3 warnings = 24 hours mute
            4: 168,  # 4 warnings = 1 week ban
            5: 720   # 5 warnings = 1 month ban
        }
    
    async def warn_user(self, user_id: int, reason: str, 
                       warned_by: int, notes: str = "") -> Dict:
        """Warn a user"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        # Get current warnings
        current_warnings = user.get("warnings", 0)
        new_warnings = current_warnings + 1
        
        # Update user warnings
        user["warnings"] = new_warnings
        user["last_warning"] = datetime.now().isoformat()
        
        # Add warning to history
        if "warning_history" not in user:
            user["warning_history"] = []
        
        warning_entry = {
            "id": f"warn_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "reason": reason,
            "reason_text": self.warn_reasons.get(reason, "অজানা"),
            "warned_by": warned_by,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
            "warning_number": new_warnings
        }
        
        user["warning_history"].append(warning_entry)
        
        # Save changes
        self.db.update_user(user_id, {
            "warnings": new_warnings,
            "last_warning": user["last_warning"],
            "warning_history": user["warning_history"]
        })
        
        # Check if should be banned
        if new_warnings >= 3:
            ban_result = await self.ban_user(
                user_id, 
                f"অটো-ব্যান: {new_warnings}টি সতর্কতা",
                warned_by,
                self.ban_durations.get(new_warnings, 24)
            )
            
            return {
                "success": True,
                "message": f"⚠️ {user_id} কে সতর্কতা #{new_warnings} দেওয়া হয়েছে। ব্যান করা হয়েছে!",
                "warnings": new_warnings,
                "banned": True,
                "ban_info": ban_result
            }
        
        return {
            "success": True,
            "message": f"⚠️ {user_id} কে সতর্কতা #{new_warnings} দেওয়া হয়েছে।",
            "warnings": new_warnings,
            "banned": False
        }
    
    async def ban_user(self, user_id: int, reason: str, 
                      banned_by: int, duration_hours: int = 24) -> Dict:
        """Ban a user"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        # Calculate ban expiration
        ban_start = datetime.now()
        ban_end = ban_start + timedelta(hours=duration_hours)
        
        # Update user
        user["is_banned"] = True
        user["ban_reason"] = reason
        user["banned_by"] = banned_by
        user["ban_start"] = ban_start.isoformat()
        user["ban_end"] = ban_end.isoformat()
        user["ban_duration"] = duration_hours
        
        # Add to ban history
        if "ban_history" not in user:
            user["ban_history"] = []
        
        ban_entry = {
            "id": f"ban_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "reason": reason,
            "banned_by": banned_by,
            "duration": duration_hours,
            "start": ban_start.isoformat(),
            "end": ban_end.isoformat(),
            "warnings": user.get("warnings", 0)
        }
        
        user["ban_history"].append(ban_entry)
        
        # Save changes
        self.db.update_user(user_id, {
            "is_banned": True,
            "ban_reason": reason,
            "banned_by": banned_by,
            "ban_start": ban_start.isoformat(),
            "ban_end": ban_end.isoformat(),
            "ban_duration": duration_hours,
            "ban_history": user["ban_history"]
        })
        
        return {
            "success": True,
            "message": f"❌ {user_id} কে {duration_hours} ঘন্টার জন্য ব্যান করা হয়েছে।",
            "user_id": user_id,
            "reason": reason,
            "duration": duration_hours,
            "ends_at": ban_end.isoformat()
        }
    
    async def unban_user(self, user_id: int, unbanned_by: int, 
                        reason: str = "Appeal approved") -> Dict:
        """Unban a user"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        if not user.get("is_banned", False):
            return {"success": False, "message": "ইউজার ব্যান করা নেই!"}
        
        # Update user
        user["is_banned"] = False
        user["unbanned_by"] = unbanned_by
        user["unban_reason"] = reason
        user["unbanned_at"] = datetime.now().isoformat()
        
        # Reset warnings if ban was due to warnings
        if user.get("warnings", 0) >= 3:
            user["warnings"] = 0
        
        # Save changes
        self.db.update_user(user_id, {
            "is_banned": False,
            "unbanned_by": unbanned_by,
            "unban_reason": reason,
            "unbanned_at": user["unbanned_at"],
            "warnings": user.get("warnings", 0)
        })
        
        return {
            "success": True,
            "message": f"✅ {user_id} আনব্যান করা হয়েছে।",
            "user_id": user_id,
            "unbanned_by": unbanned_by
        }
    
    async def mute_user(self, user_id: int, duration_minutes: int, 
                       reason: str, muted_by: int) -> Dict:
        """Mute a user (temporary restriction)"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        # Calculate mute expiration
        mute_start = datetime.now()
        mute_end = mute_start + timedelta(minutes=duration_minutes)
        
        # Update user
        user["is_muted"] = True
        user["mute_reason"] = reason
        user["muted_by"] = muted_by
        user["mute_start"] = mute_start.isoformat()
        user["mute_end"] = mute_end.isoformat()
        user["mute_duration"] = duration_minutes
        
        # Save changes
        self.db.update_user(user_id, {
            "is_muted": True,
            "mute_reason": reason,
            "muted_by": muted_by,
            "mute_start": mute_start.isoformat(),
            "mute_end": mute_end.isoformat(),
            "mute_duration": duration_minutes
        })
        
        return {
            "success": True,
            "message": f"🔇 {user_id} কে {duration_minutes} মিনিটের জন্য মিউট করা হয়েছে।",
            "user_id": user_id,
            "reason": reason,
            "duration": duration_minutes,
            "ends_at": mute_end.isoformat()
        }
    
    async def check_ban_status(self, user_id: int) -> Optional[Dict]:
        """Check user's ban status"""
        user = self.db.get_user(user_id)
        if not user:
            return None
        
        if not user.get("is_banned", False):
            return None
        
        ban_end = user.get("ban_end")
        if ban_end:
            try:
                ban_end_time = datetime.fromisoformat(ban_end)
                if datetime.now() > ban_end_time:
                    # Ban expired, auto unban
                    await self.unban_user(user_id, 0, "Auto-unban: Ban expired")
                    return None
                
                time_left = ban_end_time - datetime.now()
                
                return {
                    "banned": True,
                    "reason": user.get("ban_reason", "Unknown"),
                    "ends_in": str(time_left),
                    "ends_at": ban_end,
                    "duration": user.get("ban_duration", 24),
                    "banned_by": user.get("banned_by", 0)
                }
            except:
                pass
        
        return {
            "banned": True,
            "reason": user.get("ban_reason", "Unknown"),
            "ends_in": "Unknown",
            "ends_at": "Unknown"
        }
    
    async def check_mute_status(self, user_id: int) -> Optional[Dict]:
        """Check user's mute status"""
        user = self.db.get_user(user_id)
        if not user:
            return None
        
        if not user.get("is_muted", False):
            return None
        
        mute_end = user.get("mute_end")
        if mute_end:
            try:
                mute_end_time = datetime.fromisoformat(mute_end)
                if datetime.now() > mute_end_time:
                    # Mute expired, auto unmute
                    self.db.update_user(user_id, {"is_muted": False})
                    return None
                
                time_left = mute_end_time - datetime.now()
                
                return {
                    "muted": True,
                    "reason": user.get("mute_reason", "Unknown"),
                    "ends_in": str(time_left),
                    "ends_at": mute_end,
                    "duration": user.get("mute_duration", 60),
                    "muted_by": user.get("muted_by", 0)
                }
            except:
                pass
        
        return {
            "muted": True,
            "reason": user.get("mute_reason", "Unknown"),
            "ends_in": "Unknown",
            "ends_at": "Unknown"
        }
    
    async def get_moderation_logs(self, limit: int = 50) -> List[Dict]:
        """Get moderation logs"""
        logs = []
        
        for user_id_str, user_data in self.db.users.items():
            user_id = int(user_id_str)
            
            # Check bans
            if user_data.get("is_banned", False):
                logs.append({
                    "type": "ban",
                    "user_id": user_id,
                    "username": user_data.get("username", "N/A"),
                    "reason": user_data.get("ban_reason", "Unknown"),
                    "by": user_data.get("banned_by", 0),
                    "time": user_data.get("ban_start", "Unknown"),
                    "duration": user_data.get("ban_duration", 24)
                })
            
            # Check warnings
            warning_history = user_data.get("warning_history", [])
            for warning in warning_history[-5:]:  # Last 5 warnings
                logs.append({
                    "type": "warning",
                    "user_id": user_id,
                    "username": user_data.get("username", "N/A"),
                    "reason": warning.get("reason_text", "Unknown"),
                    "by": warning.get("warned_by", 0),
                    "time": warning.get("timestamp", "Unknown"),
                    "warning_number": warning.get("warning_number", 0)
                })
        
        # Sort by time (newest first)
        logs.sort(key=lambda x: x.get("time", ""), reverse=True)
        
        return logs[:limit]
    
    async def clear_warnings(self, user_id: int, cleared_by: int) -> Dict:
        """Clear all warnings for a user"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        warnings_cleared = user.get("warnings", 0)
        
        # Update user
        user["warnings"] = 0
        user["warnings_cleared_by"] = cleared_by
        user["warnings_cleared_at"] = datetime.now().isoformat()
        
        # Save changes
        self.db.update_user(user_id, {
            "warnings": 0,
            "warnings_cleared_by": cleared_by,
            "warnings_cleared_at": user["warnings_cleared_at"]
        })
        
        return {
            "success": True,
            "message": f"🧹 {user_id} এর {warnings_cleared}টি সতর্কতা ক্লিয়ার করা হয়েছে।",
            "warnings_cleared": warnings_cleared,
            "cleared_by": cleared_by
        }