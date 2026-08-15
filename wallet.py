from database import (
    get_user,
    update_balance,
    add_transaction,
    payout_winner,
)

from config import (
    MIN_DEPOSIT,
    MIN_WITHDRAW,
    MIN_REMAINING_BALANCE,
)


def get_balance(telegram_id):
    user = get_user(telegram_id)

    if user:
        return user["balance"]

    return 0


def deposit(telegram_id, amount):
    """
    Add an approved deposit to the wallet.

    Returns:
        True  = deposit completed
        False = invalid amount or user does not exist
    """

    if amount < MIN_DEPOSIT:
        return False

    if get_user(telegram_id) is None:
        return False

    update_balance(
        telegram_id,
        amount,
    )

    add_transaction(
        telegram_id,
        amount,
        "deposit",
        "completed",
    )

    return True


def withdraw(telegram_id, amount):
    """
    Withdraw money from the wallet.

    Returns:
        True  = withdrawal completed
        False = validation failed
    """

    if amount < MIN_WITHDRAW:
        return False

    balance = get_balance(telegram_id)

    if balance < amount:
        return False

    if balance - amount < MIN_REMAINING_BALANCE:
        return False

    update_balance(
        telegram_id,
        -amount,
    )

    add_transaction(
        telegram_id,
        amount,
        "withdrawal",
        "completed",
    )

    return True


def add_bingo_winnings(
    telegram_id,
    amount,
    game_id,
):
    """
    Add Bingo winnings to the player's wallet.

    The database guarantees that the same game
    cannot pay the winner twice.
    """

    return payout_winner(
        telegram_id,
        amount,
        game_id,
    )
