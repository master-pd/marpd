import random
from typing import List, Dict
from db import Database

class Recommender:
    """Game and item recommendation system"""
    
    def __init__(self, db: Database):
        self.db = db
        
    async def recommend_game(self, user_id: int) -> Dict:
        """Recommend game based on user activity"""
        user = self.db.get_user(user_id)
        if not user:
            return self._get_random_game()
        
        # Analyze user preferences
        games_played = user.get("games_played", {})
        
        if not games_played:
            return self._get_random_game()
        
        # Find most played game
        most_played = max(games_played.items(), key=lambda x: x[1], default=("dice", 1))
        
        recommendations = {
            "dice": {
                "game": "dice",
                "message": "🎲 আপনার ডাইস গেমে ভালো পারফরম্যান্স! আজ আবার খেলুন!",
                "suggested_bet": min(user.get("coins", 100) // 10, 100)
            },
            "slot": {
                "game": "slot",
                "message": "🎰 স্লট মেশিনে আপনার ভাগ্য ভালো! আজ জ্যাকপট পেতে পারেন!",
                "suggested_bet": min(user.get("coins", 100) // 20, 50)
            },
            "quiz": {
                "game": "quiz",
                "message": "🧠 আপনি কুইজ গেমে দক্ষ! আজ নতুন প্রশ্ন চেষ্টা করুন!",
                "suggested_bet": 0
            }
        }
        
        return recommendations.get(most_played[0], self._get_random_game())
    
    def _get_random_game(self) -> Dict:
        """Get random game recommendation"""
        games = [
            {
                "game": "dice",
                "message": "🎲 নতুন ডাইস গেম খেলুন! সহজ এবং মজার!",
                "suggested_bet": 50
            },
            {
                "game": "slot",
                "message": "🎰 স্লট মেশিনে ভাগ্য পরীক্ষা করুন! জ্যাকপটের সুযোগ!",
                "suggested_bet": 30
            },
            {
                "game": "quiz",
                "message": "🧠 মজার কুইজ গেম! জ্ঞান পরীক্ষা করুন এবং কয়েন জিতুন!",
                "suggested_bet": 0
            }
        ]
        
        return random.choice(games)
    
    async def recommend_shop_item(self, user_id: int) -> Dict:
        """Recommend shop item based on user level and coins"""
        user = self.db.get_user(user_id)
        if not user:
            return self._get_random_item()
        
        user_coins = user.get("coins", 0)
        user_level = user.get("level", 1)
        
        items = self.db.get_shop_items()
        
        # Filter items user can afford
        affordable = [item for item in items if item["price"] <= user_coins]
        
        if not affordable:
            # Recommend cheapest item
            cheapest = min(items, key=lambda x: x["price"])
            return {
                "item": cheapest,
                "message": f"🎯 এই আইটেমটি কিনতে {cheapest['price'] - user_coins} কয়েন বেশি দরকার!",
                "reason": "affordable_goal"
            }
        
        # Recommend based on user level
        if user_level >= 10:
            # High level users get VIP items
            vip_items = [item for item in affordable if "vip" in item["name"].lower()]
            if vip_items:
                return {
                    "item": random.choice(vip_items),
                    "message": "👑 VIP আইটেম আপনার লেভেলের জন্য পারফেক্ট!",
                    "reason": "vip_status"
                }
        
        # Recommend useful items
        useful_items = [item for item in affordable if item["type"] in ["boost", "powerup"]]
        if useful_items:
            return {
                "item": random.choice(useful_items),
                "message": "⚡ এই বূস্টারটি আপনার গেমপ্লে উন্নত করবে!",
                "reason": "useful"
            }
        
        # Random recommendation
        return {
            "item": random.choice(affordable),
            "message": "🎁 এই আইটেমটি আপনার সংগ্রহে যোগ করুন!",
            "reason": "random"
        }
    
    def _get_random_item(self) -> Dict:
        """Get random item recommendation"""
        items = self.db.get_shop_items()
        if not items:
            return {
                "item": {"name": "VIP Badge", "price": 500, "description": "Exclusive VIP Status"},
                "message": "🛍️ শপ ব্রাউজ করুন!",
                "reason": "default"
            }
        
        return {
            "item": random.choice(items),
            "message": "🛍️ নতুন আইটেম চেক করুন!",
            "reason": "random"
        }
    
    async def get_daily_tip(self) -> str:
        """Get daily tip"""
        tips = [
            "💡 প্রতিদিন /daily কমান্ড দিয়ে ফ্রি কয়েন নিন!",
            "💡 ছোট বেট দিয়ে শুরু করুন, ধীরে ধীরে বাড়ান!",
            "💡 শপ থেকে উপকারী আইটেম কিনুন!",
            "💡 বন্ধুদের রেফার করে এক্সট্রা বোনাস পান!",
            "💡 কুইজ গেমে আপনার জ্ঞান পরীক্ষা করুন!",
            "💡 স্লট মেশিনে ভাগ্য চেষ্টা করুন!",
            "💡 বেশি অ্যাকটিভ থাকলে এক্সট্রা রিওয়ার্ড!",
            "💡 সাপ্তাহিক লিডারবোর্ডে টপ রাখার চেষ্টা করুন!"
        ]
        
        return random.choice(tips)
    
    async def get_motivational_quote(self) -> str:
        """Get motivational quote"""
        quotes = [
            "জয়ী হওয়ার ইচ্ছাই সফলতা আনে!",
            "কঠোর পরিশ্রম কখনো বিফলে যায় না।",
            "আত্মবিশ্বাসই হল প্রথম সফলতা।",
            "যতবার পড়বে, ততবার শিখবে।",
            "সফলতা পেতে হলে প্রথমে বিশ্বাস করতে হবে।",
            "পরিশ্রম সৌভাগ্যের প্রসূতি।",
            "ধৈর্য ধরে চেষ্টা করলে সফলতা আসবেই।",
            "ছোট ছোট স্বপ্ন নিয়ে শুরু করুন, বড় স্বপ্ন দেখুন।"
        ]
        
        return random.choice(quotes)