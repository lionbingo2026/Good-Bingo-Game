import random
from config import MAX_PLAYERS


class BingoGame:

    def __init__(self):
        self.players = {}
        self.called_numbers = []
        self.running = False
        self.winner = None
        self.last_number = None


    def start_game(self):
        self.players.clear()
        self.called_numbers.clear()
        self.running = True
        self.winner = None
        self.last_number = None

        print("🎲 Good Bingo Game Started!")


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
                "message": "Already joined"
            }

        self.players[user_id] = card or {}

        return {
            "success": True,
            "players": len(self.players)
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

        print(f"🎱 Called Number: {number}")

        return number


    def check_winner(self):

        for user_id, card in self.players.items():

            if not card:
                continue

            grid = list(card.values())

            return self.set_winner(user_id)

        return None


    def set_winner(self, user_id):

        self.winner = user_id
        self.running = False

        print(f"🏆 Winner: {user_id}")

        return user_id


    def get_status(self):

        return {
            "running": self.running,
            "players": len(self.players),
            "called_numbers": self.called_numbers,
            "last_number": self.last_number,
            "winner": self.winner
        }




