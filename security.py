import re
from typing import Dict, List
from db import Database

class SecurityManager:
    """Security and moderation system"""
    
    def __init__(self, db: Database):
        self.db = db
        self.spam_detection = {}
        
        # Bad words list (Bengali)
        self.bad_words = [
            "খারাপ", "অশ্লীল", "গালি", "অপমান"
        ]
        
        # Spam patterns
        self.spam_patterns = [
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            r"@everyone",
            r"@admin",
            r"স্প্যাম"
        ]
    
    def check_message(self, user_id: int, message: str, message_type: str = "text") -> Dict:
        """Check message for security violations"""
        violations = []
        
        # Check for spam
        if self._is_spam(user_id, message):
            violations.append("spam")
        
        # Check for bad words
        if self._contains_bad_words(message):
            violations.append("bad_words")
        
        # Check for links (if not allowed)
        if self._contains_links(message) and message_type == "text":
            violations.append("links")
        
        if violations:
            # Update warning count
            user = self.db.get_user(user_id)
            if user:
                warnings = user.get("warnings", 0) + 1
                self.db.update_user(user_id, {"warnings": warnings})
            
            return {
                "safe": False,
                "violations": violations,
                "action": "warn" if len(violations) < 3 else "ban"
            }
        
        return {"safe": True, "violations": []}
    
    def _is_spam(self, user_id: int, message: str) -> bool:
        """Check if message is spam"""
        # Simple spam detection
        if user_id not in self.spam_detection:
            self.spam_detection[user_id] = {
                "count": 0,
                "last_message": "",
                "timestamp": 0
            }
        
        user_data = self.spam_detection[user_id]
        
        # Check for duplicate messages
        if message == user_data["last_message"]:
            user_data["count"] += 1
        else:
            user_data["count"] = 1
            user_data["last_message"] = message
        
        # Reset after 10 seconds
        import time
        if time.time() - user_data["timestamp"] > 10:
            user_data["count"] = 0
        
        user_data["timestamp"] = time.time()
        
        return user_data["count"] > 3  # More than 3 same messages is spam
    
    def _contains_bad_words(self, text: str) -> bool:
        """Check for bad words"""
        text_lower = text.lower()
        for word in self.bad_words:
            if word in text_lower:
                return True
        return False
    
    def _contains_links(self, text: str) -> bool:
        """Check for links"""
        for pattern in self.spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize user input"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long
        if len(text) > 2000:
            text = text[:1997] + "..."
        
        # Escape special characters for Markdown
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def validate_amount(self, amount_str: str, max_amount: float = 100000) -> Dict:
        """Validate amount input"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                return {"valid": False, "error": "অ্যামাউন্ট শূন্য বা নেগেটিভ হতে পারবে না!"}
            if amount > max_amount:
                return {"valid": False, "error": f"সর্বোচ্চ অ্যামাউন্ট {max_amount}!"}
            if amount < 0.01:
                return {"valid": False, "error": "ন্যূনতম অ্যামাউন্ট ০.০১!"}
            
            return {"valid": True, "amount": amount}
        except ValueError:
            return {"valid": False, "error": "সঠিক সংখ্যা দিন!"}