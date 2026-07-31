from flask import Flask, request
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import BOT_TOKEN, GAME_NAME
from database import create_user, get_user
from cards import generate_card, card_to_text


app = Flask(__name__)


# Telegram Application
telegram_app = Application.builder().token(
    BOT_TOKEN
).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    new_user = create_user(
        user.id,
        user.username
    )

    bonus = ""

    if new_user:
        bonus = "\n🎁 Bonus: 10 ETB"

    await update.message.reply_text(
        f"🎲 {GAME_NAME}\n"
        f"Welcome {user.first_name}"
        f"{bonus}\n\n"
        "/play - Get Bingo Card\n"
        "/balance - Check Balance"
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):

    card = generate_card()

    await update.message.reply_text(
        card_to_text(card)
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = get_user(update.effective_user.id)

    if user:
        await update.message.reply_text(
            f"💰 Balance: {user[3]} ETB"
        )
    else:
        await update.message.reply_text(
            "Use /start first"
        )


telegram_app.add_handler(
    CommandHandler("start", start)
)

telegram_app.add_handler(
    CommandHandler("play", play)
)

telegram_app.add_handler(
    CommandHandler("balance", balance)
)


@app.route("/")
def home():
    return "🎲 Good Bingo Game Server Running"


@app.route("/webhook", methods=["POST"])
async def webhook():

    data = request.get_json()

    update = Update.de_json(
        data,
        telegram_app.bot
    )

    await telegram_app.process_update(update)

    return "OK"


if __name__ == "__main__":

    port = int(
        os.getenv("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
