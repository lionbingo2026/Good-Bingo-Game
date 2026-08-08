




from flask import Flask, request, jsonify, render_template
from telegram import Update
from telegram.ext import Application
import asyncio
import os

from bot import setup_handlers
from database import init_db
from game import BingoGame


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

        print(
            "Telegram Application initialized."
        )


# Initialize when the Gunicorn worker loads.
ensure_telegram_initialized()


# ============================================================
# BINGO GAME
# ============================================================

game = BingoGame()


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
        "status": "Good Bingo Game running"
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

    if not user_id:

        return jsonify({
            "success": False,
            "message": "Telegram user ID missing"
        }), 400

    try:

        if hasattr(
            game,
            "add_player"
        ):

            try:

                game.add_player(
                    user_id
                )

            except TypeError:

                game.add_player(
                    str(user_id)
                )

        return jsonify({

            "success": True,

            "message": (
                f"Welcome {first_name}! "
                "You joined Good Bingo Game"
            ),

            "user_id": user_id,

            "username": username
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
# GAME STATUS
# ============================================================

@app.route(
    "/api/game",
    methods=["GET"]
)
def game_status():

    players = 0
    cards = 0
    prize_pool = 0
    current_number = None
    called_numbers = []
    status = "Waiting for game..."

    try:

        # ----------------------------------------------------
        # Players
        # ----------------------------------------------------

        if hasattr(
            game,
            "players"
        ):

            if isinstance(
                game.players,
                dict
            ):

                players = len(
                    game.players
                )

            elif isinstance(
                game.players,
                list
            ):

                players = len(
                    game.players
                )


        # ----------------------------------------------------
        # Cards
        # ----------------------------------------------------

        if hasattr(
            game,
            "cards"
        ):

            if isinstance(
                game.cards,
                dict
            ):

                cards = len(
                    game.cards
                )

            elif isinstance(
                game.cards,
                list
            ):

                cards = len(
                    game.cards
                )


        # ----------------------------------------------------
        # Called numbers
        # ----------------------------------------------------

        if hasattr(
            game,
            "called_numbers"
        ):

            called_numbers = list(
                game.called_numbers
            )


        # ----------------------------------------------------
        # Current number
        # ----------------------------------------------------

        if called_numbers:

            current_number = (
                called_numbers[-1]
            )


        # ----------------------------------------------------
        # Game status
        # ----------------------------------------------------

        if players > 0:

            status = "Game ready"


        return jsonify({

            "success": True,

            "players": players,

            "cards": cards,

            "prize_pool": prize_pool,

            "current_number":
                current_number,

            "called_numbers":
                called_numbers,

            "status":
                status
        })


    except Exception as e:

        print(
            "Game status error:",
            repr(e)
        )

        return jsonify({

            "success": False,

            "players": players,

            "cards": cards,

            "prize_pool": prize_pool,

            "current_number":
                current_number,

            "called_numbers":
                called_numbers,

            "status":
                status
        })


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

    card = data.get("card")


    # --------------------------------------------------------
    # User ID required
    # --------------------------------------------------------

    if not user_id:

        return jsonify({

            "success": False,

            "message":
                "Telegram user ID missing"

        }), 400


    # --------------------------------------------------------
    # Card required
    # --------------------------------------------------------

    if not card:

        return jsonify({

            "success": False,

            "message":
                "Bingo card missing"

        }), 400


    try:

        if hasattr(
            game,
            "check_bingo"
        ):

            result = game.check_bingo(
                user_id,
                card
            )


            if result:

                return jsonify({

                    "success": True,

                    "bingo": True,

                    "message":
                        "BINGO! Your claim was accepted!"
                })


            return jsonify({

                "success": False,

                "bingo": False,

                "message":
                    "Bingo not confirmed yet."
            })


        return jsonify({

            "success": False,

            "bingo": False,

            "message":
                "Bingo checking is not configured yet."
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

        # ----------------------------------------------------
        # Make absolutely sure this worker has an initialized
        # Telegram Application before processing the update.
        # ----------------------------------------------------

        ensure_telegram_initialized()


        # ----------------------------------------------------
        # Read Telegram JSON
        # ----------------------------------------------------

        data = request.get_json(
            force=True
        )

        if not data:

            return (
                "Invalid update",
                400
            )


        # ----------------------------------------------------
        # Convert JSON into Telegram Update
        # ----------------------------------------------------

        update = Update.de_json(
            data,
            telegram_app.bot
        )


        if update is None:

            return (
                "Invalid Telegram update",
                400
            )


        # ----------------------------------------------------
        # Process Telegram update
        # ----------------------------------------------------

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
