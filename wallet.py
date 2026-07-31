from database import get_user, update_balance
from config import MIN_DEPOSIT, MIN_WITHDRAW


def get_balance(telegram_id):
    user = get_user(telegram_id)

    if user:
        return user[3]

    return 0


def deposit(telegram_id, amount):

    if amount < MIN_DEPOSIT:
        return False

    update_balance(telegram_id, amount)
    return True


def withdraw(telegram_id, amount):

    if amount < MIN_WITHDRAW:
        return False

    balance = get_balance(telegram_id)

    if balance < amount:
        return False

    update_balance(telegram_id, -amount)
    return True
