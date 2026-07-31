import random


def generate_card():

    card = {
        "B": random.sample(range(1, 16), 5),
        "I": random.sample(range(16, 31), 5),
        "N": random.sample(range(31, 46), 5),
        "G": random.sample(range(46, 61), 5),
        "O": random.sample(range(61, 76), 5)
    }

    # Free center square
    card["N"][2] = "FREE"

    return card


def card_to_text(card):

    text = "🎲 GOOD BINGO GAME\n\n"
    text += " B     I     N     G     O\n"
    text += "--------------------------\n"

    for row in range(5):
        line = ""

        for column in ["B", "I", "N", "G", "O"]:
            line += f"{str(card[column][row]):^7}"

        text += line + "\n"

    return text


if __name__ == "__main__":
    print(card_to_text(generate_card()))
