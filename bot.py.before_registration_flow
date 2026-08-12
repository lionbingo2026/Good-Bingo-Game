from pathlib import Path
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import logging

from config import GAME_NAME
from database import create_user, get_user
from cartela import generate_card, format_card
from shared import game


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO
)


# ============================================================
# /start
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    try:
        new_user = create_user(
            user.id,
            user.username
        )

        if new_user:
            bonus = "🎁 Registration bonus: 10 ETB"
        else:
            bonus = "Welcome back!"

        await update.message.reply_text(
            f"🎲 {GAME_NAME}\n\n"
            f"Hello {user.first_name}\n"
            f"{bonus}\n\n"
            "🎫 /play - Get Bingo card\n"
            "🎮 /join - Join game\n"
            "🎱 /draw - Draw number\n"
            "💰 /balance - Check wallet"
        )

    except Exception as e:

        logging.exception(
            f"Start error: {e}"
        )

        await update.message.reply_text(
            "❌ Error starting account."
        )


# ============================================================
# /play
# ============================================================

async def play(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    try:

        # Add player and automatically generate
        # a standard 75-ball Bingo card.
        result = game.add_player(
            user.id
        )

        if not result.get("success"):

            if result.get("message") == "Already joined":

                card = result.get("card")

                if card:
                    await update.message.reply_text(
                        "🎫 You already have a Bingo card:\n\n"
                        + format_card(card)
                    )
                else:
                    await update.message.reply_text(
                        "ℹ️ You are already in the game."
                    )

                return

            await update.message.reply_text(
                f"❌ {result.get('message', 'Cannot join game.')}"
            )

            return

        card = result.get("card")

        await update.message.reply_text(
            "🎫 Your Bingo card:\n\n"
            + format_card(card)
        )

        if result.get("running"):
            await update.message.reply_text(
                "🎱 Good Bingo Game is now running!"
            )
        else:
            players = result.get("players", 0)

            await update.message.reply_text(
                f"⏳ Waiting for players: "
                f"{players}/2"
            )

    except Exception as e:

        logging.exception(
            f"Play error: {e}"
        )

        await update.message.reply_text(
            "❌ Cannot create Bingo card."
        )


# ============================================================
# /join
# ============================================================

async def join(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    try:

        # add_player() handles:
        # - duplicate players
        # - card generation
        # - maximum players
        # - automatic start at 2 players
        result = game.add_player(
            user.id
        )

        if not result.get("success"):

            if result.get("message") == "Already joined":

                await update.message.reply_text(
                    "ℹ️ You are already in Good Bingo Game."
                )

            else:

                await update.message.reply_text(
                    f"❌ {result.get('message', 'Join failed.')}"
                )

            return

        players = result.get(
            "players",
            len(game.players)
        )

        if result.get("running"):

            await update.message.reply_text(
                "✅ You joined Good Bingo Game!\n\n"
                f"👥 Players: {players}\n"
                "🎱 Game is running."
            )

        else:

            await update.message.reply_text(
                "✅ You joined Good Bingo Game!\n\n"
                f"👥 Players: {players}/2\n"
                "⏳ Waiting for another player."
            )

    except Exception as e:

        logging.exception(
            f"Join error: {e}"
        )

        await update.message.reply_text(
            "❌ Join failed."
        )


# ============================================================
# /draw
# ============================================================

async def draw(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        number = game.draw_number()

        if number is None:

            if game.winner is not None:

                await update.message.reply_text(
                    f"🏆 Winner: {game.winner}"
                )

            elif not game.players:

                await update.message.reply_text(
                    "⏳ No players have joined."
                )

            elif len(game.players) < 2:

                await update.message.reply_text(
                    "⏳ Waiting for at least 2 players."
                )

            else:

                await update.message.reply_text(
                    "🛑 Game is not running."
                )

            return

        display_number = game.format_number(
            number
        )

        await update.message.reply_text(
            f"🎱 Called number: {display_number}"
        )

        winner = game.check_winner()

        if winner is not None:

            await update.message.reply_text(
                f"🏆 BINGO!\n\n"
                f"🏆 Winner: {winner}"
            )

            # Send Bingo sound directly to the winning Telegram user.
            try:
                sound_path = Path("static/sounds/bingo.wav")

                with sound_path.open("rb") as audio:
                    await context.bot.send_audio(
                        chat_id=winner,
                        audio=audio,
                        caption="🎉 BINGO! Congratulations! 🏆"
                    )

            except Exception as audio_error:
                logging.exception(
                    f"Bingo audio error: {audio_error}"
                )

    except Exception as e:

        logging.exception(
            f"Draw error: {e}"
        )

        await update.message.reply_text(
            "❌ Draw failed."
        )


# ============================================================
# /balance
# ============================================================

async def balance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    try:

        data = get_user(
            user.id
        )

        if data:

            await update.message.reply_text(
                f"💰 Your balance: "
                f"{data['balance']} ETB"
            )

        else:

            await update.message.reply_text(
                "Please use /start first."
            )

    except Exception as e:

        logging.exception(
            f"Balance error: {e}"
        )

        await update.message.reply_text(
            "❌ Could not check balance."
        )


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update,
    context
):

    logging.error(
        f"Telegram error: {context.error}"
    )


# ============================================================
# SETUP TELEGRAM HANDLERS
# ============================================================

def setup_handlers(application):

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "play",
            play
        )
    )

    application.add_handler(
        CommandHandler(
            "join",
            join
        )
    )

    application.add_handler(
        CommandHandler(
            "draw",
            draw
        )
    )

    application.add_handler(
        CommandHandler(
            "balance",
            balance
        )
    )

    application.add_error_handler(
        error_handler
    )
