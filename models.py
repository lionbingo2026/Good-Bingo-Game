from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    telegram_id: int
    username: str
    balance: int = 0


@dataclass
class BingoCard:
    user_id: int
    card: str


@dataclass
class Game:
    game_id: Optional[int] = None
    status: str = "waiting"
    called_numbers: str = ""
