import sqlite3
from config import START_BALANCE, REGISTRATION_BONUS

DB = "data/bingo.db"


def connect():
    return sqlite3.connect(DB)


def create_tables():
    conn = connect()
    cur = conn.cursor()

    # Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        balance INTEGER DEFAULT 0
    )
    """)

    # Bingo cards
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        card TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Games
    cur.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT,
        called_numbers TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_user(telegram_id, username):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    user = cur.fetchone()

    if user:
        conn.close()
        return False

    cur.execute(
        """
        INSERT INTO users
        (telegram_id, username, balance)
        VALUES (?, ?, ?)
        """,
        (
            telegram_id,
            username,
            START_BALANCE + REGISTRATION_BONUS
        )
    )

    conn.commit()
    conn.close()

    return True


def get_user(telegram_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    user = cur.fetchone()

    conn.close()
    return user


def update_balance(telegram_id, amount):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET balance = balance + ?
        WHERE telegram_id=?
        """,
        (amount, telegram_id)
    )

    conn.commit()
    conn.close()


# Create database automatically
create_tables()
