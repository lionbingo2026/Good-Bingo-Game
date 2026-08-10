# cartela.py

import random


# ============================================================
# GOOD BINGO GAME
# 75-BALL BINGO CARD
# ============================================================


BINGO_COLUMNS = {
    "B": range(1, 16),
    "I": range(16, 31),
    "N": range(31, 46),
    "G": range(46, 61),
    "O": range(61, 76),
}


# ============================================================
# GENERATE CARD
# ============================================================

def generate_card():
    """
    Generate a standard 75-ball Bingo card.

    B = 1-15
    I = 16-30
    N = 31-45
    G = 46-60
    O = 61-75

    The center position is FREE.
    """

    columns = {}

    # Generate 5 unique numbers for each column.
    for letter, number_range in BINGO_COLUMNS.items():
        columns[letter] = random.sample(
            list(number_range),
            5
        )

    # Convert columns into 5 rows.
    card = []

    for row in range(5):

        current_row = []

        for column_index, letter in enumerate(
            ["B", "I", "N", "G", "O"]
        ):

            # Center position.
            if row == 2 and column_index == 2:
                current_row.append("FREE")

            else:
                current_row.append(
                    columns[letter][row]
                )

        card.append(current_row)

    return card


# ============================================================
# FORMAT CARD
# ============================================================

def format_card(card):
    """
    Convert a Bingo card into readable text.
    """

    if not isinstance(card, list):
        return ""

    lines = [
        " B   I   N   G   O",
        "-------------------"
    ]

    for row in card:

        values = []

        for value in row:

            if value == "FREE":
                values.append(" F ")

            else:
                values.append(
                    f"{value:2}"
                )

        lines.append(
            " | ".join(values)
        )

    return "\n".join(lines)


# ============================================================
# VALIDATE CARD
# ============================================================

def validate_card(card):
    """
    Validate a 5x5 75-ball Bingo card.

    Returns True if the card is valid.
    """

    if not isinstance(card, list):
        return False

    if len(card) != 5:
        return False

    for row in card:

        if not isinstance(row, list):
            return False

        if len(row) != 5:
            return False

    # Center must be FREE.
    if card[2][2] != "FREE":
        return False

    # Validate B column.
    for number in card[0:5]:

        pass

    expected_ranges = [
        range(1, 16),    # B
        range(16, 31),   # I
        range(31, 46),   # N
        range(46, 61),   # G
        range(61, 76),   # O
    ]

    for column_index, number_range in enumerate(
        expected_ranges
    ):

        values = []

        for row in range(5):

            value = card[row][column_index]

            # Center is FREE.
            if row == 2 and column_index == 2:

                if value != "FREE":
                    return False

                continue

            if not isinstance(value, int):
                return False

            if value not in number_range:
                return False

            values.append(value)

        # No duplicate numbers in a column.
        if len(values) != len(set(values)):
            return False

    return True


# ============================================================
# CREATE AND FORMAT CARD
# ============================================================

if __name__ == "__main__":

    card = generate_card()

    print("🎱 Good Bingo Game")
    print("75-Ball Bingo")
    print()

    print(format_card(card))
    print()

    print(
        "Card valid:",
        validate_card(card)
    )
