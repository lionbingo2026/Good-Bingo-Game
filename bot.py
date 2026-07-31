from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import BOT_TOKEN, GAME_NAME
from database import create_user, get_user
from cards import generate_card, card_to_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

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
        "/balance - Check wallet"
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):

    card = generate_card()

    await update.message.reply_text(
        card_to_text(card)
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = get_user(update.effective_user.id)

    if user:
        await update.message.reply_text(
            f"💰 Balance: {user[3]} ETB"
        )
    else:
        await update.message.reply_text(
            "Please use /start first"
        )


def main():

    app = Application.builder().token(
        BOT_TOKEN
    ).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("play", play)
    )

    app.add_handler(
        CommandHandler("balance", balance)
    )

    print("🤖 Good Bingo Game Bot Running")

    app.run_polling()


if __name__ == "__main__":
    main()
