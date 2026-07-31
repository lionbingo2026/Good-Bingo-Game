import sqlite3
import os

DB = "bingo.db"

def connect():
    return sqlite3.connect(DB)


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        balance INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def create_user(telegram_id, username=None):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO users
        (telegram_id, username, balance)
        VALUES (?, ?, ?)
        """,
        (telegram_id, username, 0)
    )

    conn.commit()
    conn.close()


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
