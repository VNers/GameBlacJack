import json
import pygame
import random
from constants import CARD_IMAGES, RANKS, SUITS
from player import Player, generate_random_name


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Blackjack Game")
        self.font = pygame.font.Font(None, 28)

        self.deck = [f"{rank}_of_{suit}" for rank in RANKS for suit in SUITS]
        random.shuffle(self.deck)

        self.load_player_data()
        self.player = Player("Player")
        self.dealer = Player("Dealer", is_dealer=True)
        self.bots = [Player(generate_random_name(), is_bot=True) for _ in range(3)]
        self.players = [self.player, self.dealer] + self.bots

        self.game_over = False
        self.messages = []

        self.buttons = {
            "hit": pygame.Rect(700, 450, 100, 50),
            "stand": pygame.Rect(700, 500, 100, 50),
            "bet": pygame.Rect(700, 550, 100, 50),
            "new_game": pygame.Rect(600, 450, 100, 50)
        }

    def load_player_data(self):
        try:
            with open('player_data.json', 'r') as file:
                data = file.read().strip()
                if not data:
                    raise FileNotFoundError("File is empty")
                player_data = json.loads(data)
                self.player = Player(player_data['player']['name'], balance=player_data['player']['balance'],
                                     stats=player_data['player'].get('stats', {}))
                self.dealer = Player(player_data['dealer']['name'], balance=player_data['dealer']['balance'],
                                     is_dealer=True)
                self.bots = [Player(bot['name'], balance=bot['balance'], stats=bot.get('stats', {}), is_bot=True) for
                             bot in player_data['bots']]
                self.players = [self.player, self.dealer] + self.bots
        except (FileNotFoundError, json.JSONDecodeError):
            self.player = Player("Player")
            self.dealer = Player("Dealer", is_dealer=True)
            self.bots = [Player(generate_random_name(), is_bot=True) for _ in range(3)]
            self.players = [self.player, self.dealer] + self.bots

    def save_player_data(self):
        player_data = {
            'player': {'name': self.player.name, 'balance': self.player.balance, 'stats': self.player.stats},
            'dealer': {'name': self.dealer.name, 'balance': self.dealer.balance},
            'bots': [{'name': bot.name, 'balance': bot.balance, 'stats': bot.stats} for bot in self.bots]
        }
        with open('player_data.json', 'w') as file:
            json.dump(player_data, file, indent=4)

    def start_game(self):
        self.new_round()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.screen.fill((192, 192, 192))

            self.draw_game(self.screen)
            self.draw_messages()
            self.save_player_data()
            pygame.display.flip()

        pygame.quit()

    def new_round(self):
        if len(self.deck) < 5:
            self.deck = [f"{rank}_of_{suit}" for rank in RANKS for suit in SUITS]
            random.shuffle(self.deck)

        for player in self.players:
            if len(self.deck) >= 2:
                player.hand = [self.deck.pop(), self.deck.pop()]
            else:
                player.hand = []

        if len(self.deck) >= 2:
            self.dealer.hand = [self.deck.pop(), self.deck.pop()]
            self.dealer.hidden_card = self.dealer.hand[0]
        else:
            self.dealer.hand = []
            self.dealer.hidden_card = None

        self.game_over = False
        self.messages = []

        for player in self.players:
            if player.is_bot:
                bot_bet = self.generate_bot_bet()
                player.place_bet(bot_bet)
                self.dealer.balance += bot_bet

        self.dealer.balance = 0

        self.handle_bots_bet(100)
        self.handle_player_bet(100)

    def draw_game(self, screen):
        positions = [(50, 50), (450, 50), (50, 250), (450, 250)]
        for i, player in enumerate(self.players):
            if i >= len(positions):
                break
            self.draw_player(screen, player, positions[i][0], positions[i][1])
        self.draw_buttons(screen)
        self.draw_balance(screen)

    def draw_player(self, screen, player, x, y):
        if player.is_dealer:
            if not self.game_over:
                card_image = CARD_IMAGES["back_of_card.png"]
                screen.blit(card_image, (x, y))
                if len(player.hand) > 1:
                    for i in range(1, len(player.hand)):
                        card_image = CARD_IMAGES[player.hand[i]]
                        screen.blit(card_image, (x + i * 80, y))
            else:
                for i in range(len(player.hand)):
                    card_image = CARD_IMAGES[player.hand[i]]
                    screen.blit(card_image, (x + i * 80, y))
        else:
            for i, card in enumerate(player.hand):
                card_image = CARD_IMAGES[card]
                screen.blit(card_image, (x + i * 80, y))

            if not player.is_dealer:
                bank_text = self.font.render(f"Bank: ${player.balance}", True, (255, 255, 255))
                bet_text = self.font.render(f"Bet: ${player.bet}", True, (255, 255, 255))
                screen.blit(bank_text, (x, y + 120))
                screen.blit(bet_text, (x, y + 140))

        hand_value = self.calculate_hand_value(player.hand)
        value_text = self.font.render(f"{player.name} Hand Value: {hand_value}", True, (255, 255, 255))
        screen.blit(value_text, (x, y + 100))

    def draw_buttons(self, screen):
        button_width, button_height = 100, 50
        button_margin = 10
        button_start_x = (self.screen.get_width() - (
                button_width * len(self.buttons) + button_margin * (len(self.buttons) - 1))) // 2
        button_y = 450

        for i, (name, rect) in enumerate(self.buttons.items()):
            rect.x = button_start_x + i * (button_width + button_margin)
            rect.y = button_y
            pygame.draw.rect(screen, (100, 100, 100), rect)
            text = self.font.render(name.capitalize(), True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

    def draw_balance(self, screen):
        player_balance_text = self.font.render(f"Player Balance: ${self.player.balance}", True, (255, 255, 255))
        dealer_balance_text = self.font.render(f"Dealer Bank: ${self.dealer.balance}", True, (255, 255, 255))
        screen.blit(player_balance_text, (20, 20))
        screen.blit(dealer_balance_text, (600, 20))

    def draw_messages(self):
        message_y = 300
        for message in self.messages:
            message_text = self.font.render(message, True, (255, 0, 0))
            text_rect = message_text.get_rect(center=(self.screen.get_width() // 2, message_y))
            self.screen.blit(message_text, text_rect)
            message_y += 30

    def handle_click(self, pos):
        if self.buttons["hit"].collidepoint(pos):
            self.player.hand.append(self.deck.pop())
            if self.calculate_hand_value(self.player.hand) > 21:
                self.game_over = True
        elif self.buttons["stand"].collidepoint(pos):
            while self.calculate_hand_value(self.dealer.hand) < 17:
                self.dealer.hand.append(self.deck.pop())
            self.game_over = True
        elif self.buttons["bet"].collidepoint(pos):
            self.handle_bet(100)
        elif self.buttons["new_game"].collidepoint(pos):
            self.new_round()
            self.game_over = False

        if self.game_over:
            self.resolve_round()

    def handle_player_bet(self, amount):
        if self.player.balance >= amount:
            self.player.place_bet(amount)
            self.dealer.balance += amount

    def handle_bet(self, amount):
        if self.player.balance >= amount:
            self.player.place_bet(amount)
            self.dealer.balance += amount

        for player in self.players:
            if player != self.player and not player.is_dealer and player.is_bot:
                bot_bet = self.generate_bot_bet()
                player.place_bet(bot_bet)
                self.dealer.balance += bot_bet

    def handle_bots_bet(self, amount):
        for player in self.players:
            if player != self.player and not player.is_dealer and player.is_bot:
                bot_bet = self.generate_bot_bet()
                player.place_bet(bot_bet)
                self.dealer.balance += bot_bet

    @staticmethod
    def generate_bot_bet():
        min_bet = 100
        max_bet = 1000
        step = 100
        return random.randint(min_bet // step, max_bet // step) * step

    @staticmethod
    def calculate_hand_value(hand):
        value = 0
        num_aces = 0
        for card in hand:
            if card == "back_of_card.png":
                continue

            rank = card.split("_")[0]
            if rank in ["jack", "queen", "king"]:
                value += 10
            elif rank == "ace":
                num_aces += 1
                value += 11
            else:
                value += int(rank)

        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1

        return value

    def resolve_round(self):
        dealer_blackjack = self.calculate_hand_value(self.dealer.hand) == 21
        dealer_bust = False

        while self.calculate_hand_value(self.dealer.hand) < 17:
            self.dealer.hand.append(self.deck.pop())
            if self.calculate_hand_value(self.dealer.hand) > 21:
                dealer_bust = True
                break

        for player in self.players:
            if isinstance(player, Player) and not player.is_dealer:
                while self.calculate_hand_value(player.hand) < 19:
                    player.hand.append(self.deck.pop())

        for player in self.players:
            if isinstance(player, Player) and player.is_bot:
                while self.calculate_hand_value(player.hand) < 19:
                    player.hand.append(self.deck.pop())

        for player in self.players:
            if isinstance(player, Player) and not player.is_dealer:
                self.check_winner(player, dealer_blackjack, dealer_bust)

    def check_winner(self, player, dealer_blackjack, dealer_bust):
        player_blackjack = self.calculate_hand_value(player.hand) == 21

        if player_blackjack and not dealer_blackjack:
            player.balance += player.bet * 1.5
            self.dealer.balance -= player.bet * 1.5
            self.messages.append(f"{player.name} has Blackjack and wins! Bank: ${player.balance}, Bet: ${player.bet}")
        elif player_blackjack and dealer_blackjack:
            self.messages.append(
                f"{player.name} and dealer have Blackjack! It's a push. Bank: ${player.balance}, Bet: ${player.bet}")
        elif self.calculate_hand_value(player.hand) > 21:
            self.messages.append(f"{player.name} busted! Dealer wins! Bank: ${player.balance}, Bet: ${player.bet}")
        elif dealer_bust:
            player.balance += player.bet * 1.5
            self.dealer.balance -= player.bet * 1.5
            self.messages.append(f"Dealer busted! {player.name} wins! Bank: ${player.balance}, Bet: ${player.bet}")
        elif self.calculate_hand_value(player.hand) > self.calculate_hand_value(self.dealer.hand):
            player.balance += player.bet * 1.5
            self.dealer.balance -= player.bet * 1.5
            self.messages.append(f"{player.name} wins! Bank: ${player.balance}, Bet: ${player.bet}")
        elif self.calculate_hand_value(player.hand) < self.calculate_hand_value(self.dealer.hand):
            self.messages.append(f"Dealer wins! Bank: ${player.balance}, Bet: ${player.bet}")
        else:
            self.messages.append(f"It's a push! Bank: ${player.balance}, Bet: ${player.bet}")

        player.bet = 0

    def display_message(self, message):
        self.messages.append(message)


if __name__ == "__main__":
    game = Game()
    game.start_game()
