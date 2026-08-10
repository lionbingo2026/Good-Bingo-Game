# game.py

from config import MAX_PLAYERS
from called_number import CalledNumberManager
from cartela import generate_card


# ============================================================
# GOOD BINGO GAME
# 75-BALL BINGO
# ============================================================

MIN_PLAYERS_TO_START = 2


class BingoGame:

    def __init__(self):
        self.players = {}

        # 300 selectable Bingo cards.
        # Each card number gets its own generated 75-ball card.
        self.card_catalog = {
            number: generate_card()
            for number in range(1, 301)
        }

        # One 75-ball number manager for this game.
        self.number_manager = CalledNumberManager()

        self.running = False
        self.winner = None
        self.last_number = None

    # ========================================================
    # CALLED NUMBERS COMPATIBILITY
    # ========================================================

    @property
    def called_numbers(self):
        """
        Keep compatibility with existing app.py and bot.py.

        The actual numbers are stored by CalledNumberManager.
        """
        return self.number_manager.called_numbers

    # ========================================================
    # START GAME
    # ========================================================

    def start_game(self):

        if len(self.players) < MIN_PLAYERS_TO_START:
            print(
                f"Waiting for players: "
                f"{len(self.players)}/{MIN_PLAYERS_TO_START}"
            )
            return False

        # Start a fresh 75-ball sequence.
        self.number_manager.reset()

        self.running = True
        self.winner = None
        self.last_number = None

        print("🎱 Good Bingo Game Started!")
        print(
            f"👥 Players: {len(self.players)}"
        )

        return True

    # ========================================================
    # STOP GAME
    # ========================================================

    def stop_game(self):

        self.running = False

        print("🛑 Good Bingo Game Stopped.")

    # ========================================================
    # ADD PLAYER
    # ========================================================

    def get_available_card_numbers(self):
        """Return card numbers that are still available."""

        selected = {
            player["card_number"]
            for player in self.players.values()
            if isinstance(player, dict)
            and player.get("card_number") is not None
        }

        return [
            number
            for number in range(1, 301)
            if number not in selected
        ]

    def add_player(self, user_id, card_number=None):

        # Game full
        if len(self.players) >= MAX_PLAYERS:
            return {
                "success": False,
                "message": "Game is full"
            }

        # Already joined
        if user_id in self.players:
            player = self.players[user_id]

            return {
                "success": False,
                "message": "Already joined",
                "players": len(self.players),
                "card_number": player.get("card_number"),
                "card": player.get("card")
            }

        # Card selection is required.
        if card_number is None:
            return {
                "success": False,
                "message": "Please choose a Bingo card first."
            }

        try:
            card_number = int(card_number)
        except (TypeError, ValueError):
            return {
                "success": False,
                "message": "Invalid card number."
            }

        # Only cards 1-300 are allowed.
        if card_number < 1 or card_number > 300:
            return {
                "success": False,
                "message": "Card number must be between 1 and 300."
            }

        # Prevent duplicate card selection.
        for player in self.players.values():

            if (
                isinstance(player, dict)
                and player.get("card_number") == card_number
            ):
                return {
                    "success": False,
                    "message": f"Card {card_number} is already taken."
                }

        # Get the actual card belonging to this number.
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

        # Automatically start at 2 players.
        if (
            len(self.players) >= MIN_PLAYERS_TO_START
            and not self.running
        ):
            self.start_game()

        return {
            "success": True,
            "players": len(self.players),
            "cards": len(self.players),
            "running": self.running,
            "card_number": card_number,
            "card": card
        }

    # ========================================================
    # DRAW 75-BALL NUMBER
    # ========================================================

    def draw_number(self):

        # Game not running.
        if not self.running:
            return None

        # Use CalledNumberManager.
        number = self.number_manager.call_number()

        # All 75 numbers have been called.
        if number is None:

            print("🎱 All 75 numbers have been called.")

            self.running = False

            return None

        self.last_number = number

        print(
            f"🎱 Called Number: "
            f"{self.format_number(number)}"
        )

        # Check all players immediately after each number.
        winner = self.check_winner()

        if winner is not None:
            print(
                f"🏆 Bingo winner detected: {winner}"
            )

        return number

    # ========================================================
    # BINGO LETTER
    # ========================================================

    def get_bingo_letter(self, number):

        return self.number_manager.get_letter(number)

    # ========================================================
    # DISPLAY NUMBER
    # ========================================================

    def format_number(self, number):

        if number is None:
            return None

        letter = self.get_bingo_letter(number)

        if letter is None:
            return str(number)

        return f"{letter}-{number}"

    # ========================================================
    # GAME STATUS
    # ========================================================

    def get_status(self):

        return {
            "running": self.running,
            "players": len(self.players),
            "cards": len(self.players),
            "called_numbers": self.number_manager.get_called_numbers(),
            "last_number": self.last_number,
            "last_number_display": self.format_number(
                self.last_number
            ),
            "winner": self.winner,
            "available_cards": self.get_available_card_numbers(),
            "called_count": self.number_manager.called_count(),
            "remaining_numbers": self.number_manager.remaining_count()
        }

    # ========================================================
    # CHECK WINNER
    # ========================================================

    def check_winner(self):

        # Winner already found.
        if self.winner is not None:
            return self.winner

        # Check every player.
        for user_id, card in self.players.items():

            if not card:
                continue

            if self.check_bingo(user_id, card):
                return self.set_winner(user_id)

        return None

    # ========================================================
    # CHECK BINGO CARD
    # ========================================================

    def check_bingo(self, user_id, card):

        if user_id not in self.players:
            return False

        if not isinstance(card, dict):
            return False

        required_columns = [
            "B",
            "I",
            "N",
            "G",
            "O"
        ]

        # Make sure card has all columns.
        for column in required_columns:

            if column not in card:
                return False

            if not isinstance(card[column], list):
                return False

            if len(card[column]) != 5:
                return False

        called = set(
            self.number_manager.get_called_numbers()
        )

        # ====================================================
        # CHECK ROWS
        # ====================================================

        for row in range(5):

            values = []

            for column in required_columns:
                values.append(
                    card[column][row]
                )

            if all(
                value == "FREE"
                or value in called
                for value in values
            ):
                print(
                    f"🏆 Bingo row found for player {user_id}"
                )

                return True

        # ====================================================
        # CHECK COLUMNS
        # ====================================================

        for column in required_columns:

            values = card[column]

            if all(
                value == "FREE"
                or value in called
                for value in values
            ):
                print(
                    f"🏆 Bingo column found for player {user_id}"
                )

                return True

        # ====================================================
        # CHECK DIAGONAL 1
        # ====================================================

        diagonal_1 = [
            card["B"][0],
            card["I"][1],
            card["N"][2],
            card["G"][3],
            card["O"][4]
        ]

        if all(
            value == "FREE"
            or value in called
            for value in diagonal_1
        ):
            print(
                f"🏆 Bingo diagonal found for player {user_id}"
            )

            return True

        # ====================================================
        # CHECK DIAGONAL 2
        # ====================================================

        diagonal_2 = [
            card["O"][0],
            card["G"][1],
            card["N"][2],
            card["I"][3],
            card["B"][4]
        ]

        if all(
            value == "FREE"
            or value in called
            for value in diagonal_2
        ):
            print(
                f"🏆 Bingo diagonal found for player {user_id}"
            )

            return True

        return False

    # ========================================================
    # SET WINNER
    # ========================================================

    def set_winner(self, user_id):

        self.winner = user_id
        self.running = False

        print(
            f"🏆 WINNER: {user_id}"
        )

        return user_id

    # ========================================================
    # RESET GAME
    # ========================================================

    def reset_game(self):

        self.players.clear()

        self.number_manager.reset()

        self.running = False
        self.winner = None
        self.last_number = None

        print("🔄 Good Bingo Game Reset.")

        return True
