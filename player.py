import random
from constants import FIRST_NAMES, LAST_NAMES


def generate_random_name():
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return f"{first_name} {last_name}"


def get_player_name():
    name = input("Please enter your name: ")
    if not name:
        name = "Player"
    return name


class Player:
    def __init__(self, name, balance=1000, is_dealer=False, is_bot=False, stats=None):
        self.name = name
        self.hand = []
        self.hidden_card = None
        self.is_dealer = is_dealer
        self.balance = balance
        self.bet = 0
        self.is_bot = is_bot
        self.wins = 0
        self.losses = 0
        self.player_score = 0
        self.stats = stats or {}

    def place_bet(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.bet += amount
        else:
            print(f"{self.name} doesn't have enough balance to place a bet.")

    def increase_balance(self, amount):
        self.balance += amount

    def clear_hand(self):
        self.hand = []
        self.hidden_card = None
        self.player_score = 0

    def update_player_score(self, new_score):
        self.player_score = new_score


# Приклад використання:


class Bot(Player):
    def __init__(self, name):
        super().__init__(name, is_bot=True)

    def make_decision(self):
        pass

    def clear_bot_data(self):
        self.clear_hand()
        self.bet = 0


class Dealer(Player):
    def __init__(self, name="Dealer"):
        super().__init__(name, is_dealer=True)

    def flip_hidden_card(self):
        self.hidden_card = None
