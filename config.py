import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Essential credentials
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 0))
    BOT_USERNAME = os.getenv("BOT_USERNAME", "")
    OWNER_USERNAME = os.getenv("OWNER_USERNAME", "")
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
    NAGOD_NUMBER = os.getenv("NAGOD_NUMBER", "017XXXXXXXX")
    BIKASH_NUMBER = os.getenv("BIKASH_NUMBER", "017XXXXXXXX")
    
    # Bot info
    BOT_NAME = "🤖 MARPd Ultra Pro Max"
    VERSION = "v2.0 Final"
    CURRENCY = os.getenv("CURRENCY", "৳")
    
    # Settings
    WELCOME_BONUS = 100
    DAILY_BONUS = 50
    REFERRAL_BONUS = 200
    
    # Collections
    DB_COLLECTIONS = {
        'users': 'users_v2',
        'payments': 'manual_payments',
        'shop': 'shop_items',
        'games': 'games_stats',
        'groups': 'groups_data'
    }
    
    # Admin IDs
    ADMINS = [BOT_OWNER_ID]
    
    @staticmethod
    def validate():
        """Validate all required credentials"""
        missing = []
        
        if not Config.BOT_TOKEN or "your_bot_token" in Config.BOT_TOKEN:
            missing.append("BOT_TOKEN")
        
        if Config.BOT_OWNER_ID == 0:
            missing.append("BOT_OWNER_ID")
            
        if not Config.FIREBASE_API_KEY or "your_firebase" in Config.FIREBASE_API_KEY:
            missing.append("FIREBASE_API_KEY")
            
        if missing:
            print(f"\n❌ Missing or invalid credentials: {', '.join(missing)}")
            print("ℹ️ Please edit .env file with your credentials!")
            return False
            
        return True
    
    @staticmethod
    def show_banner():
        """Show beautiful banner"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        banner = f"""
\033[1;35m╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           🤖 MARPd ULTRA PRO MAX BOT 🤖                ║
║              Version: {Config.VERSION}                     ║
║                                                          ║
║         Owner: @{Config.OWNER_USERNAME}                        ║
║         Bot: @{Config.BOT_USERNAME}                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝\033[0m
        
\033[1;36m✅ Config Loaded Successfully!
💰 Currency: {Config.CURRENCY}
📱 Payment: Nagod({Config.NAGOD_NUMBER}), Bikash({Config.BIKASH_NUMBER})
\033[0m"""
        print(banner)