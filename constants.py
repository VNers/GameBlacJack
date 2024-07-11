import pygame
import os

CARD_IMAGES = {}
SUITS = ["clubs", "diamonds", "hearts", "spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "ace", "jack", "queen", "king"]
CARD_WIDTH, CARD_HEIGHT = 68, 90

for rank in RANKS:
    for suit in SUITS:
        card_name = f"{rank}_of_{suit}"
        card_image = pygame.image.load(os.path.join("images", f"{card_name}.png"))
        card_image = pygame.transform.scale(card_image, (CARD_WIDTH, CARD_HEIGHT))
        CARD_IMAGES[card_name] = card_image


card_back_image = pygame.image.load(os.path.join("images", "back_of_card.png"))
card_back_image = pygame.transform.scale(card_back_image, (CARD_WIDTH, CARD_HEIGHT))
CARD_IMAGES["back_of_card.png"] = card_back_image

FIRST_NAMES = ["Alice", "Bob", "Charlie", "Dave", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jack"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]