import random

from config import MAX_PLAYERS
from cards import generate_card


# ============================================================
# GOOD BINGO GAME
# 75-BALL BINGO
# ============================================================

MIN_PLAYERS_TO_START = 2


class BingoGame:

    def __init__(self):
        self.players = {}
        self.called_numbers = []
        self.running = False
        self.winner = None
        self.last_number = None

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

        self.called_numbers.clear()
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

    def add_player(self, user_id, card=None):

        # Game full
        if len(self.players) >= MAX_PLAYERS:
            return {
                "success": False,
                "message": "Game is full"
            }

        # Already joined
        if user_id in self.players:
            return {
                "success": False,
                "message": "Already joined",
                "players": len(self.players),
                "card": self.players[user_id]
            }

        # Generate card automatically
        if card is None:
            card = generate_card()

        self.players[user_id] = card

        print(
            f"👤 Player joined: {user_id} "
            f"({len(self.players)} players)"
        )

        # ====================================================
        # AUTOMATICALLY START AT 2 PLAYERS
        # ====================================================

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
            "card": card
        }

    # ========================================================
    # DRAW RANDOM 75-BALL NUMBER
    # ========================================================

    def draw_number(self):

        # Game not running
        if not self.running:
            return None

        # All 75 numbers already called
        available = [
            number
            for number in range(1, 76)
            if number not in self.called_numbers
        ]

        if not available:

            print("🎱 All 75 numbers have been called.")

            self.running = False

            return None

        # Draw random number
        number = random.choice(available)

        # Save number
        self.called_numbers.append(number)

        self.last_number = number

        print(
            f"🎱 Called Number: {number}"
        )

        return number

    # ========================================================
    # BINGO LETTER
    # ========================================================

    def get_bingo_letter(self, number):

        if number is None:
            return None

        if 1 <= number <= 15:
            return "B"

        if 16 <= number <= 30:
            return "I"

        if 31 <= number <= 45:
            return "N"

        if 46 <= number <= 60:
            return "G"

        if 61 <= number <= 75:
            return "O"

        return None

    # ========================================================
    # DISPLAY NUMBER
    # ========================================================

    def format_number(self, number):

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
            "called_numbers": self.called_numbers,
            "last_number": self.last_number,
            "last_number_display": self.format_number(
                self.last_number
            ),
            "winner": self.winner
        }

    # ========================================================
    # CHECK WINNER
    # ========================================================

    def check_winner(self):

        # Winner already found
        if self.winner is not None:
            return self.winner

        # Check every player
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

        # Make sure card has all columns
        for column in required_columns:

            if column not in card:
                return False

            if not isinstance(card[column], list):
                return False

            if len(card[column]) != 5:
                return False

        called = set(self.called_numbers)

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
        self.called_numbers.clear()

        self.running = False
        self.winner = None
        self.last_number = None

        print("🔄 Good Bingo Game Reset.")

        return True
