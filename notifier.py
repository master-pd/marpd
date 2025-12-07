import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class Notifier:
    """Notification system"""
    
    def __init__(self, db):
        self.db = db
        self.notifications = []
        self.user_notifications = {}
    
    async def send_notification(self, user_id: int, title: str, message: str, 
                               notification_type: str = "info") -> bool:
        """Send notification to user"""
        try:
            notification = {
                "id": f"notif_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "timestamp": datetime.now().isoformat(),
                "read": False
            }
            
            # Store notification
            self.notifications.append(notification)
            
            # Store in user's notifications
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            
            self.user_notifications[user_id].append(notification)
            
            # Limit notifications per user
            if len(self.user_notifications[user_id]) > 100:
                self.user_notifications[user_id] = self.user_notifications[user_id][-100:]
            
            print(f"📢 Notification sent to {user_id}: {title}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
            return False
    
    async def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Dict]:
        """Get user notifications"""
        if user_id not in self.user_notifications:
            return []
        
        notifications = self.user_notifications[user_id]
        
        if unread_only:
            notifications = [n for n in notifications if not n.get("read", False)]
        
        return sorted(notifications, key=lambda x: x["timestamp"], reverse=True)[:50]
    
    async def mark_as_read(self, user_id: int, notification_id: str) -> bool:
        """Mark notification as read"""
        if user_id not in self.user_notifications:
            return False
        
        for notification in self.user_notifications[user_id]:
            if notification["id"] == notification_id:
                notification["read"] = True
                return True
        
        return False
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """Mark all user notifications as read"""
        if user_id not in self.user_notifications:
            return 0
        
        count = 0
        for notification in self.user_notifications[user_id]:
            if not notification.get("read", False):
                notification["read"] = True
                count += 1
        
        return count
    
    async def delete_notification(self, user_id: int, notification_id: str) -> bool:
        """Delete notification"""
        if user_id not in self.user_notifications:
            return False
        
        for i, notification in enumerate(self.user_notifications[user_id]):
            if notification["id"] == notification_id:
                del self.user_notifications[user_id][i]
                
                # Also remove from main list
                for j, n in enumerate(self.notifications):
                    if n["id"] == notification_id:
                        del self.notifications[j]
                        break
                
                return True
        
        return False
    
    async def clear_old_notifications(self, days_old: int = 30):
        """Clear old notifications"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Clear from main list
        initial_count = len(self.notifications)
        self.notifications = [
            n for n in self.notifications
            if datetime.fromisoformat(n["timestamp"]) > cutoff_date
        ]
        
        # Clear from user notifications
        cleared_count = initial_count - len(self.notifications)
        
        for user_id in self.user_notifications:
            self.user_notifications[user_id] = [
                n for n in self.user_notifications[user_id]
                if datetime.fromisoformat(n["timestamp"]) > cutoff_date
            ]
        
        print(f"🧹 Cleared {cleared_count} old notifications (older than {days_old} days)")
        return cleared_count
    
    async def send_system_notification(self, title: str, message: str, 
                                      user_ids: Optional[List[int]] = None) -> Dict:
        """Send system notification to multiple users"""
        results = {
            "total_sent": 0,
            "failed": 0,
            "failed_users": []
        }
        
        if user_ids is None:
            # Send to all users
            user_ids = [int(uid) for uid in self.db.users.keys()]
        
        for user_id in user_ids:
            success = await self.send_notification(
                user_id, 
                f"🔔 {title}",
                message,
                "system"
            )
            
            if success:
                results["total_sent"] += 1
            else:
                results["failed"] += 1
                results["failed_users"].append(user_id)
        
        return results
    
    async def send_payment_notification(self, payment_data: Dict):
        """Send payment notification"""
        user_id = payment_data.get("user_id")
        amount = payment_data.get("amount", 0)
        payment_type = payment_data.get("type", "DEPOSIT")
        status = payment_data.get("status", "PENDING")
        
        if payment_type == "DEPOSIT":
            if status == "COMPLETED":
                await self.send_notification(
                    user_id,
                    "💰 ডিপোজিট কনফার্মড",
                    f"আপনার {amount} টাকা ডিপোজিট কনফার্ম হয়েছে!\n"
                    f"ব্যবহার করতে /balance কমান্ড দিন।",
                    "success"
                )
            elif status == "PENDING":
                await self.send_notification(
                    user_id,
                    "⏳ ডিপোজিট পেন্ডিং",
                    f"আপনার {amount} টাকা ডিপোজিট রিকোয়েস্ট রিসিভ হয়েছে।\n"
                    f"অ্যাডমিন শীঘ্রই চেক করবেন।",
                    "info"
                )
        
        elif payment_type == "WITHDRAW":
            if status == "COMPLETED":
                await self.send_notification(
                    user_id,
                    "✅ উইথড্র কনফার্মড",
                    f"আপনার {amount} টাকা উইথড্র কনফার্ম হয়েছে!\n"
                    f"২৪ ঘন্টার মধ্যে টাকা পেয়ে যাবেন।",
                    "success"
                )
            elif status == "PENDING":
                await self.send_notification(
                    user_id,
                    "⏳ উইথড্র প্রসেসিং",
                    f"আপনার {amount} টাকা উইথড্র রিকোয়েস্ট রিসিভ হয়েছে।\n"
                    f"অ্যাডমিন শীঘ্রই প্রসেস করবেন।",
                    "info"
                )
    
    async def send_game_notification(self, user_id: int, game_result: Dict):
        """Send game result notification"""
        game_type = game_result.get("game", "unknown")
        
        if game_type == "dice":
            await self.send_notification(
                user_id,
                "🎲 ডাইস গেম রেজাল্ট",
                game_result.get("message", "গেম শেষ হয়েছে!"),
                "game"
            )
        elif game_type == "slot":
            await self.send_notification(
                user_id,
                "🎰 স্লট গেম রেজাল্ট",
                game_result.get("message", "গেম শেষ হয়েছে!"),
                "game"
            )
        elif game_type == "quiz":
            await self.send_notification(
                user_id,
                "🧠 কুইজ রেজাল্ট",
                game_result.get("message", "কুইজ শেষ হয়েছে!"),
                "game"
            )
    
    async def get_notification_stats(self, user_id: int) -> Dict:
        """Get user notification statistics"""
        notifications = await self.get_user_notifications(user_id, unread_only=False)
        
        total = len(notifications)
        unread = len([n for n in notifications if not n.get("read", False)])
        
        return {
            "total_notifications": total,
            "unread_notifications": unread,
            "read_notifications": total - unread,
            "latest_notification": notifications[0]["timestamp"] if notifications else None
        }