from flask import Flask, request
from telegram import Update
from telegram.ext import Application
import asyncio
import os

from bot import setup_handlers

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

telegram_app = Application.builder().token(BOT_TOKEN).build()

setup_handlers(telegram_app)

loop = asyncio.new_event_loop()


async def init_bot():
    await telegram_app.initialize()
    await telegram_app.start()


loop.run_until_complete(init_bot())


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
