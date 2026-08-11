# game.py

import threading
import time
import uuid

from config import (
    MAX_PLAYERS,
    CARD_PRICE,
    WIN_PERCENTAGE
)

from called_number import CalledNumberManager
from cartela import generate_card
from wallet import add_bingo_winnings


# ============================================================
# GOOD BINGO GAME
# 75-BALL BINGO
# ============================================================

MIN_PLAYERS_TO_START = 2

AUTO_DRAW_INTERVAL = 5

START_COUNTDOWN = 10


class BingoGame:

    def __init__(self):

        self.players = {}

        # 300 selectable Bingo cards.
        self.card_catalog = {
            number: generate_card()
            for number in range(1, 301)
        }

        # 75-ball number manager.
        self.number_manager = CalledNumberManager()

        # ----------------------------------------------------
        # GAME STATE
        # ----------------------------------------------------

        self.running = False

        self.winner = None

        self.last_number = None

        # Countdown state.
        self.starting = False
        self.countdown = 0

        # Unique ID for every game.
        self.game_id = None

        # Last completed winner information.
        self.last_winner = None
        self.last_prize = 0

        self._draw_thread = None
        self._countdown_thread = None

        self._draw_stop = threading.Event()
        self._countdown_stop = threading.Event()

        # Prevent two countdown threads.
        self._state_lock = threading.Lock()

    # ========================================================
    # CALLED NUMBERS COMPATIBILITY
    # ========================================================

    @property
    def called_numbers(self):

        return self.number_manager.called_numbers

    # ========================================================
    # START GAME / START COUNTDOWN
    # ========================================================

    def start_game(self):

        with self._state_lock:

            # Not enough players.
            if len(self.players) < MIN_PLAYERS_TO_START:

                self.starting = False
                self.countdown = 0

                print(
                    f"⏳ Waiting for players: "
                    f"{len(self.players)}/"
                    f"{MIN_PLAYERS_TO_START}"
                )

                return False

            # Already live.
            if self.running:
                return True

            # Countdown already running.
            if self.starting:
                return True

            # Start countdown.
            self.starting = True
            self.countdown = START_COUNTDOWN

            self._countdown_stop.clear()

            self._countdown_thread = threading.Thread(
                target=self._countdown_loop,
                daemon=True
            )

            self._countdown_thread.start()

            print(
                f"🚀 Starting in "
                f"{START_COUNTDOWN} seconds..."
            )

            return True

    # ========================================================
    # 10 SECOND COUNTDOWN
    # ========================================================

    def _countdown_loop(self):

        for seconds in range(
            START_COUNTDOWN,
            0,
            -1
        ):

            # Countdown cancelled.
            if self._countdown_stop.is_set():
                return

            # Check player count.
            if len(self.players) < MIN_PLAYERS_TO_START:

                with self._state_lock:
                    self.starting = False
                    self.countdown = 0

                print(
                    "⏳ Not enough players. "
                    "Countdown cancelled."
                )

                return

            with self._state_lock:
                self.countdown = seconds

            print(
                f"🚀 Starting in {seconds} second"
                f"{'' if seconds == 1 else 's'}..."
            )

            # Wait one second.
            if self._countdown_stop.wait(1):
                return

        # ----------------------------------------------------
        # START LIVE GAME
        # ----------------------------------------------------

        with self._state_lock:

            if len(self.players) < MIN_PLAYERS_TO_START:

                self.starting = False
                self.countdown = 0

                print(
                    "⏳ Countdown finished but "
                    "not enough players."
                )

                return

            self.starting = False
            self.countdown = 0

            # New game ID.
            self.game_id = str(uuid.uuid4())

            # Fresh number sequence.
            self.number_manager.reset()

            self.running = True
            self.winner = None
            self.last_number = None

            self.last_winner = None
            self.last_prize = 0

            self._draw_stop.clear()

            self._draw_thread = threading.Thread(
                target=self._auto_draw_loop,
                daemon=True
            )

            self._draw_thread.start()

        print("")
        print("🎱 GOOD BINGO GAME STARTED!")
        print(
            f"🆔 Game: {self.game_id}"
        )
        print(
            f"👥 Players: {len(self.players)}"
        )
        print(
            f"💰 Prize Pool: "
            f"{self.get_prize_pool()} ETB"
        )
        print("🔴 LIVE - Number drawing")
        print("")

        return True

    # ========================================================
    # PRIZE POOL
    # ========================================================

    def get_prize_pool(self):

        return len(self.players) * CARD_PRICE

    # ========================================================
    # WINNER PRIZE
    # ========================================================

    def get_winner_prize(self):

        prize_pool = self.get_prize_pool()

        return int(
            prize_pool * WIN_PERCENTAGE / 100
        )

    # ========================================================
    # AUTOMATIC NUMBER CALLER
    # ========================================================

    def _auto_draw_loop(self):

        while (
            self.running
            and not self._draw_stop.is_set()
        ):

            if self._draw_stop.wait(
                AUTO_DRAW_INTERVAL
            ):
                break

            if not self.running:
                break

            number = self.draw_number()

            if number is None:
                break

    # ========================================================
    # STOP GAME
    # ========================================================

    def stop_game(self):

        self.running = False
        self._draw_stop.set()

        print("🛑 Good Bingo Game Stopped.")

    # ========================================================
    # ADD PLAYER
    # ========================================================

    def get_available_card_numbers(self):

        selected = {
            player["card_number"]
            for player in self.players.values()
            if (
                isinstance(player, dict)
                and player.get("card_number") is not None
            )
        }

        return [
            number
            for number in range(1, 301)
            if number not in selected
        ]

    def add_player(
        self,
        user_id,
        card_number=None
    ):

        # Game full.
        if len(self.players) >= MAX_PLAYERS:

            return {
                "success": False,
                "message": "Game is full"
            }

        # Do not allow joining a live game.
        if self.running:

            return {
                "success": False,
                "message": "Game is already running."
            }

        # Already joined.
        if user_id in self.players:

            player = self.players[user_id]

            return {
                "success": False,
                "message": "Already joined",
                "players": len(self.players),
                "card_number": player.get(
                    "card_number"
                ),
                "card": player.get("card")
            }

        # Card required.
        if card_number is None:

            return {
                "success": False,
                "message": "Please choose a Bingo card first."
            }

        try:
            card_number = int(card_number)

        except (
            TypeError,
            ValueError
        ):

            return {
                "success": False,
                "message": "Invalid card number."
            }

        # Only cards 1-300.
        if (
            card_number < 1
            or card_number > 300
        ):

            return {
                "success": False,
                "message": (
                    "Card number must be "
                    "between 1 and 300."
                )
            }

        # Prevent duplicate card.
        for player in self.players.values():

            if (
                isinstance(player, dict)
                and player.get(
                    "card_number"
                ) == card_number
            ):

                return {
                    "success": False,
                    "message": (
                        f"Card {card_number} "
                        "is already taken."
                    )
                }

        # Get selected card.
        card = self.card_catalog[card_number]

        self.players[user_id] = {
            "card_number": card_number,
            "card": card
        }

        print(
            f"👤 Player joined: {user_id} "
            f"with Card {card_number} "
            f"({len(self.players)} players)"
        )

        # ----------------------------------------------------
        # Start 10-second countdown at 2 players.
        # ----------------------------------------------------

        if (
            len(self.players)
            >= MIN_PLAYERS_TO_START
            and not self.running
        ):

            self.start_game()

        # Status message.
        if self.starting:

            message = (
                f"🚀 Starting in "
                f"{self.countdown} seconds..."
            )

        else:

            message = "Waiting for players..."

        return {
            "success": True,
            "message": message,
            "players": len(self.players),
            "cards": len(self.players),
            "running": self.running,
            "starting": self.starting,
            "countdown": self.countdown,
            "card_number": card_number,
            "card": card,
            "prize_pool": self.get_prize_pool()
        }

    # ========================================================
    # DRAW 75-BALL NUMBER
    # ========================================================

    def draw_number(self):

        if not self.running:
            return None

        number = self.number_manager.call_number()

        # All 75 numbers called.
        if number is None:

            print(
                "🎱 All 75 numbers have been called."
            )

            self.running = False
            self._draw_stop.set()

            return None

        self.last_number = number

        print(
            f"🎱 Called Number: "
            f"{self.format_number(number)}"
        )

        # Check players after every number.
        winner = self.check_winner()

        if winner is not None:

            print(
                f"🏆 Bingo winner detected: "
                f"{winner}"
            )

        return number

    # ========================================================
    # BINGO LETTER
    # ========================================================

    def get_bingo_letter(self, number):

        return self.number_manager.get_letter(
            number
        )

    # ========================================================
    # DISPLAY NUMBER
    # ========================================================

    def format_number(self, number):

        if number is None:
            return None

        letter = self.get_bingo_letter(
            number
        )

        if letter is None:
            return str(number)

        return f"{letter}-{number}"

    # ========================================================
    # GAME STATUS
    # ========================================================

    def get_status(self):

        if self.running:

            status = "🔴 LIVE - Number drawing"

        elif self.starting:

            status = (
                f"🚀 Starting in "
                f"{self.countdown} seconds..."
            )

        else:

            status = "⏳ Waiting for players..."

        return {
            "running": self.running,

            "starting": self.starting,

            "countdown": self.countdown,

            "status": status,

            "players": len(self.players),

            "cards": len(self.players),

            "prize_pool": self.get_prize_pool(),

            "winner_prize": (
                self.get_winner_prize()
                if self.running
                else 0
            ),

            "called_numbers":
                self.number_manager.get_called_numbers(),

            "last_number":
                self.last_number,

            "last_number_display":
                self.format_number(
                    self.last_number
                ),

            "winner":
                self.winner,

            "last_winner":
                self.last_winner,

            "last_prize":
                self.last_prize,

            "available_cards":
                self.get_available_card_numbers(),

            "called_count":
                self.number_manager.called_count(),

            "remaining_numbers":
                self.number_manager.remaining_count(),

            "game_id":
                self.game_id
        }

    # ========================================================
    # CHECK WINNER
    # ========================================================

    def check_winner(self):

        if self.winner is not None:
            return self.winner

        for user_id, card in self.players.items():

            if not card:
                continue

            if self.check_bingo(
                user_id,
                card
            ):

                return self.set_winner(
                    user_id
                )

        return None

    # ========================================================
    # CHECK BINGO CARD
    # ========================================================

    def check_bingo(
        self,
        user_id,
        card
    ):

        if user_id not in self.players:
            return False

        if (
            isinstance(card, dict)
            and "card" in card
        ):

            card = card["card"]

        if (
            not isinstance(card, list)
            or len(card) != 5
        ):

            return False

        if not all(
            isinstance(row, list)
            and len(row) == 5
            for row in card
        ):

            return False

        called = set(
            self.number_manager
            .get_called_numbers()
        )

        def marked(value):

            return (
                value == "FREE"
                or value in called
            )

        # ----------------------------------------------------
        # ROWS
        # ----------------------------------------------------

        for row in range(5):

            if all(
                marked(card[row][column])
                for column in range(5)
            ):

                print(
                    f"🏆 Bingo ROW found "
                    f"for player {user_id}"
                )

                return True

        # ----------------------------------------------------
        # COLUMNS
        # ----------------------------------------------------

        for column in range(5):

            if all(
                marked(card[row][column])
                for row in range(5)
            ):

                print(
                    f"🏆 Bingo COLUMN found "
                    f"for player {user_id}"
                )

                return True

        # ----------------------------------------------------
        # DIAGONAL
        # ----------------------------------------------------

        if all(
            marked(card[i][i])
            for i in range(5)
        ):

            print(
                f"🏆 Bingo DIAGONAL found "
                f"for player {user_id}"
            )

            return True

        # ----------------------------------------------------
        # OTHER DIAGONAL
        # ----------------------------------------------------

        if all(
            marked(card[i][4 - i])
            for i in range(5)
        ):

            print(
                f"🏆 Bingo DIAGONAL found "
                f"for player {user_id}"
            )

            return True

        # ----------------------------------------------------
        # FOUR CORNERS
        # ----------------------------------------------------

        corners = [
            card[0][0],
            card[0][4],
            card[4][0],
            card[4][4]
        ]

        if all(
            marked(value)
            for value in corners
        ):

            print(
                f"🏆 Bingo FOUR CORNERS "
                f"found for player {user_id}"
            )

            return True

        return False

    # ========================================================
    # SET WINNER + PAY WINNER
    # ========================================================

    def set_winner(self, user_id):

        # ----------------------------------------------------
        # Prevent duplicate winner processing.
        # ----------------------------------------------------

        if self.winner is not None:

            return self.winner

        self.winner = user_id

        # Stop automatic drawing.
        self.running = False
        self._draw_stop.set()

        # Calculate prize BEFORE resetting players.
        prize_pool = self.get_prize_pool()

        prize = int(
            prize_pool
            * WIN_PERCENTAGE
            / 100
        )

        # Save winner information.
        self.last_winner = user_id
        self.last_prize = prize

        print("")
        print("🏆 ===============================")
        print("🏆 BINGO WINNER!")
        print(
            f"🏆 Winner: {user_id}"
        )
        print(
            f"💰 Prize Pool: {prize_pool} ETB"
        )
        print(
            f"💰 Winner Prize: {prize} ETB"
        )
        print("🏆 ===============================")
        print("")

        # ----------------------------------------------------
        # PAY WINNER
        # ----------------------------------------------------

        if prize > 0:

            paid = add_bingo_winnings(
                telegram_id=user_id,
                amount=prize,
                game_id=self.game_id
            )

            if paid:

                print(
                    f"💰 {prize} ETB "
                    f"added to wallet of "
                    f"{user_id}"
                )

            else:

                print(
                    "⚠️ Winner payout was "
                    "already completed "
                    "or failed."
                )

        # ----------------------------------------------------
        # Reset after winner.
        #
        # Keep last_winner and last_prize so
        # the API can still show the result.
        # ----------------------------------------------------

        threading.Thread(
            target=self._finish_winner_game,
            daemon=True
        ).start()

        return user_id

    # ========================================================
    # FINISH WINNER GAME
    # ========================================================

    def _finish_winner_game(self):

        # Small delay allows the winner state to
        # be visible to the API/UI before reset.
        time.sleep(2)

        self.reset_game(
            keep_last_result=True
        )

        print(
            "🔄 Game finished."
        )

        print(
            "⏳ Waiting for players..."
        )

    # ========================================================
    # RESET GAME
    # ========================================================

    def reset_game(
        self,
        keep_last_result=False
    ):

        self._draw_stop.set()
        self._countdown_stop.set()

        self.players.clear()

        self.number_manager.reset()

        self.running = False
        self.starting = False
        self.countdown = 0
        self.winner = None
        self.last_number = None

        self.game_id = None

        if not keep_last_result:

            self.last_winner = None
            self.last_prize = 0

        print(
            "🔄 Good Bingo Game Reset."
        )

        return True
