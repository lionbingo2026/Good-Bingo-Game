from flask import Flask, request, jsonify, render_template
from telegram import Update
from telegram.ext import Application
import asyncio
import os
import threading
import time

from bot import setup_handlers, setup_mini_app_menu
from database import init_db
from shared import game


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# DATABASE
# ============================================================

init_db()


# ============================================================
# TELEGRAM BOT
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN environment variable is missing"
    )


telegram_app = (
    Application
    .builder()
    .token(BOT_TOKEN)
    .build()
)


# Register Telegram handlers
setup_handlers(telegram_app)


# ============================================================
# TELEGRAM EVENT LOOP
# ============================================================

telegram_loop = asyncio.new_event_loop()
asyncio.set_event_loop(telegram_loop)


# ============================================================
# TELEGRAM INITIALIZATION
# ============================================================

def ensure_telegram_initialized():
    """
    Make sure the Telegram Application is initialized
    before processing webhook updates.
    """

    if not getattr(telegram_app, "_initialized", False):

        print(
            "Initializing Telegram Application..."
        )

        telegram_loop.run_until_complete(
            telegram_app.initialize()
        )

        telegram_loop.run_until_complete(
            setup_mini_app_menu(telegram_app)
        )

        print(
            "Telegram Application initialized."
        )


# Initialize when Gunicorn worker loads.
ensure_telegram_initialized()


# ============================================================
# BINGO GAME
# ============================================================



# ============================================================
# BINGO SETTINGS
# ============================================================

MIN_PLAYERS_TO_START = 2
DRAW_INTERVAL = 5


# ============================================================
# AUTOMATIC BINGO CALLER
# ============================================================

def bingo_caller():

    print("🎱 Bingo caller started.")

    while True:

        try:

            if game.running:

                number = game.draw_number()

                if number is not None:

                    print(
                        f"🎱 Live Bingo Number: {number}"
                    )

            time.sleep(DRAW_INTERVAL)

        except Exception as e:

            print(
                "Bingo caller error:",
                repr(e)
            )

            time.sleep(DRAW_INTERVAL)


bingo_thread = threading.Thread(
    target=bingo_caller,
    daemon=True
)

bingo_thread.start()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "ok": True,

        "status":
            "Good Bingo Game running"

    })


# ============================================================
# JOIN GAME
# ============================================================

@app.route(
    "/api/join",
    methods=["POST"]
)
def join():

    data = request.get_json(
        silent=True
    ) or {}

    user_id = (
        data.get("telegram_id")
        or data.get("user_id")
    )

    username = data.get(
        "username",
        ""
    )

    first_name = data.get(
        "first_name",
        "Player"
    )

    card_number = data.get("card_number")

    if not user_id:

        return jsonify({

            "success": False,

            "message":
                "Telegram user ID missing"

        }), 400


    try:

        result = game.add_player(
            user_id,
            card_number=card_number
        )

        if not result.get("success"):

            return jsonify(result), 400


        # ----------------------------------------------------
        # Start game automatically when enough players join
        # ----------------------------------------------------

        if (
            len(game.players)
            >= MIN_PLAYERS_TO_START
            and not game.running
        ):

            game.start_game()

            print(
                f"🎮 Game started with "
                f"{len(game.players)} players."
            )


        return jsonify({

            "success": True,

            "message": (
                f"Welcome {first_name}! "
                "You joined Good Bingo Game"
            ),

            "user_id": user_id,

            "username": username,

            "players":
                len(game.players),

            "card_number":
                result.get("card_number"),

            "card":
                result.get("card"),

            "running":
                game.running

        })


    except Exception as e:

        print(
            "Join error:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to join the game"

        }), 500


# ============================================================
# AVAILABLE BINGO CARDS
# ============================================================

@app.route(
    "/api/cards",
    methods=["GET"]
)
def available_cards():

    try:

        return jsonify({
            "success": True,
            "cards": game.get_available_card_numbers()
        })

    except Exception as e:

        print(
            "Available cards error:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "cards": []
        }), 500


# ============================================================
# GAME STATUS
# ============================================================

@app.route(
    "/api/game",
    methods=["GET"]
)
def game_status():

    try:

        status = game.get_status()

        players = status.get(
            "players",
            0
        )

        cards = status.get(
            "cards",
            0
        )

        called_numbers = status.get(
            "called_numbers",
            []
        )

        current_number = status.get(
            "last_number"
        )

        running = status.get(
            "running",
            False
        )

        winner = status.get(
            "winner"
        )


        # ----------------------------------------------------
        # Status text
        # ----------------------------------------------------

        if winner is not None:

            game_status_text = (
                f"🏆 Winner: {winner}"
            )

        elif running:

            game_status_text = (
                "🔴 LIVE - Number drawing"
            )

        elif players == 0:

            game_status_text = (
                "Waiting for players..."
            )

        elif players < MIN_PLAYERS_TO_START:

            game_status_text = (
                f"Waiting for players "
                f"({players}/{MIN_PLAYERS_TO_START})"
            )

        else:

            game_status_text = (
                "Game finished"
            )


        return jsonify({

            "success": True,

            "players": players,

            "cards": cards,

            "prize_pool": 0,

            "current_number":
                current_number,

            "called_numbers":
                called_numbers,

            "status":
                game_status_text,

            "running":
                running,

            "winner":
                winner

        })


    except Exception as e:

        print(
            "Game status error:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "players": 0,

            "cards": 0,

            "prize_pool": 0,

            "current_number": None,

            "called_numbers": [],

            "status":
                "Game status unavailable",

            "running": False,

            "winner": None

        }), 500


# ============================================================
# BINGO CLAIM
# ============================================================

@app.route(
    "/api/bingo",
    methods=["POST"]
)
def bingo():

    data = request.get_json(
        silent=True
    ) or {}

    user_id = (
        data.get("telegram_id")
        or data.get("user_id")
    )

    if not user_id:

        return jsonify({

            "success": False,

            "message":
                "Telegram user ID missing"

        }), 400


    try:

        # ----------------------------------------------------
        # Use the server-side card
        # ----------------------------------------------------

        if user_id not in game.players:

            return jsonify({

                "success": False,

                "bingo": False,

                "message":
                    "You have not joined this game."

            }), 400


        card = game.players[user_id]


        if game.check_bingo(
            user_id,
            card
        ):

            winner = game.set_winner(
                user_id
            )

            return jsonify({

                "success": True,

                "bingo": True,

                "winner": winner,

                "message":
                    "🏆 BINGO! You are the winner!"

            })


        return jsonify({

            "success": False,

            "bingo": False,

            "message":
                "Bingo not confirmed yet."

        })


    except Exception as e:

        print(
            "Bingo error:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "bingo": False,

            "message":
                "Unable to check Bingo."

        }), 500


# ============================================================
# TELEGRAM WEBHOOK
# ============================================================

@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    try:

        ensure_telegram_initialized()


        data = request.get_json(
            force=True
        )

        if not data:

            return (
                "Invalid update",
                400
            )


        update = Update.de_json(
            data,
            telegram_app.bot
        )


        if update is None:

            return (
                "Invalid Telegram update",
                400
            )


        telegram_loop.run_until_complete(
            telegram_app.process_update(
                update
            )
        )


        print(
            "Telegram webhook update processed."
        )


        return (
            "OK",
            200
        )


    except Exception as e:

        print(
            "Webhook error:",
            repr(e)
        )

        return (
            "Webhook error",
            500
        )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )
