from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes
)
import logging

from config import GAME_NAME
from database import create_user, get_user
from cards import generate_card, card_to_text
from game import BingoGame


logging.basicConfig(
    level=logging.INFO
)


game = BingoGame()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
            "/play - Get Bingo card\n"
            "/join - Join game\n"
            "/draw - Draw number\n"
            "/balance - Check wallet"
        )

    except Exception as e:
        logging.error(f"Start error: {e}")
        await update.message.reply_text(
            "❌ Error starting account."
        )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    try:
        card = generate_card()

        game.add_player(
            user.id,
            card
        )

        await update.message.reply_text(
            "🎫 Your Bingo card:\n\n"
            + card_to_text(card)
        )

    except Exception as e:
        logging.error(f"Play error: {e}")
        await update.message.reply_text(
            "❌ Cannot create card."
        )


async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    try:
        if not game.running:
            game.start_game()

        card = generate_card()

        added = game.add_player(
            user.id,
            card
        )

        if added:
            await update.message.reply_text(
                "✅ You joined Good Bingo Game!"
            )
        else:
            await update.message.reply_text(
                "❌ Game is full."
            )

    except Exception as e:
        logging.error(f"Join error: {e}")
        await update.message.reply_text(
            "❌ Join failed."
        )


async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        number = game.draw_number()

        if number:
            await update.message.reply_text(
                f"🎱 Called number: {number}"
            )

            winner = game.check_winner()

            if winner:
                await update.message.reply_text(
                    f"🏆 Winner: {winner}"
                )

        else:
            await update.message.reply_text(
                "Game is not running."
            )

    except Exception as e:
        logging.error(f"Draw error: {e}")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    try:
        data = get_user(user.id)

        if data:
            await update.message.reply_text(
                f"💰 Your balance: {data['balance']} ETB"
            )
        else:
            await update.message.reply_text(
                "Please use /start first."
            )

    except Exception as e:
        logging.error(f"Balance error: {e}")


async def error_handler(update, context):
    logging.error(
        f"Telegram error: {context.error}"
    )


def setup_handlers(application):

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("play", play)
    )

    application.add_handler(
        CommandHandler("join", join)
    )

    application.add_handler(
        CommandHandler("draw", draw)
    )

    application.add_handler(
        CommandHandler("balance", balance)
    )

    application.add_error_handler(
        error_handler
    )
