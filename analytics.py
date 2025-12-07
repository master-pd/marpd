from datetime import datetime, timedelta
from typing import Dict, List
from db import Database

class Analytics:
    """Analytics and statistics system"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get_daily_stats(self, date_str: str = None) -> Dict:
        """Get daily statistics"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # This would normally query database for daily stats
        # For now, return simulated data
        return {
            "date": date_str,
            "new_users": 5,
            "active_users": 25,
            "total_messages": 150,
            "games_played": 30,
            "transactions": 8,
            "revenue": 500.00,
            "popular_game": "dice",
            "peak_hour": "20:00"
        }
    
    async def get_weekly_stats(self) -> Dict:
        """Get weekly statistics"""
        week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        week_end = datetime.now().strftime("%Y-%m-%d")
        
        return {
            "period": f"{week_start} to {week_end}",
            "total_new_users": 35,
            "total_active_users": 120,
            "total_messages": 850,
            "total_games": 210,
            "total_transactions": 45,
            "total_revenue": 2500.00,
            "avg_daily_users": 17,
            "most_active_day": "Saturday",
            "growth_rate": "+12.5%"
        }
    
    async def get_user_growth(self, days: int = 30) -> List[Dict]:
        """Get user growth data"""
        growth_data = []
        
        # Simulated growth data
        base_users = 100
        for i in range(days, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_growth = max(0, (days - i) * 2 + (i % 3))
            
            growth_data.append({
                "date": date,
                "total_users": base_users + daily_growth,
                "new_users": daily_growth if i < days else 0,
                "active_users": int((base_users + daily_growth) * 0.3)
            })
        
        return growth_data
    
    async def get_game_analytics(self) -> Dict:
        """Get game analytics"""
        # Collect game statistics from database
        game_stats = {}
        
        for key, stats in self.db.games.items():
            game_type = key.split("_")[-1] if "_" in key else "unknown"
            
            if game_type not in game_stats:
                game_stats[game_type] = {
                    "plays": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_won": 0,
                    "total_lost": 0
                }
            
            game_stats[game_type]["plays"] += stats.get("plays", 0)
            game_stats[game_type]["wins"] += stats.get("wins", 0)
            game_stats[game_type]["losses"] += stats.get("losses", 0)
            game_stats[game_type]["total_won"] += stats.get("total_won", 0)
            game_stats[game_type]["total_lost"] += stats.get("total_lost", 0)
        
        # Calculate percentages
        for game_type in game_stats:
            stats = game_stats[game_type]
            total_plays = stats["plays"]
            
            if total_plays > 0:
                stats["win_rate"] = (stats["wins"] / total_plays) * 100
                stats["avg_win"] = stats["total_won"] / max(stats["wins"], 1)
                stats["avg_loss"] = stats["total_lost"] / max(stats["losses"], 1)
            else:
                stats["win_rate"] = 0
                stats["avg_win"] = 0
                stats["avg_loss"] = 0
        
        return game_stats
    
    async def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Get top users by coins"""
        users_list = []
        
        for user_id_str, user_data in self.db.users.items():
            users_list.append({
                "user_id": int(user_id_str),
                "username": user_data.get("username", ""),
                "coins": user_data.get("coins", 0),
                "level": user_data.get("level", 1),
                "total_messages": user_data.get("total_messages", 0)
            })
        
        # Sort by coins (descending)
        users_list.sort(key=lambda x: x["coins"], reverse=True)
        
        return users_list[:limit]
    
    async def get_revenue_report(self) -> Dict:
        """Get revenue report"""
        # Analyze payment data
        payments = self.db.payments.values()
        
        total_revenue = 0
        completed_payments = 0
        pending_payments = 0
        method_breakdown = {}
        
        for payment in payments:
            if payment.get("type") == "DEPOSIT" and payment.get("status") == "COMPLETED":
                amount = payment.get("amount", 0)
                total_revenue += amount
                completed_payments += 1
                
                method = payment.get("method", "unknown")
                method_breakdown[method] = method_breakdown.get(method, 0) + amount
            
            elif payment.get("status") == "PENDING":
                pending_payments += 1
        
        return {
            "total_revenue": total_revenue,
            "completed_payments": completed_payments,
            "pending_payments": pending_payments,
            "method_breakdown": method_breakdown,
            "avg_transaction": total_revenue / max(completed_payments, 1)
        }
    
    async def get_system_health(self) -> Dict:
        """Get system health metrics"""
        total_users = len(self.db.users)
        active_users = sum(1 for u in self.db.users.values() 
                          if (datetime.now() - datetime.fromisoformat(u.get("last_seen", "2020-01-01"))).days < 7)
        
        total_coins = sum(u.get("coins", 0) for u in self.db.users.values())
        total_messages = sum(u.get("total_messages", 0) for u in self.db.users.values())
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "activity_rate": (active_users / max(total_users, 1)) * 100,
            "total_coins": total_coins,
            "avg_coins_per_user": total_coins / max(total_users, 1),
            "total_messages": total_messages,
            "avg_messages_per_user": total_messages / max(total_users, 1),
            "database_size": "N/A",
            "uptime": "100%",
            "last_backup": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    
    async def generate_report(self, report_type: str = "daily") -> str:
        """Generate formatted report"""
        if report_type == "daily":
            stats = await self.get_daily_stats()
            
            report = f"""
📊 **দৈনিক রিপোর্ট** - {stats['date']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 **ইউজার স্ট্যাটস:**
• নতুন ইউজার: {stats['new_users']}
• অ্যাকটিভ ইউজার: {stats['active_users']}
• টোটাল মেসেজ: {stats['total_messages']}

🎮 **গেম স্ট্যাটস:**
• গেম খেলা হয়েছে: {stats['games_played']}
• জনপ্রিয় গেম: {stats['popular_game']}
• পিক আওয়ার: {stats['peak_hour']}

💰 **ফাইন্যান্সিয়াল:**
• ট্রানজেকশন: {stats['transactions']}
• রাজস্ব: ৳{stats['revenue']:,.2f}

📈 **সারাংশ:**
আজকে {stats['new_users']} জন নতুন ইউজার যোগ দিয়েছেন।
{stats['active_users']} জন ইউজার অ্যাকটিভ ছিলেন।
            """
            
        elif report_type == "weekly":
            stats = await self.get_weekly_stats()
            
            report = f"""
📊 **সাপ্তাহিক রিপোর্ট** - {stats['period']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 **ইউজার গ্রোথ:**
• নতুন ইউজার: {stats['total_new_users']}
• অ্যাকটিভ ইউজার: {stats['total_active_users']}
• ডেইলি অ্যাভারেজ: {stats['avg_daily_users']}
• গ্রোথ রেট: {stats['growth_rate']}

🎮 **গেম অ্যাকটিভিটি:**
• টোটাল গেম: {stats['total_games']}
• টোটাল মেসেজ: {stats['total_messages']}
• সবচেয়ে অ্যাকটিভ দিন: {stats['most_active_day']}

💰 **ফাইন্যান্সিয়াল:**
• টোটাল ট্রানজেকশন: {stats['total_transactions']}
• টোটাল রাজস্ব: ৳{stats['total_revenue']:,.2f}

🏆 **সাফল্য:**
এই সপ্তাহে {stats['total_new_users']} জন নতুন ইউজার যোগ দিয়েছেন।
{stats['growth_rate']} গ্রোথ রেকর্ড করা হয়েছে।
            """
        
        else:
            report = "❌ অজানা রিপোর্ট টাইপ!"
        
        return report