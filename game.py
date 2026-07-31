import random
import time
from config import DRAW_INTERVAL, MAX_PLAYERS


class BingoGame:

    def __init__(self):
        self.players = {}
        self.called_numbers = []
        self.running = False
        self.winner = None


    def start_game(self):
        self.players = {}
        self.called_numbers = []
        self.running = True
        self.winner = None
        print("🎲 Good Bingo Game Started!")


    def add_player(self, user_id, card):
        if len(self.players) >= MAX_PLAYERS:
            return False

        self.players[user_id] = card
        return True


    def draw_number(self):
        numbers = [
            n for n in range(1, 76)
            if n not in self.called_numbers
        ]

        if not numbers:
            self.running = False
            return None

        number = random.choice(numbers)
        self.called_numbers.append(number)

        print(f"🎱 Number: {number}")

        return number


    def check_winner(self):
        for user_id, card in self.players.items():

            count = 0

            for column in card.values():
                for value in column:

                    if value == "FREE":
                        continue

                    if value in self.called_numbers:
                        count += 1

            if count >= 24:
                self.winner = user_id
                self.running = False
                return user_id

        return None


if __name__ == "__main__":

    game = BingoGame()
    game.start_game()

    for i in range(10):
        game.draw_number()
        time.sleep(1)
