import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading

class Database:
    """Simple JSON-based database for Termux"""
    
    def __init__(self):
        self.data_dir = "data"
        self.backup_dir = "backups"
        
        # Create directories if not exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Initialize data
        self.users = self._load_json("users.json", {})
        self.payments = self._load_json("payments.json", {})
        self.shop = self._load_json("shop.json", self._default_shop())
        self.games = self._load_json("games.json", {})
        self.groups = self._load_json("groups.json", {})
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        print("✅ Database initialized (JSON Storage)")
    
    def _load_json(self, filename: str, default=None):
        """Load JSON file"""
        path = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading {filename}: {e}")
        return default if default is not None else {}
    
    def _save_json(self, filename: str, data):
        """Save JSON file"""
        path = os.path.join(self.data_dir, filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving {filename}: {e}")
            return False
    
    def _default_shop(self):
        """Default shop items"""
        return {
            "items": [
                {
                    "id": "vip_badge",
                    "name": "VIP Badge",
                    "price": 500,
                    "description": "Exclusive VIP Status",
                    "icon": "👑"
                },
                {
                    "id": "color_name",
                    "name": "Color Name",
                    "price": 300,
                    "description": "Colored name in chat",
                    "icon": "🎨"
                },
                {
                    "id": "double_xp",
                    "name": "2x XP (24h)",
                    "price": 200,
                    "description": "Double experience for 24 hours",
                    "icon": "⚡"
                },
                {
                    "id": "coin_boost",
                    "name": "Coin Booster",
                    "price": 150,
                    "description": "+50% coins for 3 days",
                    "icon": "💰"
                }
            ]
        }
    
    # User Management
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        with self.lock:
            return self.users.get(str(user_id))
    
    def create_user(self, user_id: int, user_info: Dict) -> Dict:
        """Create new user"""
        with self.lock:
            user_data = {
                "id": user_id,
                "username": user_info.get("username", ""),
                "first_name": user_info.get("first_name", ""),
                "balance": 100.0,  # Welcome bonus
                "coins": 100,
                "level": 1,
                "xp": 0,
                "daily_streak": 0,
                "last_daily": None,
                "warnings": 0,
                "inventory": [],
                "joined": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "total_messages": 0,
                "referrals": [],
                "settings": {
                    "language": "bn",
                    "notifications": True
                }
            }
            
            self.users[str(user_id)] = user_data
            self._save_json("users.json", self.users)
            return user_data
    
    def update_user(self, user_id: int, updates: Dict) -> bool:
        """Update user data"""
        with self.lock:
            user_id_str = str(user_id)
            if user_id_str in self.users:
                self.users[user_id_str].update(updates)
                self.users[user_id_str]["last_seen"] = datetime.now().isoformat()
                self._save_json("users.json", self.users)
                return True
            return False
    
    # Payments
    def add_payment(self, payment_data: Dict) -> str:
        """Add payment record"""
        with self.lock:
            payment_id = f"pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            payment_data["id"] = payment_id
            payment_data["created_at"] = datetime.now().isoformat()
            
            self.payments[payment_id] = payment_data
            self._save_json("payments.json", self.payments)
            return payment_id
    
    def get_payments(self, user_id: int) -> list:
        """Get user's payments"""
        user_payments = []
        for payment in self.payments.values():
            if payment.get("user_id") == user_id:
                user_payments.append(payment)
        return sorted(user_payments, key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Shop
    def get_shop_items(self) -> list:
        """Get all shop items"""
        return self.shop.get("items", [])
    
    def buy_item(self, user_id: int, item_id: str) -> bool:
        """User buys an item"""
        with self.lock:
            user = self.get_user(user_id)
            if not user:
                return False
            
            item = next((i for i in self.shop["items"] if i["id"] == item_id), None)
            if not item:
                return False
            
            if user["coins"] >= item["price"]:
                user["coins"] -= item["price"]
                user["inventory"].append({
                    "item_id": item_id,
                    "name": item["name"],
                    "purchased_at": datetime.now().isoformat()
                })
                
                self.update_user(user_id, user)
                return True
            
            return False
    
    # Games
    def update_game_stats(self, user_id: int, game_type: str, won: bool, amount: int = 0):
        """Update game statistics"""
        with self.lock:
            game_key = f"{user_id}_{game_type}"
            if game_key not in self.games:
                self.games[game_key] = {
                    "plays": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_won": 0,
                    "total_lost": 0
                }
            
            stats = self.games[game_key]
            stats["plays"] += 1
            
            if won:
                stats["wins"] += 1
                stats["total_won"] += amount
            else:
                stats["losses"] += 1
                stats["total_lost"] += amount
            
            self._save_json("games.json", self.games)
    
    # Backup
    def create_backup(self):
        """Create database backup"""
        with self.lock:
            backup_data = {
                "users": self.users,
                "payments": self.payments,
                "timestamp": datetime.now().isoformat()
            }
            
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = os.path.join(self.backup_dir, backup_file)
            
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)
                print(f"✅ Backup created: {backup_file}")
                return True
            except Exception as e:
                print(f"❌ Backup failed: {e}")
                return False
    
    # Statistics
    def get_stats(self) -> Dict:
        """Get bot statistics"""
        with self.lock:
            total_users = len(self.users)
            active_users = sum(1 for u in self.users.values() 
                             if (datetime.now() - datetime.fromisoformat(u.get("last_seen", "2020-01-01"))).days < 7)
            
            total_coins = sum(u.get("coins", 0) for u in self.users.values())
            total_payments = len(self.payments)
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_coins": total_coins,
                "total_payments": total_payments,
                "shop_items": len(self.shop.get("items", [])),
                "backup_time": datetime.now().isoformat()
            }