from flask import Flask, request, jsonify, render_template
from telegram import Update
from telegram.ext import Application
import asyncio
import os

from bot import setup_handlers
from database import init_db
from game import BingoGame


app = Flask(__name__)

# Initialize database
init_db()

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing")


# Telegram bot application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Setup bot commands
setup_handlers(telegram_app)


# Game engine
game = BingoGame()


# -------------------------
# Mini App Home Page
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# Mini App Join API
# -------------------------
@app.route("/api/join", methods=["POST"])
def join():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No data received"
        }), 400

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({
            "message": "User ID missing"
        }), 400


    # Add player to bingo game
    # Example:
    # game.add_player(user_id)

    return jsonify({
        "message": f"Player {user_id} joined Good Bingo Game 🎲"
    })


# -------------------------
# Telegram Webhook
# -------------------------
@app.route("/webhook", methods=["POST"])
def webhook():

    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        telegram_app.process_update(update)
    )

    loop.close()

    return "OK", 200


# -------------------------
# Health Check
# -------------------------
@app.route("/health")
def health():
    return jsonify({
        "status": "Good Bingo Game running"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

