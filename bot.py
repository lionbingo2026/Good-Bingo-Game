from pathlib import Path

import logging
import sqlite3

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    MenuButtonWebApp,
    WebAppInfo,
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import (
    GAME_NAME,
    MINI_APP_URL,
    REGISTRATION_BONUS,
    MIN_DEPOSIT,
    MIN_WITHDRAW,
    MIN_REMAINING_BALANCE,
    CURRENCY,
)
from database import (
    create_user,
    get_user,
)
from cartela import format_card
from shared import game


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO
)


# ============================================================
# REGISTRATION
# ============================================================

REGISTRATION_NAME, REGISTRATION_PHONE = range(2)


# ============================================================
# MAIN MENU
# ============================================================

def main_menu_keyboard():

    return ReplyKeyboardMarkup(
        [
            ["🏠 Start", "👤 Registration / Profile"],
            ["📱 Phone Number", "💰 Wallet / Balance"],
            ["➕ Deposit", "💸 Withdrawal"],
            ["🎫 My Cards", "🎯 Play Bingo"],
            ["🏆 Winners", "📜 Transactions"],
            ["ℹ️ Help"],
        ],
        resize_keyboard=True,
    )


# ============================================================
# /start
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    try:

        existing_user = get_user(user.id)

        if existing_user:

            await update.message.reply_text(
                f"🎲 {GAME_NAME}\n\n"
                f"Welcome back, {user.first_name}! 👋\n\n"
                f"💰 Balance: {existing_user['balance']} ETB",
                reply_markup=main_menu_keyboard(),
            )

            return ConversationHandler.END

        context.user_data.clear()

        await update.message.reply_text(
            f"🎉 Welcome to {GAME_NAME}!\n\n"
            "Let's create your account.\n\n"
            "Please enter your full name:"
        )

        return REGISTRATION_NAME

    except Exception as e:

        logging.exception(
            f"Start error: {e}"
        )

        await update.message.reply_text(
            "❌ Error starting registration."
        )

        return ConversationHandler.END


# ============================================================
# REGISTRATION NAME
# ============================================================

async def registration_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    name = update.message.text.strip()

    if len(name) < 2:

        await update.message.reply_text(
            "❌ Please enter a valid name."
        )

        return REGISTRATION_NAME

    context.user_data["full_name"] = name

    keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    "📱 Share Phone Number",
                    request_contact=True,
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await update.message.reply_text(
        "Great! 👍\n\n"
        "Now please share your phone number "
        "using the button below.",
        reply_markup=keyboard,
    )

    return REGISTRATION_PHONE


# ============================================================
# REGISTRATION PHONE
# ============================================================

async def registration_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    contact = update.message.contact

    if not contact:

        await update.message.reply_text(
            "❌ Please use the "
            "'📱 Share Phone Number' button."
        )

        return REGISTRATION_PHONE

    if (
        contact.user_id
        and contact.user_id != update.effective_user.id
    ):

        await update.message.reply_text(
            "❌ Please share your own phone number."
        )

        return REGISTRATION_PHONE

    user = update.effective_user

    full_name = context.user_data.get(
        "full_name"
    )

    phone_number = contact.phone_number

    try:

        new_user = create_user(
            user.id,
            user.username,
            full_name,
            phone_number,
        )

        if not new_user:

            await update.message.reply_text(
                "Welcome back! Your account already exists.",
                reply_markup=main_menu_keyboard(),
            )

            return ConversationHandler.END

        await update.message.reply_text(
            "✅ Registration complete!\n\n"
            f"🎉 Welcome to {GAME_NAME}!\n\n"
            "Your account is ready.\n\n"
            f"🎁 Registration Bonus: +{REGISTRATION_BONUS} {CURRENCY}\n"
            f"💰 Your balance: {REGISTRATION_BONUS} {CURRENCY}\n\n"
            "Choose an option below to continue.",
            reply_markup=main_menu_keyboard(),
        )

        context.user_data.clear()

        return ConversationHandler.END

    except Exception as e:

        logging.exception(
            f"Registration error: {e}"
        )

        await update.message.reply_text(
            "❌ Registration failed. "
            "Please try /start again.",
            reply_markup=main_menu_keyboard(),
        )

        return ConversationHandler.END


# ============================================================
# CANCEL REGISTRATION
# ============================================================

async def cancel_registration(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data.clear()

    await update.message.reply_text(
        "Registration cancelled.",
        reply_markup=main_menu_keyboard(),
    )

    return ConversationHandler.END


# ============================================================
# MY CARDS
# ============================================================

async def my_cards(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "🎫 MY CARDS\n\n"
        "Your Bingo cards will appear here.\n\n"
        "🎮 Tap Play Bingo to select a card "
        "and join a game."
    )


# ============================================================
# WINNERS
# ============================================================

async def winners(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "🏆 WINNERS\n\n"
        "No winners recorded yet.\n\n"
        "Play Bingo to become a winner! 🎉"
    )


# ============================================================
# GAME RULES
# ============================================================

async def game_rules(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "ℹ️ GAME RULES\n\n"
        "🎯 Bingo type: 75 Ball\n"
        "🎫 Card price: 10 ETB\n"
        "👥 Minimum players: 2\n"
        "🏆 Maximum winners: 1\n"
        "💰 Prize pool: 80% of the game pool\n"
        "🏦 Platform fee: 20%\n\n"
        "Select a card, join the game, "
        "and complete a Bingo pattern to win."
    )


# ============================================================
# /play
# ============================================================

async def play(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    try:

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

            players = result.get(
                "players",
                0,
            )

            await update.message.reply_text(
                f"⏳ Waiting for players: {players}/2"
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
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    try:

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
            len(game.players),
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
    context: ContextTypes.DEFAULT_TYPE,
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

            try:

                sound_path = Path(
                    "static/sounds/bingo.wav"
                )

                with sound_path.open("rb") as audio:

                    await context.bot.send_audio(
                        chat_id=winner,
                        audio=audio,
                        caption="🎉 BINGO! Congratulations! 🏆",
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
    context: ContextTypes.DEFAULT_TYPE,
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
# WALLET
# ============================================================

async def menu_wallet(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    try:

        data = get_user(
            user.id
        )

        if not data:

            await update.message.reply_text(
                "Please use /start first."
            )

            return

        await update.message.reply_text(
            f"💰 Wallet\n\n"
            f"Balance: {data['balance']} ETB"
        )

    except Exception as e:

        logging.exception(
            f"Wallet error: {e}"
        )

        await update.message.reply_text(
            "❌ Could not load wallet."
        )


# ============================================================
# ACCOUNT
# ============================================================

async def menu_account(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    try:

        data = get_user(
            user.id
        )

        if not data:

            await update.message.reply_text(
                "Please use /start first."
            )

            return

        full_name = (
            data["full_name"]
            or user.first_name
        )

        phone = (
            data["phone_number"]
            or "Not provided"
        )

        await update.message.reply_text(
            f"👤 My Account\n\n"
            f"Name: {full_name}\n"
            f"Phone: {phone}\n"
            f"Telegram ID: {user.id}\n"
            f"Balance: {data['balance']} ETB"
        )

    except Exception as e:

        logging.exception(
            f"Account error: {e}"
        )

        await update.message.reply_text(
            "❌ Could not load account."
        )


# ============================================================
# TRANSACTIONS
# ============================================================

async def menu_transactions(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    try:

        conn = sqlite3.connect(
            "bingo.db"
        )

        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT amount, type, status
            FROM transactions
            WHERE telegram_id=?
            ORDER BY id DESC
            LIMIT 10
            """,
            (user.id,),
        ).fetchall()

        conn.close()

        if not rows:

            await update.message.reply_text(
                "📋 Transactions\n\n"
                "No transactions yet."
            )

            return

        lines = [
            "📋 Recent Transactions\n"
        ]

        for row in rows:

            lines.append(
                f"• {row['type']}: "
                f"{row['amount']} ETB "
                f"({row['status']})"
            )

        await update.message.reply_text(
            "\n".join(lines)
        )

    except Exception as e:

        logging.exception(
            f"Transactions error: {e}"
        )

        await update.message.reply_text(
            "❌ Could not load transactions."
        )


# ============================================================
# HELP
# ============================================================

async def menu_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        f"❓ {GAME_NAME} Help\n\n"
        "🎮 /play - Get a Bingo card\n"
        "🎮 /join - Join the current game\n"
        "🎱 /draw - Draw a number\n"
        "💰 /balance - Check balance\n"
        "❌ /cancel - Cancel registration\n"
        "/start - Open the main menu"
    )


# ============================================================
# DEPOSIT
# ============================================================

async def menu_deposit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "➕ Deposit\n\n"
        "Deposit functionality is currently being prepared."
    )


# ============================================================
# WITHDRAWAL
# ============================================================

async def menu_withdrawal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "💸 Withdrawal\n\n"
        "Withdrawal functionality is currently being prepared."
    )


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update,
    context,
):

    logging.error(
        "========== TELEGRAM ERROR =========="
    )

    logging.error(
        "ERROR TYPE: %s",
        type(context.error).__name__,
    )

    logging.error(
        "ERROR: %s",
        context.error,
    )

    logging.exception(
        "FULL TRACEBACK"
    )

    logging.error(
        "===================================="
    )


# ============================================================
# TELEGRAM MINI APP MENU BUTTON
# ============================================================

async def setup_mini_app_menu(
    application,
):

    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🎮 Play Bingo",
            web_app=WebAppInfo(
                url=MINI_APP_URL
            ),
        )
    )


# ============================================================
# SETUP TELEGRAM HANDLERS
# ============================================================

def setup_handlers(
    application,
):

    # --------------------------------------------------------
    # REGISTRATION CONVERSATION
    # --------------------------------------------------------

    registration_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                "start",
                start
            )
        ],

        states={

            REGISTRATION_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    registration_name,
                )
            ],

            REGISTRATION_PHONE: [
                MessageHandler(
                    filters.CONTACT,
                    registration_phone,
                )
            ],
        },

        fallbacks=[
            CommandHandler(
                "cancel",
                cancel_registration,
            ),

            CommandHandler(
                "start",
                start,
            ),
        ],
    )

    application.add_handler(
        registration_handler
    )

    # ========================================================
    # MAIN MENU BUTTONS
    # ========================================================

    application.add_handler(
        MessageHandler(
            filters.Regex("^🏠 Start$"),
            start,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^🎯 Play Bingo$"),
            play,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^🎫 My Cards$"),
            my_cards,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^💰 Wallet / Balance$"),
            menu_wallet,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^➕ Deposit$"),
            menu_deposit,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^💸 Withdrawal$"),
            menu_withdrawal,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^📜 Transactions$"),
            menu_transactions,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^👤 Registration / Profile$"),
            menu_account,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^🏆 Winners$"),
            winners,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex("^ℹ️ Help$"),
            menu_help,
        )
    )

    # ========================================================
    # COMMANDS
    # ========================================================

    application.add_handler(
        CommandHandler(
            "play",
            play,
        )
    )

    application.add_handler(
        CommandHandler(
            "join",
            join,
        )
    )

    application.add_handler(
        CommandHandler(
            "draw",
            draw,
        )
    )

    application.add_handler(
        CommandHandler(
            "balance",
            balance,
        )
    )

    # ========================================================
    # ERROR HANDLER
    # ========================================================

    application.add_error_handler(
        error_handler
    )
