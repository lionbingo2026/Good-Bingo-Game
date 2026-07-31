from config import MIN_DEPOSIT, CURRENCY
from database import update_balance


def create_deposit_request(telegram_id, amount):
    if amount < MIN_DEPOSIT:
        return False, f"Minimum deposit is {MIN_DEPOSIT} {CURRENCY}"

    return True, (
        "Deposit Request\n"
        f"User ID: {telegram_id}\n"
        f"Amount: {amount} {CURRENCY}\n"
        "Status: Pending Admin Approval"
    )


def approve_deposit(telegram_id, amount):
    update_balance(telegram_id, amount)
    return f"Deposit approved: {amount} {CURRENCY} added."


def reject_deposit():
    return "Deposit request rejected."


if __name__ == "__main__":
    print("Good Bingo Game Telebirr Module Ready")
