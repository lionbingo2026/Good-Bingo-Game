from flask import Flask, request
from telegram import Update
from telegram.ext import Application
import os
import asyncio

from bot import setup_handlers

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

telegram_app = Application.builder().token(BOT_TOKEN).build()

setup_handlers(telegram_app)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

loop.run_until_complete(telegram_app.initialize())

loop.run_until_complete(
    telegram_app.bot.set_webhook(WEBHOOK_URL)
)


@app.route("/")
def home():
    return "🎲 Good Bingo Game is running"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )

    loop.run_until_complete(
        telegram_app.process_update(update)
    )

    return "OK"


@app.route("/health")
def health():
    return "OK"
