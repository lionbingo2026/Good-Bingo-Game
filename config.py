import os

# ==========================================
# Telegram Bot
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(
    os.getenv("ADMIN_ID", "8612978218")
)

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN environment variable is missing"
    )


# ==========================================
# Good Bingo Game
# ==========================================

GAME_NAME = "Good Bingo Game"

CARD_PRICE = 10

MAX_PLAYERS = 300

MAX_CARDS_PER_USER = 3


# ==========================================
# Bingo Settings
# ==========================================

BINGO_TYPE = "75 BALL"

BINGO_SIZE = 5

FREE_CENTER = True

AUTO_DRAW = True

DRAW_INTERVAL = 5

MIN_PLAYERS_TO_START = 2

MAX_WINNERS = 1


# ==========================================
# Prize Settings
# ==========================================

WIN_PERCENTAGE = 80

PLATFORM_FEE = 20


# ==========================================
# Wallet Settings
# ==========================================

START_BALANCE = 0

REGISTRATION_BONUS = 20

CURRENCY = "ETB"


# ==========================================
# Payment Limits
# ==========================================

MIN_DEPOSIT = 50

MIN_WITHDRAW = 100
MIN_REMAINING_BALANCE = 50


# ==========================================
# Server
# ==========================================

HOST = "0.0.0.0"

PORT = int(
    os.getenv("PORT", "10000")
)


# ==========================================
# Telegram Webhook
# ==========================================

WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://good-bingo-game-r0pe.onrender.com/webhook"
)


# ==========================================
# Telegram Mini App
# ==========================================

MINI_APP_URL = os.getenv(
    "MINI_APP_URL",
    "https://good-bingo-game-r0pe.onrender.com/"
)


# ==========================================
# Database
# ==========================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///bingo.db"
)
