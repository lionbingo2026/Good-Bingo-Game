import sqlite3
from config import REGISTRATION_BONUS


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
        balance INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        type TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        game_id TEXT
    )
    """)

    # --------------------------------------------------------
    # Upgrade existing database
    # --------------------------------------------------------

    cur.execute("PRAGMA table_info(transactions)")
    columns = {
        row["name"]
        for row in cur.fetchall()
    }

    if "game_id" not in columns:
        cur.execute("""
        ALTER TABLE transactions
        ADD COLUMN game_id TEXT
        """)

    # Prevent the same game from paying the winner twice.
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS
    idx_one_winner_payout_per_game
    ON transactions(game_id, type)
    WHERE type = 'winner_payout'
    """)

    # --------------------------------------------------------
    # Upgrade users table for registration
    # --------------------------------------------------------

    cur.execute("PRAGMA table_info(users)")
    user_columns = {
        row["name"]
        for row in cur.fetchall()
    }

    if "full_name" not in user_columns:
        cur.execute("""
        ALTER TABLE users
        ADD COLUMN full_name TEXT
        """)

    if "phone_number" not in user_columns:
        cur.execute("""
        ALTER TABLE users
        ADD COLUMN phone_number TEXT
        """)

    conn.commit()
    conn.close()


def create_user(
    telegram_id,
    username,
    full_name=None,
    phone_number=None
):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT telegram_id FROM users WHERE telegram_id=?",
            (telegram_id,)
        )

        if cur.fetchone():
            return False

        cur.execute("""
        INSERT INTO users (
            telegram_id,
            username,
            full_name,
            phone_number,
            balance
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            telegram_id,
            username,
            full_name,
            phone_number,
            REGISTRATION_BONUS
        ))

        cur.execute("""
        INSERT INTO transactions (
            telegram_id,
            amount,
            type,
            status,
            game_id
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            telegram_id,
            REGISTRATION_BONUS,
            "registration_bonus",
            "completed",
            None
        ))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


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


def add_transaction(
    telegram_id,
    amount,
    tx_type,
    status="pending",
    game_id=None
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO transactions
    (telegram_id, amount, type, status, game_id)
    VALUES (?, ?, ?, ?, ?)
    """, (
        telegram_id,
        amount,
        tx_type,
        status,
        game_id
    ))

    conn.commit()
    conn.close()



def get_pending_transactions(tx_type):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        id,
        telegram_id,
        amount,
        type,
        status,
        game_id
    FROM transactions
    WHERE type=?
      AND status='pending'
    ORDER BY id ASC
    """, (tx_type,))

    rows = cur.fetchall()
    conn.close()

    return rows




def approve_transaction(transaction_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT telegram_id, amount, type, status
        FROM transactions
        WHERE id=?
        """, (transaction_id,))

        row = cur.fetchone()

        if row is None or row["status"] != "pending":
            conn.rollback()
            return False

        if row["type"] == "deposit":
            cur.execute("""
            UPDATE users
            SET balance = balance + ?
            WHERE telegram_id=?
            """, (row["amount"], row["telegram_id"]))

        elif row["type"] == "withdrawal":
            cur.execute("""
            UPDATE users
            SET balance = balance - ?
            WHERE telegram_id=?
            AND balance - ? >= ?
            """, (
                row["amount"],
                row["telegram_id"],
                row["amount"],
                0,
            ))

            if cur.rowcount != 1:
                conn.rollback()
                return False

        else:
            conn.rollback()
            return False

        cur.execute("""
        UPDATE transactions
        SET status='completed'
        WHERE id=?
        AND status='pending'
        """, (transaction_id,))

        if cur.rowcount != 1:
            conn.rollback()
            return False

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def reject_transaction(transaction_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        UPDATE transactions
        SET status='rejected'
        WHERE id=?
        AND status='pending'
        """, (transaction_id,))

        if cur.rowcount != 1:
            conn.rollback()
            return False

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()



def get_balance(telegram_id):
    user = get_user(telegram_id)

    if user:
        return user["balance"]

    return 0


def payout_winner(
    telegram_id,
    amount,
    game_id
):
    """
    Credit a Bingo winner exactly once.

    Returns:
        True  = payout completed
        False = payout was already completed or failed
    """

    if amount <= 0:
        return False

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Make sure the user exists.
        cur.execute("""
        SELECT telegram_id
        FROM users
        WHERE telegram_id=?
        """, (telegram_id,))

        if cur.fetchone() is None:
            conn.rollback()
            return False

        # Check whether this game has already paid a winner.
        cur.execute("""
        SELECT id
        FROM transactions
        WHERE game_id=?
        AND type='winner_payout'
        LIMIT 1
        """, (game_id,))

        if cur.fetchone() is not None:
            conn.rollback()
            return False

        # Credit wallet.
        cur.execute("""
        UPDATE users
        SET balance = balance + ?
        WHERE telegram_id=?
        """, (
            amount,
            telegram_id
        ))

        if cur.rowcount != 1:
            conn.rollback()
            return False

        # Record payout.
        cur.execute("""
        INSERT INTO transactions
        (
            telegram_id,
            amount,
            type,
            status,
            game_id
        )
        VALUES (?, ?, 'winner_payout', 'completed', ?)
        """, (
            telegram_id,
            amount,
            game_id
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:
        # Another call already paid this game.
        conn.rollback()
        return False

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
