from database import (
    get_user,
    update_balance,
    payout_winner
)

from config import (
    MIN_DEPOSIT,
    MIN_WITHDRAW
)


def get_balance(telegram_id):
    user = get_user(telegram_id)

    if user:
        return user["balance"]

    return 0


def deposit(telegram_id, amount):

    if amount < MIN_DEPOSIT:
        return False

    update_balance(telegram_id, amount)

    return True


def withdraw(telegram_id, amount):

    MIN_REMAINING_BALANCE = 50

    if amount < MIN_WITHDRAW:
        return False

    balance = get_balance(telegram_id)

    if balance < amount:
        return False

    if balance - amount < MIN_REMAINING_BALANCE:
        return False

    update_balance(telegram_id, -amount)

    return True


def add_bingo_winnings(
    telegram_id,
    amount,
    game_id
):
    """
    Add Bingo winnings to the player's wallet.

    The database guarantees that the same game
    cannot pay the winner twice.
    """

    return payout_winner(
        telegram_id,
        amount,
        game_id
    )
