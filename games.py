import random
from typing import Dict, Tuple
from datetime import datetime
from db import Database
from utils import Utils

class GamesManager:
    """All games in one class"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def play_dice(self, user_id: int, bet: int) -> Dict:
        """Dice game"""
        if bet < 10:
            return {"success": False, "message": "ন্যূনতম বেট 10 কয়েন"}
        
        user = self.db.get_user(user_id)
        if not user or user["coins"] < bet:
            return {"success": False, "message": "পর্যাপ্ত কয়েন নেই!"}
        
        # Roll dice
        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)
        
        # Determine winner
        if user_roll > bot_roll:
            win_amount = bet * 2
            user["coins"] += win_amount
            result = "WIN"
            message = f"🎲 আপনি পেলেন: {user_roll}\n🤖 বট পেলো: {bot_roll}\n🎉 আপনি জিতেছেন! +{win_amount} কয়েন"
        elif user_roll < bot_roll:
            user["coins"] -= bet
            result = "LOSE"
            message = f"🎲 আপনি পেলেন: {user_roll}\n🤖 বট পেলো: {bot_roll}\n😢 আপনি হারলেন! -{bet} কয়েন"
        else:
            result = "DRAW"
            message = f"🎲 আপনি পেলেন: {user_roll}\n🤖 বট পেলো: {bot_roll}\n🤝 ড্র হয়েছে!"
        
        # Update user
        self.db.update_user(user_id, {"coins": user["coins"]})
        
        # Record game stats
        self.db.update_game_stats(user_id, "dice", result == "WIN", bet if result == "WIN" else -bet)
        
        return {
            "success": True,
            "result": result,
            "message": message,
            "user_roll": user_roll,
            "bot_roll": bot_roll,
            "coins": user["coins"]
        }
    
    async def play_slot(self, user_id: int, bet: int) -> Dict:
        """Slot machine game"""
        if bet < 20:
            return {"success": False, "message": "ন্যূনতম বেট 20 কয়েন"}
        
        user = self.db.get_user(user_id)
        if not user or user["coins"] < bet:
            return {"success": False, "message": "পর্যাপ্ত কয়েন নেই!"}
        
        # Slot symbols
        symbols = ["🍒", "🍋", "⭐", "7️⃣", "🔔", "💎"]
        
        # Generate slots
        slots = [random.choice(symbols) for _ in range(3)]
        
        # Check win
        if slots[0] == slots[1] == slots[2]:
            # Jackpot
            multiplier = 10
            result = "JACKPOT"
        elif slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:
            # Partial win
            multiplier = 2
            result = "WIN"
        else:
            multiplier = 0
            result = "LOSE"
        
        # Calculate winnings
        if result != "LOSE":
            win_amount = bet * multiplier
            user["coins"] += win_amount
            message = f"{slots[0]} | {slots[1]} | {slots[2]}\n🎉 {result}! +{win_amount} কয়েন"
        else:
            user["coins"] -= bet
            message = f"{slots[0]} | {slots[1]} | {slots[2]}\n😢 হারলেন! -{bet} কয়েন"
        
        # Update user
        self.db.update_user(user_id, {"coins": user["coins"]})
        
        # Record game stats
        self.db.update_game_stats(user_id, "slot", result != "LOSE", 
                                win_amount if result != "LOSE" else -bet)
        
        return {
            "success": True,
            "result": result,
            "message": message,
            "slots": slots,
            "coins": user["coins"]
        }
    
    async def play_quiz(self, user_id: int) -> Dict:
        """Quiz game"""
        questions = [
            {
                "question": "বাংলাদেশের জাতীয় পাখি কি?",
                "options": ["দোয়েল", "ময়ূর", "কাক", "শালিক"],
                "answer": 0
            },
            {
                "question": "বাংলাদেশের স্বাধীনতা দিবস কবে?",
                "options": ["২৬ মার্চ", "১৬ ডিসেম্বর", "২১ ফেব্রুয়ারি", "৭ মার্চ"],
                "answer": 0
            },
            {
                "question": "বাংলাদেশের জাতীয় ফুল কি?",
                "options": ["গোলাপ", "শাপলা", "জবা", "বেলি"],
                "answer": 1
            },
            {
                "question": "পদ্মা সেতুর দৈর্ঘ্য কত কিমি?",
                "options": ["৬.১৫ কিমি", "৫.৮ কিমি", "৭.২ কিমি", "৬.৫ কিমি"],
                "answer": 0
            },
            {
                "question": "বাংলাদেশের প্রথম প্রধানমন্ত্রী কে?",
                "options": ["শেখ মুজিবুর রহমান", "তাজউদ্দিন আহমেদ", "খন্দকার মোশতাক আহমেদ", "জিয়াউর রহমান"],
                "answer": 1
            }
        ]
        
        question = random.choice(questions)
        
        return {
            "success": True,
            "question": question["question"],
            "options": question["options"],
            "correct_index": question["answer"],
            "reward": 50  # Coins for correct answer
        }
    
    async def check_quiz_answer(self, user_id: int, question_idx: int, answer_idx: int) -> Dict:
        """Check quiz answer"""
        # For simplicity, using predefined questions
        questions = [
            {"answer": 0},
            {"answer": 0},
            {"answer": 1},
            {"answer": 0},
            {"answer": 1}
        ]
        
        if question_idx >= len(questions):
            return {"success": False, "message": "ভুল প্রশ্ন!"}
        
        user = self.db.get_user(user_id)
        correct = questions[question_idx]["answer"] == answer_idx
        
        if correct:
            reward = 50
            user["coins"] += reward
            self.db.update_user(user_id, {"coins": user["coins"]})
            message = f"✅ সঠিক উত্তর! 🎉 +{reward} কয়েন"
        else:
            reward = 0
            message = "❌ ভুল উত্তর!"
        
        self.db.update_game_stats(user_id, "quiz", correct, reward)
        
        return {
            "success": True,
            "correct": correct,
            "message": message,
            "reward": reward,
            "coins": user["coins"] if user else 0
        }
    
    async def daily_bonus(self, user_id: int) -> Dict:
        """Daily bonus claim"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        last_daily = user.get("last_daily")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if last_daily == today:
            return {"success": False, "message": "আজকের বোনাস ইতিমধ্যে নিয়েছেন!"}
        
        # Calculate streak bonus
        streak = user.get("daily_streak", 0)
        if last_daily and (datetime.now() - datetime.fromisoformat(last_daily)).days == 1:
            streak += 1
        else:
            streak = 1
        
        # Calculate bonus
        base_bonus = 50
        streak_bonus = min(streak * 10, 100)  # Max 100 extra
        total_bonus = base_bonus + streak_bonus
        
        # Update user
        user["coins"] += total_bonus
        user["daily_streak"] = streak
        user["last_daily"] = today
        
        self.db.update_user(user_id, {
            "coins": user["coins"],
            "daily_streak": streak,
            "last_daily": today
        })
        
        return {
            "success": True,
            "bonus": total_bonus,
            "streak": streak,
            "message": f"🎁 ডেইলি বোনাস! +{total_bonus} কয়েন\n🔥 {streak} দিন স্ট্রীক!",
            "coins": user["coins"]
        }