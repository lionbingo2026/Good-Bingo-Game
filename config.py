import os

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8612978218"))

# Game Settings
GAME_NAME = "Good Bingo Game"
CARD_PRICE = 10
MAX_PLAYERS = 300
MAX_CARDS_PER_USER = 3

# Bingo Settings
BINGO_TYPE = "75 BALL"
FREE_CENTER = True
DRAW_INTERVAL = 5

# Wallet Settings
START_BALANCE = 0
REGISTRATION_BONUS = 10
CURRENCY = "ETB"

# Payment Limits
MIN_DEPOSIT = 50
MIN_WITHDRAW = 100

# Server
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 5000))

# Webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
