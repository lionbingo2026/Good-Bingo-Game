from flask import Flask, request
from telegram import Update
from telegram.ext import Application
import os
import asyncio

from bot import setup_handlers

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

telegram_app = Application.builder().token(BOT_TOKEN).build()

setup_handlers(telegram_app)

initialized = False


async def init_telegram():
    global initialized
    if not initialized:
        await telegram_app.initialize()
        initialized = True


@app.route("/")
def home():
    return "🎲 Good Bingo Game is running"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(
            request.get_json(force=True),
            telegram_app.bot
        )

        async def process():
            await init_telegram()
            await telegram_app.process_update(update)

        asyncio.run(process())

        return "OK", 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return "OK", 200
