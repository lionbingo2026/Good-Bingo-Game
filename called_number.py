# called_number.py

import random


class CalledNumberManager:
    """
    Manages the 75 Bingo numbers.

    B = 1-15
    I = 16-30
    N = 31-45
    G = 46-60
    O = 61-75
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Start a new Bingo number sequence."""
        self.available_numbers = list(range(1, 76))
        self.called_numbers = []

    def call_number(self):
        """
        Call one unused Bingo number.

        Returns:
            int | None: The called number, or None if all
            75 numbers have already been called.
        """
        if not self.available_numbers:
            return None

        number = random.choice(self.available_numbers)

        self.available_numbers.remove(number)
        self.called_numbers.append(number)

        return number

    def get_called_numbers(self):
        """Return all numbers that have been called."""
        return list(self.called_numbers)

    def get_last_number(self):
        """Return the most recently called number."""
        if not self.called_numbers:
            return None

        return self.called_numbers[-1]

    def is_called(self, number):
        """Return True if a number has already been called."""
        try:
            number = int(number)
        except (TypeError, ValueError):
            return False

        return number in self.called_numbers

    def remaining_count(self):
        """Return how many Bingo numbers remain."""
        return len(self.available_numbers)

    def called_count(self):
        """Return how many numbers have been called."""
        return len(self.called_numbers)

    @staticmethod
    def get_letter(number):
        """Return the Bingo column letter for a number."""

        try:
            number = int(number)
        except (TypeError, ValueError):
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

    def get_called_labels(self):
        """
        Return called numbers with Bingo letters.

        Example:
            ['B-7', 'I-22', 'N-35']
        """
        return [
            f"{self.get_letter(number)}-{number}"
            for number in self.called_numbers
        ]

    def get_state(self):
        """
        Return the current caller state.

        Useful for the Good Bingo Game Flask API
        and Telegram Mini App.
        """
        return {
            "called_numbers": self.get_called_numbers(),
            "last_number": self.get_last_number(),
            "called_count": self.called_count(),
            "remaining": self.remaining_count(),
            "running": bool(self.available_numbers),
        }


# Optional standalone test
if __name__ == "__main__":
    caller = CalledNumberManager()

    print("🎱 Good Bingo Game")
    print("75-Ball Bingo")
    print()

    for _ in range(5):
        number = caller.call_number()
        letter = caller.get_letter(number)
        print(f"Called: {letter}-{number}")

    print()
    print("Called numbers:", caller.get_called_numbers())
    print("Last number:", caller.get_last_number())
    print("Called count:", caller.called_count())
    print("Remaining:", caller.remaining_count())
