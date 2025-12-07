from datetime import datetime
from typing import Dict, Optional
from config import Config
from db import Database
from utils import Utils

class PaymentManager:
    """Manual payment manager"""
    
    def __init__(self, db: Database):
        self.db = db
        self.config = Config()
    
    async def request_deposit(self, user_id: int, amount: float, method: str) -> Dict:
        """Request deposit"""
        if amount < 10:
            return {"success": False, "message": "ন্যূনতম ডিপোজিট ৳10"}
        
        if method not in ["নগদ", "বিকাশ"]:
            return {"success": False, "message": "সাপোর্টেড মেথড: নগদ, বিকাশ"}
        
        payment_data = {
            "user_id": user_id,
            "amount": amount,
            "method": method,
            "status": "PENDING",
            "type": "DEPOSIT",
            "time": datetime.now().strftime("%H:%M %d/%m/%Y"),
            "instructions": self._get_payment_instructions(method, amount)
        }
        
        payment_id = self.db.add_payment(payment_data)
        
        return {
            "success": True,
            "payment_id": payment_id,
            "instructions": payment_data["instructions"],
            "message": "পেমেন্ট রিকোয়েস্ট তৈরি হয়েছে!"
        }
    
    def _get_payment_instructions(self, method: str, amount: float) -> str:
        """Get payment instructions"""
        if method == "নগদ":
            return f"""
💰 **নগদে পেমেন্ট করুন:**
📱 নম্বর: {self.config.NAGOD_NUMBER}
💵 Amount: {Utils.format_currency(amount)}
📌 Reference: MARPd-{datetime.now().strftime('%H%M')}

✅ পেমেন্টের পর স্ক্রিনশট পাঠান।
✅ অপেক্ষা করুন কনফার্মেশনের জন্য।
            """
        else:  # বিকাশ
            return f"""
💰 **বিকাশে পেমেন্ট করুন:**
📱 নম্বর: {self.config.BIKASH_NUMBER}
💵 Amount: {Utils.format_currency(amount)}
📌 Reference: MARPd-{datetime.now().strftime('%H%M')}

✅ পেমেন্টের পর লেনদেন আইডি (TrxID) পাঠান।
✅ অপেক্ষা করুন কনফার্মেশনের জন্য।
            """
    
    async def confirm_deposit(self, payment_id: str, admin_id: int) -> Dict:
        """Confirm deposit (admin only)"""
        if admin_id != self.config.BOT_OWNER_ID:
            return {"success": False, "message": "শুধুমাত্র অ্যাডমিন কনফার্ম করতে পারবেন!"}
        
        payment = self.db.payments.get(payment_id)
        if not payment:
            return {"success": False, "message": "পেমেন্ট খুঁজে পাওয়া যায়নি!"}
        
        if payment["status"] != "PENDING":
            return {"success": False, "message": f"পেমেন্ট ইতিমধ্যে {payment['status']}!"}
        
        # Update payment status
        payment["status"] = "COMPLETED"
        payment["confirmed_by"] = admin_id
        payment["confirmed_at"] = datetime.now().isoformat()
        
        # Add to user balance
        user = self.db.get_user(payment["user_id"])
        if user:
            user["balance"] = user.get("balance", 0) + payment["amount"]
            self.db.update_user(payment["user_id"], {"balance": user["balance"]})
        
        self.db._save_json("payments.json", self.db.payments)
        
        return {
            "success": True,
            "message": f"পেমেন্ট কনফার্ম হয়েছে! {Utils.format_currency(payment['amount'])} যোগ করা হয়েছে।"
        }
    
    async def request_withdraw(self, user_id: int, amount: float, method: str, number: str) -> Dict:
        """Request withdrawal"""
        user = self.db.get_user(user_id)
        if not user:
            return {"success": False, "message": "ইউজার খুঁজে পাওয়া যায়নি!"}
        
        if user["balance"] < amount:
            return {"success": False, "message": f"পর্যাপ্ত ব্যালেন্স নেই! আপনার ব্যালেন্স: {Utils.format_currency(user['balance'])}"}
        
        if amount < 50:
            return {"success": False, "message": "ন্যূনতম উইথড্র ৳50"}
        
        if not Utils.validate_phone(number):
            return {"success": False, "message": "সঠিক মোবাইল নম্বর দিন (11 ডিজিট)"}
        
        payment_data = {
            "user_id": user_id,
            "amount": amount,
            "method": method,
            "status": "PENDING",
            "type": "WITHDRAW",
            "account": number,
            "time": datetime.now().strftime("%H:%M %d/%m/%Y")
        }
        
        # Deduct balance immediately
        user["balance"] -= amount
        self.db.update_user(user_id, {"balance": user["balance"]})
        
        payment_id = self.db.add_payment(payment_data)
        
        # Notify admin
        admin_msg = f"""
🚨 নতুন উইথড্র রিকোয়েস্ট!
👤 ইউজার: {user_id}
💵 Amount: {Utils.format_currency(amount)}
📱 Method: {method}
📞 Number: {number}
🆔 Payment ID: {payment_id}

✅ /confirm_{payment_id} - কনফার্ম করুন
❌ /reject_{payment_id} - রিজেক্ট করুন
        """
        
        return {
            "success": True,
            "payment_id": payment_id,
            "message": "উইথড্র রিকোয়েস্ট করা হয়েছে! অ্যাডমিন শীঘ্রই প্রসেস করবেন।",
            "admin_notification": admin_msg
        }
    
    async def get_user_payments(self, user_id: int) -> str:
        """Get user's payment history"""
        payments = self.db.get_payments(user_id)
        
        if not payments:
            return "📭 কোনো পেমেন্ট হিস্টরি পাওয়া যায়নি!"
        
        history = "💳 **আপনার পেমেন্ট হিস্টরি:**\n\n"
        for payment in payments[:10]:  # Last 10 payments
            status_icon = "✅" if payment["status"] == "COMPLETED" else "⏳" if payment["status"] == "PENDING" else "❌"
            history += f"{status_icon} {payment['type']} - {Utils.format_currency(payment['amount'])} ({payment['method']})\n"
            history += f"   📅 {payment['time']} - {payment['status']}\n\n"
        
        return history