#!/bin/bash
clear

echo -e "\e[1;35m"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                🤖 MARPd ULTRA PRO MAX BOT 🤖             ║"
echo "║                Professional Telegram Bot                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "\e[0m"

echo -e "\e[1;36m[*] Starting bot...\e[0m"
echo -e "\e[1;33m[*] Date: $(date)\e[0m"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "\e[1;31m[!] Python3 not found! Installing...\e[0m"
    pkg install python -y
fi

# Check requirements
if [ ! -f "requirements.txt" ]; then
    echo -e "\e[1;31m[!] requirements.txt not found!\e[0m"
    exit 1
fi

# Install requirements if needed
echo -e "\e[1;36m[*] Checking dependencies...\e[0m"
pip3 install -r requirements.txt --quiet

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "\e[1;33m[!] .env file not found! Creating template...\e[0m"
    cat > .env << EOL
# === ENTER YOUR CREDENTIALS BELOW ===
BOT_TOKEN=your_bot_token_here
BOT_OWNER_ID=123456789
BOT_USERNAME=your_bot_username
OWNER_USERNAME=your_username
FIREBASE_API_KEY=your_firebase_key_here
NAGOD_NUMBER=017XXXXXXXX
BIKASH_NUMBER=017XXXXXXXX
# === END ===
EOL
    echo -e "\e[1;33m[!] Please edit .env file with your credentials!\e[0m"
    exit 1
fi

# Check if credentials are set
if grep -q "your_bot_token_here" .env; then
    echo -e "\e[1;31m[!] Please update .env file with your credentials!\e[0m"
    exit 1
fi

# Run bot
echo -e "\e[1;32m[✓] Starting MARPd Bot...\e[0m"
echo -e "\e[1;35m══════════════════════════════════════════════════════════\e[0m"
python3 bot.py