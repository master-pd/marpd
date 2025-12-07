from typing import List, Dict, Optional
from db import Database
from utils import Utils

class ShopManager:
    """Shop management system"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_shop_items(self) -> List[Dict]:
        """Get all shop items"""
        return self.db.get_shop_items()
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get specific item by ID"""
        items = self.get_shop_items()
        for item in items:
            if item["id"] == item_id:
                return item
        return None
    
    async def buy_item(self, user_id: int, item_id: str) -> Dict:
        """Buy an item"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "আইটেম খুঁজে পাওয়া যায়নি!"}
        
        if user["coins"] < item["price"]:
            return {"success": False, "message": f"পর্যাপ্ত কয়েন নেই! দাম: {Utils.format_coins(item['price'])}"}
        
        # Process purchase
        success = self.db.buy_item(user_id, item_id)
        
        if success:
            return {
                "success": True,
                "message": f"✅ {item['name']} কিনেছেন! -{Utils.format_coins(item['price'])}",
                "item": item,
                "coins": user["coins"] - item["price"]
            }
        else:
            return {"success": False, "message": "ক্রয় ব্যর্থ হয়েছে!"}
    
    async def get_user_inventory(self, user_id: int) -> str:
        """Get user's inventory"""
        user = self.db.get_user(user_id)
        if not user or not user.get("inventory"):
            return "📦 আপনার ইনভেন্টরিতে কোনো আইটেম নেই!"
        
        inventory = user["inventory"]
        items = self.get_shop_items()
        
        inventory_text = "🛍️ **আপনার ইনভেন্টরি:**\n\n"
        
        # Count items
        item_counts = {}
        for inv_item in inventory:
            item_id = inv_item.get("item_id")
            if item_id:
                item_counts[item_id] = item_counts.get(item_id, 0) + 1
        
        # Display items
        for item_id, count in item_counts.items():
            item = self.get_item_by_id(item_id)
            if item:
                inventory_text += f"{item.get('icon', '📦')} {item['name']} ×{count}\n"
                if "description" in item:
                    inventory_text += f"   📝 {item['description']}\n"
                inventory_text += "\n"
        
        return inventory_text
    
    async def use_item(self, user_id: int, item_id: str) -> Dict:
        """Use an item from inventory"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        # Find item in inventory
        item_index = -1
        for i, inv_item in enumerate(user.get("inventory", [])):
            if inv_item.get("item_id") == item_id:
                item_index = i
                break
        
        if item_index == -1:
            return {"success": False, "message": "এই আইটেম আপনার ইনভেন্টরিতে নেই!"}
        
        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "আইটেম খুঁজে পাওয়া যায়নি!"}
        
        # Remove from inventory
        user["inventory"].pop(item_index)
        self.db.update_user(user_id, {"inventory": user["inventory"]})
        
        # Apply item effects
        effects = self._apply_item_effect(user_id, item)
        
        return {
            "success": True,
            "message": f"✅ {item['name']} ব্যবহার করা হয়েছে!\n{effects}",
            "item": item
        }
    
    def _apply_item_effect(self, user_id: int, item: Dict) -> str:
        """Apply item effect"""
        item_type = item.get("type", "")
        
        if item_type == "double_xp":
            # For demonstration, just add coins
            user = self.db.get_user(user_id)
            bonus = 100
            user["coins"] += bonus
            self.db.update_user(user_id, {"coins": user["coins"]})
            return f"⚡ +{bonus} কয়েন বোনাস!"
        
        elif item_type == "coin_boost":
            bonus = 200
            user = self.db.get_user(user_id)
            user["coins"] += bonus
            self.db.update_user(user_id, {"coins": user["coins"]})
            return f"💰 +{bonus} কয়েন বোনাস!"
        
        else:
            return f"🎁 {item['name']} সক্রিয় হয়েছে!"