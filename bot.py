#!/usr/bin/env python3
"""
🤖 MARPd ULTRA PRO MAX BOT
Professional Telegram Bot for Termux
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Import custom modules
from config import Config
from db import Database
from utils import Utils
from payments import PaymentManager
from games import GamesManager
from shop import ShopManager
from admin import AdminManager
from security import SecurityManager

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
AMOUNT, METHOD, ACCOUNT, QUESTION, ANSWER = range(5)

class MARPdBot:
    def __init__(self):
        """Initialize the bot"""
        self.config = Config()
        
        # Validate config
        if not self.config.validate():
            sys.exit(1)
        
        # Show banner
        self.config.show_banner()
        
        # Initialize managers
        self.db = Database()
        self.payments = PaymentManager(self.db)
        self.games = GamesManager(self.db)
        self.shop = ShopManager(self.db)
        self.admin = AdminManager(self.db)
        self.security = SecurityManager(self.db)
        
        # User sessions
        self.user_sessions = {}
        
        print("\n✅ Bot initialized successfully!")
        print("⏳ Starting bot...\n")
    
    def setup_handlers(self, application: Application):
        """Setup all command handlers"""
        
        # Basic commands
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("profile", self.profile_command))
        
        # Economy commands
        application.add_handler(CommandHandler("balance", self.balance_command))
        application.add_handler(CommandHandler("deposit", self.deposit_command))
        application.add_handler(CommandHandler("withdraw", self.withdraw_command))
        application.add_handler(CommandHandler("payments", self.payments_command))
        
        # Game commands
        application.add_handler(CommandHandler("games", self.games_command))
        application.add_handler(CommandHandler("dice", self.dice_command))
        application.add_handler(CommandHandler("slot", self.slot_command))
        application.add_handler(CommandHandler("quiz", self.quiz_command))
        application.add_handler(CommandHandler("daily", self.daily_command))
        
        # Shop commands
        application.add_handler(CommandHandler("shop", self.shop_command))
        application.add_handler(CommandHandler("inventory", self.inventory_command))
        application.add_handler(CommandHandler("buy", self.buy_command))
        
        # Admin commands
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        application.add_handler(CommandHandler("userinfo", self.userinfo_command))
        application.add_handler(CommandHandler("backup", self.backup_command))
        
        # Message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        # Callback query handler
        application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Error handler
        application.add_error_handler(self.error_handler)
    
    # =============== COMMAND HANDLERS ===============
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Get or create user
        db_user = self.db.get_user(user_id)
        if not db_user:
            db_user = self.db.create_user(user_id, {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name or ""
            })
        
        welcome_text = f"""
🎉 **স্বাগতম {user.first_name}!** 🎉

🤖 **{self.config.BOT_NAME}** - সর্বশেষ ভার্সন {self.config.VERSION}

💰 **আপনার স্টার্টার বোনাস:**
• {Utils.format_currency(db_user.get('balance', 0))} ব্যালেন্স
• {Utils.format_coins(db_user.get('coins', 0))} কয়েন

🎮 **গেম খেলুন:** /games
🛍️ **শপ ব্রাউজ করুন:** /shop
💳 **ব্যালেন্স চেক:** /balance

📱 **পেমেন্ট মেথড:**
• নগদ: {self.config.NAGOD_NUMBER}
• বিকাশ: {self.config.BIKASH_NUMBER}

🔧 **সাহায্যের জন্য:** /help

**"সাফল্য চাইলে আগে বিশ্বাস করতে হবে!"**
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎮 গেমস", callback_data="games_menu"),
                InlineKeyboardButton("🛍️ শপ", callback_data="shop_menu")
            ],
            [
                InlineKeyboardButton("💰 ব্যালেন্স", callback_data="balance"),
                InlineKeyboardButton("📊 প্রোফাইল", callback_data="profile")
            ],
            [
                InlineKeyboardButton("ℹ️ সাহায্য", callback_data="help"),
                InlineKeyboardButton("⭐ ডেইলি বোনাস", callback_data="daily_bonus")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🆘 **সাহায্য - সকল কমান্ড**

🎯 **সাধারণ কমান্ড:**
/start - বট শুরু করুন
/help - সাহায্য দেখুন
/profile - আপনার প্রোফাইল
/settings - সেটিংস (শীঘ্রই)

💰 **ইকোনমি কমান্ড:**
/balance - ব্যালেন্স চেক
/deposit - ডিপোজিট করুন
/withdraw - উইথড্র করুন
/payments - পেমেন্ট হিস্টরি

🎮 **গেমস কমান্ড:**
/games - সকল গেম দেখুন
/dice [bet] - ডাইস গেম খেলুন
/slot [bet] - স্লট মেশিন
/quiz - কুইজ গেম
/daily - ডেইলি বোনাস নিন

🛍️ **শপ কমান্ড:**
/shop - শপ ব্রাউজ করুন
/inventory - আপনার ইনভেন্টরি
/buy [item_id] - আইটেম কিনুন

👑 **অ্যাডমিন কমান্ড:**
/admin - অ্যাডমিন প্যানেল
/stats - বট পরিসংখ্যান
/broadcast [msg] - ব্রডকাস্ট
/userinfo [id] - ইউজার তথ্য

📞 **সাপোর্ট:**
রিপোর্টের জন্য সরাসরি অ্যাডমিনকে কন্টাক্ট করুন: @{}
        """.format(self.config.OWNER_USERNAME)
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        user = update.effective_user
        user_id = user.id
        
        db_user = self.db.get_user(user_id)
        if not db_user:
            await update.message.reply_text("❌ আপনার প্রোফাইল খুঁজে পাওয়া যায়নি! /start লিখুন।")
            return
        
        level_info = Utils.calculate_level(db_user.get("xp", 0))
        
        profile_text = f"""
📋 **আপনার প্রোফাইল**

👤 **ব্যক্তিগত তথ্য:**
• আইডি: `{user_id}`
• নাম: {db_user.get('first_name', '')} {db_user.get('last_name', '')}
• ইউজারনেম: @{db_user.get('username', 'নেই')}
• জয়েন করেছেন: {db_user.get('joined', '')[:10]}

🏆 **স্ট্যাটাস:**
• লেভেল: {level_info['level']}
• XP: {level_info['xp']}/{level_info['xp_needed']}
• প্রোগ্রেস: {Utils.create_progress_bar(level_info['xp'], level_info['xp_needed'])}
• সতর্কতা: {db_user.get('warnings', 0)}/3

💰 **ইকোনমি:**
• ব্যালেন্স: {Utils.format_currency(db_user.get('balance', 0))}
• কয়েন: {Utils.format_coins(db_user.get('coins', 0))}
• ডেইলি স্ট্রীক: {db_user.get('daily_streak', 0)} দিন

📊 **অ্যাকটিভিটি:**
• মোট মেসেজ: {db_user.get('total_messages', 0)}
• শেষ দেখা: {db_user.get('last_seen', '')[:16]}
• ইনভেন্টরি: {len(db_user.get('inventory', []))} আইটেম

🎯 **উদ্ধৃতি:** {Utils.get_random_quote()}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="refresh_profile"),
                InlineKeyboardButton("💰 ব্যালেন্স", callback_data="balance")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            profile_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        user_id = update.effective_user.id
        
        db_user = self.db.get_user(user_id)
        if not db_user:
            await update.message.reply_text("❌ আপনার একাউন্ট খুঁজে পাওয়া যায়নি! /start লিখুন।")
            return
        
        balance_text = f"""
💰 **আপনার ব্যালেন্স**

💵 **নগদ ব্যালেন্স:**
{Utils.format_currency(db_user.get('balance', 0))}

🪙 **কয়েন ব্যালেন্স:**
{Utils.format_coins(db_user.get('coins', 0))}

📈 **সামগ্রিক অবস্থা:**
• লেভেল: {Utils.calculate_level(db_user.get('xp', 0))['level']}
• মোট উপার্জন: {Utils.format_currency(db_user.get('total_earned', 0))}

💳 **পেমেন্ট অপশন:**
• ডিপোজিট: /deposit
• উইথড্র: /withdraw
• হিস্টরি: /payments

📱 **পেমেন্ট নম্বর:**
• নগদ: {self.config.NAGOD_NUMBER}
• বিকাশ: {self.config.BIKASH_NUMBER}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💵 ডিপোজিট", callback_data="deposit"),
                InlineKeyboardButton("🏧 উইথড্র", callback_data="withdraw")
            ],
            [
                InlineKeyboardButton("📜 হিস্টরি", callback_data="payment_history"),
                InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="refresh_balance")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            balance_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def deposit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /deposit command"""
        if context.args:
            # Quick deposit
            amount_str = context.args[0]
            validation = self.security.validate_amount(amount_str)
            
            if not validation["valid"]:
                await update.message.reply_text(f"❌ {validation['error']}")
                return
            
            amount = validation["amount"]
            
            keyboard = [
                [
                    InlineKeyboardButton("নগদ", callback_data=f"deposit_nagod_{amount}"),
                    InlineKeyboardButton("বিকাশ", callback_data=f"deposit_bikash_{amount}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"💰 {Utils.format_currency(amount)} ডিপোজিট করতে পেমেন্ট মেথড সিলেক্ট করুন:",
                reply_markup=reply_markup
            )
        else:
            # Show deposit instructions
            deposit_text = f"""
💳 **ডিপোজিট করুন**

📱 **পেমেন্ট নম্বর:**
• নগদ: `{self.config.NAGOD_NUMBER}`
• বিকাশ: `{self.config.BIKASH_NUMBER}`

📝 **ডিপোজিট করার নিয়ম:**
1. উপরের নম্বরে টাকা সেন্ড করুন
2. ট্রান্সফারের পর স্ক্রিনশট বা TrxID সেভ করুন
3. এই ফরম্যাটে মেসেজ দিন:
   `/deposit [amount] [method] [trxid]`
   
   **উদাহরণ:**
   `/deposit 100 নগদ TRX123456`

💡 **দ্রষ্টব্য:**
• ন্যূনতম ডিপোজিট: ৳10
• অটোমেটিক ভেরিফিকেশন (শীঘ্রই)
• কোনো সমস্যা হলে @{self.config.OWNER_USERNAME} কে কন্টাক্ট করুন

⚡ **কুইক ডিপোজিট:**
`/deposit 100`
            """
            
            await update.message.reply_text(deposit_text, parse_mode='Markdown')
    
    async def withdraw_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /withdraw command"""
        user_id = update.effective_user.id
        
        if context.args and len(context.args) >= 2:
            # Quick withdraw
            amount_str = context.args[0]
            method = context.args[1]
            number = context.args[2] if len(context.args) > 2 else ""
            
            validation = self.security.validate_amount(amount_str, 10000)
            if not validation["valid"]:
                await update.message.reply_text(f"❌ {validation['error']}")
                return
            
            if method not in ["নগদ", "বিকাশ"]:
                await update.message.reply_text("❌ সাপোর্টেড মেথড: নগদ, বিকাশ")
                return
            
            if not number or not Utils.validate_phone(number):
                await update.message.reply_text("❌ সঠিক মোবাইল নম্বর দিন (11 ডিজিট)")
                return
            
            amount = validation["amount"]
            
            result = await self.payments.request_withdraw(user_id, amount, method, number)
            
            if result["success"]:
                await update.message.reply_text(
                    f"✅ {result['message']}\n\n📋 **বিস্তারিত:**\n"
                    f"• Amount: {Utils.format_currency(amount)}\n"
                    f"• Method: {method}\n"
                    f"• Number: {number}\n"
                    f"• ID: {result['payment_id']}\n\n"
                    f"অ্যাডমিন শীঘ্রই প্রসেস করবেন।"
                )
            else:
                await update.message.reply_text(f"❌ {result['message']}")
        else:
            # Show withdraw instructions
            user = self.db.get_user(user_id)
            if not user:
                await update.message.reply_text("❌ আপনার একাউন্ট খুঁজে পাওয়া যায়নি!")
                return
            
            withdraw_text = f"""
🏧 **উইথড্র করুন**

💰 **আপনার ব্যালেন্স:** {Utils.format_currency(user.get('balance', 0))}

📝 **উইথড্র করার নিয়ম:**
1. নিচের ফরম্যাটে মেসেজ দিন:
   `/withdraw [amount] [method] [number]`
   
   **উদাহরণ:**
   `/withdraw 500 নগদ 01712345678`

2. অ্যাডমিন ভেরিফাই করবেন
3. ২৪ ঘন্টার মধ্যে টাকা পেয়ে যাবেন

💡 **শর্তাবলী:**
• ন্যূনতম উইথড্র: ৳50
• সর্বোচ্চ উইথড্র: ৳10,000 (প্রতিদিন)
• প্রসেসিং টাইম: ২৪ ঘন্টা
• কোনো চার্জ নেই

⚡ **কুইক উইথড্র:**
`/withdraw 500 নগদ 017XXXXXXXX`
            """
            
            await update.message.reply_text(withdraw_text, parse_mode='Markdown')
    
    async def payments_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /payments command"""
        user_id = update.effective_user.id
        
        history = await self.payments.get_user_payments(user_id)
        await update.message.reply_text(history, parse_mode='Markdown')
    
    async def games_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /games command"""
        games_text = """
🎮 **গেমস জোন**

🎲 **ডাইস গেম:**
• বেট করে ডাইস রোল করুন
• বটের চেয়ে বেশি পেলে জিতবেন
• কমান্ড: `/dice [bet]`
• ন্যূনতম বেট: 10 কয়েন

🎰 **স্লট মেশিন:**
• ৩টি মিললে জ্যাকপট!
• কমান্ড: `/slot [bet]`
• ন্যূনতম বেট: 20 কয়েন

🧠 **কুইজ গেম:**
• জ্ঞান পরীক্ষা করুন
• সঠিক উত্তরে 50 কয়েন
• কমান্ড: `/quiz`

🎁 **ডেইলি বোনাস:**
• প্রতিদিন ফ্রি কয়েন
• স্ট্রীক বাড়লে বোনাস বাড়ে
• কমান্ড: `/daily`

🏆 **লিডারবোর্ড:**
• শীর্ষ খেলোয়াড়দের দেখুন
• সাপ্তাহিক পুরস্কার

⚡ **টিপস:**
• ছোট বেট দিয়ে শুরু করুন
• ডেইলি বোনাস নিতে ভুলবেন না
• লাকি হলে বিশাল জিততে পারেন!
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎲 ডাইস (10)", callback_data="game_dice_10"),
                InlineKeyboardButton("🎰 স্লট (20)", callback_data="game_slot_20")
            ],
            [
                InlineKeyboardButton("🧠 কুইজ", callback_data="game_quiz"),
                InlineKeyboardButton("🎁 ডেইলি", callback_data="daily_bonus")
            ],
            [
                InlineKeyboardButton("🏆 লিডারবোর্ড", callback_data="leaderboard"),
                InlineKeyboardButton("📊 স্ট্যাটস", callback_data="game_stats")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            games_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def dice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /dice command"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text("❌ ব্যবহার: `/dice [bet]`\nউদাহরণ: `/dice 50`")
            return
        
        bet_str = context.args[0]
        if not bet_str.isdigit():
            await update.message.reply_text("❌ সঠিক সংখ্যা দিন!")
            return
        
        bet = int(bet_str)
        
        result = await self.games.play_dice(user_id, bet)
        
        if result["success"]:
            # Create dice visual
            dice_faces = {
                1: "⚀",
                2: "⚁", 
                3: "⚂",
                4: "⚃",
                5: "⚄",
                6: "⚅"
            }
            
            user_dice = dice_faces.get(result["user_roll"], "🎲")
            bot_dice = dice_faces.get(result["bot_roll"], "🎲")
            
            result_text = f"""
🎲 **ডাইস গেম রেজাল্ট**

{user_dice} **আপনার ডাইস:** {result["user_roll"]}
{bot_dice} **বটের ডাইস:** {result["bot_roll"]}

📊 **রেজাল্ট:** {result["message"].split('\n')[-1]}

💰 **বর্তমান কয়েন:** {Utils.format_coins(result["coins"])}
            """
            
            await update.message.reply_text(result_text)
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    async def slot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /slot command"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text("❌ ব্যবহার: `/slot [bet]`\nউদাহরণ: `/slot 100`")
            return
        
        bet_str = context.args[0]
        if not bet_str.isdigit():
            await update.message.reply_text("❌ সঠিক সংখ্যা দিন!")
            return
        
        bet = int(bet_str)
        
        result = await self.games.play_slot(user_id, bet)
        
        if result["success"]:
            slots_display = " | ".join(result["slots"])
            
            result_text = f"""
🎰 **স্লট মেশিন**

[{slots_display}]

📊 **রেজাল্ট:** {result["message"].split('\n')[-1]}

💰 **বর্তমান কয়েন:** {Utils.format_coins(result["coins"])}
            """
            
            await update.message.reply_text(result_text)
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    async def quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quiz command"""
        user_id = update.effective_user.id
        
        # Store current question for user
        result = await self.games.play_quiz(user_id)
        
        if result["success"]:
            self.user_sessions[user_id] = {
                "quiz_question": result,
                "timestamp": datetime.now()
            }
            
            options_text = "\n".join([
                f"{i+1}. {option}" 
                for i, option in enumerate(result["options"])
            ])
            
            quiz_text = f"""
🧠 **কুইজ গেম**

❓ **প্রশ্ন:** {result["question"]}

{options_text}

💰 **পুরস্কার:** {Utils.format_coins(result["reward"])}

📝 **উত্তর দিন:** 1, 2, 3 বা 4 লিখুন
⏱️ **টাইম লিমিট:** 60 সেকেন্ড
            """
            
            await update.message.reply_text(quiz_text)
        else:
            await update.message.reply_text("❌ কুইজ লোড করতে সমস্যা হয়েছে!")
    
    async def daily_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /daily command"""
        user_id = update.effective_user.id
        
        result = await self.games.daily_bonus(user_id)
        
        if result["success"]:
            await update.message.reply_text(
                f"🎁 **ডেইলি বোনাস!**\n\n"
                f"{result['message']}\n\n"
                f"💰 **মোট কয়েন:** {Utils.format_coins(result['coins'])}\n"
                f"🔥 **স্ট্রীক:** {result['streak']} দিন\n\n"
                f"আগামীকাল আবার আসুন!"
            )
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    async def shop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /shop command"""
        items = self.shop.get_shop_items()
        
        if not items:
            await update.message.reply_text("❌ শপে এখন কোনো আইটেম নেই!")
            return
        
        shop_text = "🛍️ **শপ - সকল আইটেম**\n\n"
        
        keyboard = []
        row = []
        
        for i, item in enumerate(items):
            shop_text += f"{item.get('icon', '📦')} **{item['name']}**\n"
            shop_text += f"   💰 দাম: {Utils.format_coins(item['price'])}\n"
            shop_text += f"   📝 {item.get('description', '')}\n"
            shop_text += f"   🆔 ID: `{item['id']}`\n\n"
            
            # Add buy button
            row.append(InlineKeyboardButton(
                f"{item.get('icon', '📦')} {item['price']}",
                callback_data=f"buy_{item['id']}"
            ))
            
            if len(row) == 2 or i == len(items) - 1:
                keyboard.append(row)
                row = []
        
        # Add navigation buttons
        keyboard.append([
            InlineKeyboardButton("📦 ইনভেন্টরি", callback_data="inventory"),
            InlineKeyboardButton("🔄 রিফ্রেশ", callback_data="refresh_shop")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            shop_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def inventory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /inventory command"""
        user_id = update.effective_user.id
        
        inventory_text = await self.shop.get_user_inventory(user_id)
        await update.message.reply_text(inventory_text, parse_mode='Markdown')
    
    async def buy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /buy command"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text("❌ ব্যবহার: `/buy [item_id]`\nউদাহরণ: `/buy vip_badge`")
            return
        
        item_id = context.args[0]
        
        result = await self.shop.buy_item(user_id, item_id)
        
        if result["success"]:
            await update.message.reply_text(
                f"✅ **ক্রয় সফল!**\n\n"
                f"{result['message']}\n"
                f"💰 **বাকি কয়েন:** {Utils.format_coins(result['coins'])}\n\n"
                f"📦 আইটেমটি আপনার ইনভেন্টরিতে যোগ হয়েছে!\n"
                f"ইনভেন্টরি দেখতে: /inventory"
            )
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        if not self.admin.is_admin(user_id):
            await update.message.reply_text("❌ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য!")
            return
        
        admin_text = f"""
👑 **অ্যাডমিন প্যানেল**

👤 **অ্যাডমিন:** @{update.effective_user.username}
🤖 **বট:** @{self.config.BOT_USERNAME}

📊 **কুইক স্ট্যাটস:**
• মোট ইউজার: {len(self.db.users):,}
• অ্যাকটিভ পেমেন্ট: {sum(1 for p in self.db.payments.values() if p.get('status') == 'PENDING')}
• টোটাল কয়েন: {Utils.format_coins(sum(u.get('coins', 0) for u in self.db.users.values()))}

🛠️ **অ্যাডমিন টুলস:**
• /stats - বিস্তারিত পরিসংখ্যান
• /broadcast [msg] - ব্রডকাস্ট বার্তা
• /userinfo [id] - ইউজার তথ্য
• /backup - ডাটাবেস ব্যাকআপ

👤 **ইউজার ম্যানেজমেন্ট:**
• `/warn [id] [reason]` - সতর্কতা দিন
• `/ban [id] [reason]` - ইউজার ব্যান করুন
• `/unban [id]` - ইউজার আনব্যান করুন
• `/addcoins [id] [amount]` - কয়েন যোগ করুন

💳 **পেমেন্ট ম্যানেজমেন্ট:**
• পেমেন্ট আইডি দিয়ে কনফার্ম/রিজেক্ট
• ম্যানুয়াল চেকের জন্য স্ক্রিনশট

⚙️ **সিস্টেম:**
• লগস চেক করুন
• পারফরম্যান্স মনিটর করুন
• ব্যাকআপ নিয়মিত নিন
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 স্ট্যাটস", callback_data="admin_stats"),
                InlineKeyboardButton("📢 ব্রডকাস্ট", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton("💾 ব্যাকআপ", callback_data="admin_backup"),
                InlineKeyboardButton("👥 ইউজার", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("💳 পেমেন্ট", callback_data="admin_payments"),
                InlineKeyboardButton("🚨 লগস", callback_data="admin_logs")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            admin_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        
        if not self.admin.is_admin(user_id):
            await update.message.reply_text("❌ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য!")
            return
        
        stats_text = await self.admin.get_bot_stats()
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command"""
        user_id = update.effective_user.id
        
        if not self.admin.is_admin(user_id):
            await update.message.reply_text("❌ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ ব্যবহার: `/broadcast [message]`")
            return
        
        message = " ".join(context.args)
        
        result = await self.admin.broadcast_message(user_id, message)
        
        if result["success"]:
            await update.message.reply_text(f"✅ {result['message']}")
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    async def userinfo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /userinfo command"""
        user_id = update.effective_user.id
        
        if not self.admin.is_admin(user_id):
            await update.message.reply_text("❌ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য!")
            return
        
        if not context.args:
            target_id = user_id
        else:
            try:
                target_id = int(context.args[0])
            except ValueError:
                await update.message.reply_text("❌ সঠিক ইউজার আইডি দিন!")
                return
        
        user_info = await self.admin.get_user_info(target_id)
        await update.message.reply_text(user_info, parse_mode='Markdown')
    
    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /backup command"""
        user_id = update.effective_user.id
        
        if not self.admin.is_admin(user_id):
            await update.message.reply_text("❌ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য!")
            return
        
        result = await self.admin.create_backup(user_id)
        
        if result["success"]:
            await update.message.reply_text(f"✅ {result['message']}")
        else:
            await update.message.reply_text(f"❌ {result['message']}")
    
    # =============== MESSAGE HANDLER ===============
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all text messages"""
        user = update.effective_user
        user_id = user.id
        message = update.message.text
        
        # Security check
        security_check = self.security.check_message(user_id, message)
        if not security_check["safe"]:
            if security_check["action"] == "warn":
                await update.message.reply_text(
                    f"⚠️ সতর্কতা! নিষিদ্ধ কন্টেন্ট: {', '.join(security_check['violations'])}\n"
                    f"আরও সতর্কতা পেলে ব্যান হতে পারেন!"
                )
            return
        
        # Update user message count
        db_user = self.db.get_user(user_id)
        if db_user:
            self.db.update_user(user_id, {
                "total_messages": db_user.get("total_messages", 0) + 1
            })
        
        # Check for quiz answer
        if user_id in self.user_sessions and "quiz_question" in self.user_sessions[user_id]:
            if message in ["1", "2", "3", "4"]:
                answer_idx = int(message) - 1
                question_data = self.user_sessions[user_id]["quiz_question"]
                
                result = await self.games.check_quiz_answer(
                    user_id, 
                    question_data.get("question_index", 0),
                    answer_idx
                )
                
                if result["success"]:
                    await update.message.reply_text(
                        f"🧠 **কুইজ রেজাল্ট**\n\n"
                        f"{result['message']}\n"
                        f"💰 **মোট কয়েন:** {Utils.format_coins(result['coins'])}"
                    )
                else:
                    await update.message.reply_text(f"❌ {result['message']}")
                
                # Clear session
                del self.user_sessions[user_id]
                return
        
        # Check for payment confirmation
        if message.startswith("trx") or message.startswith("TRX"):
            # This could be a payment transaction ID
            await update.message.reply_text(
                "📱 **পেমেন্ট রিসিভ করা হয়েছে!**\n\n"
                "অ্যাডমিন শীঘ্রই আপনার পেমেন্ট চেক করবেন।\n"
                "কনফার্মেশন পেলে নোটিফিকেশন পাবেন।\n\n"
                "ধন্যবাদ!"
            )
    
    # =============== BUTTON HANDLER ===============
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        data = query.data
        
        # Handle different button actions
        if data == "games_menu":
            await self.games_command(update, context)
        
        elif data == "shop_menu":
            await self.shop_command(update, context)
        
        elif data == "balance":
            await self.balance_command(update, context)
        
        elif data == "profile":
            await self.profile_command(update, context)
        
        elif data == "help":
            await self.help_command(update, context)
        
        elif data == "daily_bonus":
            await self.daily_command(update, context)
        
        elif data.startswith("game_dice_"):
            bet = int(data.split("_")[-1])
            result = await self.games.play_dice(user_id, bet)
            
            if result["success"]:
                await query.edit_message_text(
                    f"🎲 **ডাইস গেম**\n\n"
                    f"আপনার ডাইস: {result['user_roll']}\n"
                    f"বটের ডাইস: {result['bot_roll']}\n\n"
                    f"**রেজাল্ট:** {result['message'].split('!')[0]}!\n\n"
                    f"💰 কয়েন: {Utils.format_coins(result['coins'])}"
                )
            else:
                await query.edit_message_text(f"❌ {result['message']}")
        
        elif data.startswith("game_slot_"):
            bet = int(data.split("_")[-1])
            result = await self.games.play_slot(user_id, bet)
            
            if result["success"]:
                slots_display = " | ".join(result["slots"])
                await query.edit_message_text(
                    f"🎰 **স্লট মেশিন**\n\n"
                    f"[{slots_display}]\n\n"
                    f"**রেজাল্ট:** {result['message'].split('\n')[-1]}\n\n"
                    f"💰 কয়েন: {Utils.format_coins(result['coins'])}"
                )
            else:
                await query.edit_message_text(f"❌ {result['message']}")
        
        elif data == "game_quiz":
            await self.quiz_command(update, context)
        
        elif data.startswith("buy_"):
            item_id = data[4:]
            result = await self.shop.buy_item(user_id, item_id)
            
            if result["success"]:
                await query.edit_message_text(
                    f"✅ **ক্রয় সফল!**\n\n"
                    f"{result['message']}\n"
                    f"💰 বাকি কয়েন: {Utils.format_coins(result['coins'])}\n\n"
                    f"📦 আইটেমটি আপনার ইনভেন্টরিতে যোগ হয়েছে!"
                )
            else:
                await query.edit_message_text(f"❌ {result['message']}")
        
        elif data == "inventory":
            await self.inventory_command(update, context)
        
        elif data.startswith("deposit_"):
            # Handle deposit buttons
            parts = data.split("_")
            if len(parts) >= 3:
                method = parts[1]
                amount = float(parts[2])
                
                instructions = f"""
💰 **{method.upper()} ডিপোজিট**

📱 নম্বর: {
                    self.config.NAGOD_NUMBER if method == 'nagod' 
                    else self.config.BIKASH_NUMBER
                }

💵 Amount: {Utils.format_currency(amount)}
📌 Reference: MARPd-{datetime.now().strftime('%H%M')}

✅ পেমেন্টের পর স্ক্রিনশট/TrxID পাঠান।
⏳ অ্যাডমিন শীঘ্রই কনফার্ম করবেন।
                """
                
                await query.edit_message_text(
                    instructions,
                    parse_mode='Markdown'
                )
        
        elif data.startswith("admin_"):
            # Admin button actions
            if not self.admin.is_admin(user_id):
                await query.edit_message_text("❌ অনুমতি নেই!")
                return
            
            action = data[6:]
            
            if action == "stats":
                await self.stats_command(update, context)
            elif action == "backup":
                result = await self.admin.create_backup(user_id)
                await query.edit_message_text(f"📊 {result['message']}")
            else:
                await query.edit_message_text(f"⚙️ {action} ফিচার শীঘ্রই আসছে!")
    
    # =============== ERROR HANDLER ===============
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Error: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ কিছু সমস্যা হয়েছে! দয়া করে আবার চেষ্টা করুন।"
            )
    
    # =============== RUN BOT ===============
    
    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Setup handlers
        self.setup_handlers(application)
        
        # Start the bot
        print(f"🤖 Bot starting as @{self.config.BOT_USERNAME}")
        print(f"👑 Owner: @{self.config.OWNER_USERNAME}")
        print(f"💰 Payment: Nagod({self.config.NAGOD_NUMBER}), Bikash({self.config.BIKASH_NUMBER})")
        print("\n" + "="*50)
        print("✅ Bot is running! Press Ctrl+C to stop.")
        print("="*50 + "\n")
        
        # Run bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

# =============== MAIN ENTRY POINT ===============

if __name__ == "__main__":
    # Check if running in Termux
    is_termux = "com.termux" in os.environ.get("PREFIX", "")
    
    if is_termux:
        print("📱 Termux environment detected!")
    
    try:
        # Create and run bot
        bot = MARPdBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)