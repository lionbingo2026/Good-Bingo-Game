from flask import Flask, request, jsonify, render_template
from telegram import Update
from telegram.ext import Application
import asyncio
import os
import threading

from bot import setup_handlers
from database import init_db
from game import BingoGame


app = Flask(__name__)


# Database
init_db()


BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing")


# Game engine
game = BingoGame()


# Telegram application
telegram_app = Application.builder().token(BOT_TOKEN).build()

setup_handlers(telegram_app)


# Async loop
loop = asyncio.new_event_loop()


def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()


threading.Thread(
    target=start_loop,
    daemon=True
).start()


async def init_bot():
    await telegram_app.initialize()
    await telegram_app.start()


asyncio.run_coroutine_threadsafe(
    init_bot(),
    loop
)


# Mini App page
@app.route("/")
def home():
    return render_template("index.html")


# Game status API
@app.route("/api/game")
def game_status():
    return jsonify(game.get_status())


# Join Bingo API
@app.route("/api/join", methods=["POST"])
def join_bingo():
    data = request.get_json()

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "User ID missing"
        }), 400

    result = game.add_player(user_id)

    return jsonify({
        "success": True,
        "message": "Joined Bingo!",
        "data": result
    })


# Telegram webhook
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
        print("Webhook error:", repr(e))
        return "ERROR", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )



