from config import ADMIN_ID
from database import update_balance, get_user


def is_admin(user_id):
    return user_id == ADMIN_ID


def add_balance(admin_id, telegram_id, amount):
    if not is_admin(admin_id):
        return False, "Access denied."

    update_balance(telegram_id, amount)
    return True, f"Added {amount} ETB."


def deduct_balance(admin_id, telegram_id, amount):
    if not is_admin(admin_id):
        return False, "Access denied."

    update_balance(telegram_id, -amount)
    return True, f"Deducted {amount} ETB."


def user_info(admin_id, telegram_id):
    if not is_admin(admin_id):
        return None

    return get_user(telegram_id)


if __name__ == "__main__":
    print("Good Bingo Game Admin Module Ready")
