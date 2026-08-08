import random

from config import MAX_PLAYERS
from cards import generate_card


class BingoGame:

    def __init__(self):
        self.players = {}
        self.called_numbers = []
        self.running = False
        self.winner = None
        self.last_number = None

    def start_game(self):
        self.called_numbers.clear()
        self.running = True
        self.winner = None
        self.last_number = None

        print("Good Bingo Game Started!")

    def stop_game(self):
        self.running = False

    def add_player(self, user_id, card=None):

        if len(self.players) >= MAX_PLAYERS:
            return {
                "success": False,
                "message": "Game is full"
            }

        if user_id in self.players:
            return {
                "success": False,
                "message": "Already joined",
                "card": self.players[user_id]
            }

        if card is None:
            card = generate_card()

        self.players[user_id] = card

        return {
            "success": True,
            "players": len(self.players),
            "card": card
        }

    def draw_number(self):

        if not self.running:
            return None

        available = [
            n for n in range(1, 76)
            if n not in self.called_numbers
        ]

        if not available:
            self.running = False
            return None

        number = random.choice(available)

        self.called_numbers.append(number)
        self.last_number = number

        print(f"Called Number: {number}")

        return number

    def get_status(self):

        return {
            "running": self.running,
            "players": len(self.players),
            "cards": len(self.players),
            "called_numbers": self.called_numbers,
            "last_number": self.last_number,
            "winner": self.winner
        }

    def check_winner(self):

        if self.winner is not None:
            return self.winner

        for user_id, card in self.players.items():

            if not card:
                continue

            if self.check_bingo(user_id, card):
                return self.set_winner(user_id)

        return None

    def check_bingo(self, user_id, card):

        if user_id not in self.players:
            return False

        if not isinstance(card, dict):
            return False

        called = set(self.called_numbers)

        for row in range(5):

            values = []

            for column in ["B", "I", "N", "G", "O"]:
                values.append(card[column][row])

            if all(
                value == "FREE" or value in called
                for value in values
            ):
                return True

        for column in ["B", "I", "N", "G", "O"]:

            values = card[column]

            if all(
                value == "FREE" or value in called
                for value in values
            ):
                return True

        diagonal_1 = [
            card["B"][0],
            card["I"][1],
            card["N"][2],
            card["G"][3],
            card["O"][4]
        ]

        if all(
            value == "FREE" or value in called
            for value in diagonal_1
        ):
            return True

        diagonal_2 = [
            card["O"][0],
            card["G"][1],
            card["N"][2],
            card["I"][3],
            card["B"][4]
        ]

        if all(
            value == "FREE" or value in called
            for value in diagonal_2
        ):
            return True

        return False

    def set_winner(self, user_id):

        self.winner = user_id
        self.running = False

        print(f"Winner: {user_id}")

        return user_id
