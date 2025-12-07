import random
from datetime import datetime
from typing import List, Dict, Any
import json
import os

class Utils:
    """Utility functions for the bot"""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency with symbol"""
        return f"৳{amount:,.2f}"
    
    @staticmethod
    def format_coins(coins: int) -> str:
        """Format coins"""
        return f"🪙 {coins:,}"
    
    @staticmethod
    def create_progress_bar(current: int, total: int, length: int = 10) -> str:
        """Create progress bar"""
        filled = int((current / total) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {current}/{total}"
    
    @staticmethod
    def calculate_level(xp: int) -> dict:
        """Calculate level from XP"""
        level = 1
        xp_needed = 100
        
        while xp >= xp_needed:
            xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.5)
        
        return {
            "level": level,
            "xp": xp,
            "xp_needed": xp_needed,
            "progress": (xp / xp_needed) * 100 if xp_needed > 0 else 100
        }
    
    @staticmethod
    def generate_receipt(payment_data: Dict) -> str:
        """Generate payment receipt"""
        receipt = f"""
╔══════════════════════════════════════════╗
║           PAYMENT RECEIPT               ║
╠══════════════════════════════════════════╣
║ ID: {payment_data.get('id', 'N/A'):<32} ║
║ User: {payment_data.get('user_id', 'N/A'):<30} ║
║ Amount: {Utils.format_currency(payment_data.get('amount', 0)):<27} ║
║ Method: {payment_data.get('method', 'N/A'):<30} ║
║ Status: {payment_data.get('status', 'PENDING'):<30} ║
║ Time: {payment_data.get('time', datetime.now().strftime('%H:%M %d/%m/%Y')):<28} ║
╚══════════════════════════════════════════╝
        """
        return receipt
    
    @staticmethod
    def get_random_quote() -> str:
        """Get random motivational quote"""
        quotes = [
            "জয়ী হওয়ার ইচ্ছাই সফলতা আনে!",
            "কঠোর পরিশ্রম কখনো বিফলে যায় না।",
            "আত্মবিশ্বাসই হল প্রথম সফলতা।",
            "যতবার পড়বে, ততবার শিখবে।",
            "সফলতা পেতে হলে প্রথমে বিশ্বাস করতে হবে।"
        ]
        return random.choice(quotes)
    
    @staticmethod
    def validate_phone(number: str) -> bool:
        """Validate Bangladeshi phone number"""
        if len(number) != 11:
            return False
        if not number.startswith('01'):
            return False
        if not number[2] in ['3', '4', '5', '6', '7', '8', '9']:
            return False
        return number.isdigit()
    
    @staticmethod
    def generate_referral_code(user_id: int) -> str:
        """Generate referral code"""
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        code = ''.join(random.choices(chars, k=6))
        return f"REF{user_id % 1000}{code}"
    
    @staticmethod
    def format_time_delta(seconds: int) -> str:
        """Format seconds to human readable time"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days} দিন")
        if hours > 0:
            parts.append(f"{hours} ঘন্টা")
        if minutes > 0:
            parts.append(f"{minutes} মিনিট")
        if secs > 0 or not parts:
            parts.append(f"{secs} সেকেন্ড")
        
        return " ".join(parts)