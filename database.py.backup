import sqlite3

DB_NAME = "bingo.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        balance INTEGER DEFAULT 10
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        type TEXT NOT NULL,
        status TEXT DEFAULT 'pending'
    )
    """)

    conn.commit()
    conn.close()


def create_user(telegram_id, username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT telegram_id FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    if cur.fetchone():
        conn.close()
        return False

    cur.execute("""
    INSERT INTO users (telegram_id, username, balance)
    VALUES (?, ?, ?)
    """, (telegram_id, username, 10))

    conn.commit()
    conn.close()
    return True


def get_user(telegram_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    user = cur.fetchone()

    conn.close()
    return user


def update_balance(telegram_id, amount):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET balance = balance + ?
    WHERE telegram_id=?
    """, (amount, telegram_id))

    conn.commit()
    conn.close()


def add_transaction(telegram_id, amount, tx_type, status="pending"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO transactions
    (telegram_id, amount, type, status)
    VALUES (?, ?, ?, ?)
    """, (telegram_id, amount, tx_type, status))

    conn.commit()
    conn.close()


def get_balance(telegram_id):
    user = get_user(telegram_id)
    if user:
        return user["balance"]
    return 0
