

from flask import Flask, request
from telegram import Update
from telegram.ext import Application
import asyncio
import threading
import os

from bot import setup_handlers

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

telegram_app = Application.builder().token(BOT_TOKEN).build()

setup_handlers(telegram_app)

# Persistent asyncio loop
loop = asyncio.new_event_loop()

def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_loop, daemon=True).start()


# Initialize Telegram application once
async def init_bot():
    await telegram_app.initialize()

asyncio.run_coroutine_threadsafe(init_bot(), loop)


@app.route("/")
def home():
    return "🎲 Good Bingo Game is running"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)

        update = Update.de_json(
            data,
            telegram_app.bot
        )

        asyncio.run_coroutine_threadsafe(
            telegram_app.process_update(update),
            loop
        )

        return "OK", 200

    except Exception as e:
        print("Webhook error:", e)
        return "ERROR", 500
