"""
Blackjack - Casino Style Card Game
===================================
A fun and visually appealing blackjack game with casino effects.
"""

import pygame
import random
import math

# Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BRIGHT_GOLD = (255, 223, 0)
RED = (220, 20, 60)
GREEN = (0, 128, 0)
DARK_GREEN = (0, 80, 0)
FELT_GREEN = (35, 101, 51)
CASINO_RED = (139, 0, 0)
DEEP_PURPLE = (75, 0, 130)
CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 16, 240)
ORANGE = (255, 165, 0)

# Card constants
CARD_WIDTH = 70
CARD_HEIGHT = 100
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

# Game states
STATE_BETTING = 0
STATE_PLAYING = 1
STATE_DEALER_TURN = 2
STATE_GAME_OVER = 3


# =============================================================================
# SUIT DRAWING FUNCTIONS
# =============================================================================

def draw_heart(surface, x, y, size, color):
    """Draw a heart symbol at (x, y) with given size."""
    points = []
    for i in range(360):
        angle = math.radians(i)
        hx = size * (16 * math.sin(angle) ** 3)
        hy = -size * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        points.append((x + hx, y + hy))
    if len(points) > 2:
        pygame.draw.polygon(surface, color, points)


def draw_diamond(surface, x, y, size, color):
    """Draw a diamond symbol at (x, y) with given size."""
    points = [
        (x, y - size * 12),
        (x + size * 8, y),
        (x, y + size * 12),
        (x - size * 8, y)
    ]
    pygame.draw.polygon(surface, color, points)


def draw_spade(surface, x, y, size, color):
    """Draw a spade symbol at (x, y) with given size."""
    # Draw inverted heart shape for top of spade
    points = []
    for i in range(360):
        angle = math.radians(i)
        hx = size * (16 * math.sin(angle) ** 3)
        hy = size * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        points.append((x + hx, y - size * 5 + hy))
    if len(points) > 2:
        pygame.draw.polygon(surface, color, points)
    # Draw stem
    stem_points = [
        (x - size * 3, y + size * 8),
        (x + size * 3, y + size * 8),
        (x + size * 2, y + size * 2),
        (x - size * 2, y + size * 2)
    ]
    pygame.draw.polygon(surface, color, stem_points)


def draw_club(surface, x, y, size, color):
    """Draw a club symbol at (x, y) with given size."""
    # Three circles for club
    radius = int(size * 6)
    pygame.draw.circle(surface, color, (int(x), int(y - size * 6)), radius)
    pygame.draw.circle(surface, color, (int(x - size * 6), int(y + size * 2)), radius)
    pygame.draw.circle(surface, color, (int(x + size * 6), int(y + size * 2)), radius)
    # Stem
    stem_points = [
        (x - size * 3, y + size * 10),
        (x + size * 3, y + size * 10),
        (x + size * 2, y + size * 2),
        (x - size * 2, y + size * 2)
    ]
    pygame.draw.polygon(surface, color, stem_points)


def draw_suit_icon(surface, suit, x, y, size, color):
    """Draw the appropriate suit icon."""
    if suit == '♥':
        draw_heart(surface, x, y, size, color)
    elif suit == '♦':
        draw_diamond(surface, x, y, size, color)
    elif suit == '♠':
        draw_spade(surface, x, y, size, color)
    elif suit == '♣':
        draw_club(surface, x, y, size, color)


class CasinoFloater:
    """Floating casino elements like chips, cards, dice"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1, -0.3)
        self.type = random.choice(["chip", "spade", "heart", "diamond", "club"])
        self.size = random.randint(12, 25)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.alpha = random.randint(20, 60)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        
        if self.y < -50:
            self.y = self.height + 50
            self.x = random.randint(0, self.width)
        if self.x < -50:
            self.x = self.width + 50
        elif self.x > self.width + 50:
            self.x = -50
    
    def draw(self, screen):
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        if self.type == "chip":
            pygame.draw.circle(surf, (255, 0, 0, self.alpha), (self.size, self.size), self.size)
            pygame.draw.circle(surf, (255, 255, 255, self.alpha), (self.size, self.size), self.size, 2)
        elif self.type == "spade":
            color = (255, 255, 255, self.alpha)
            points = [(self.size, self.size - 8), (self.size - 6, self.size + 4), (self.size + 6, self.size + 4)]
            pygame.draw.polygon(surf, color, points)
        elif self.type == "heart":
            color = (255, 20, 60, self.alpha)
            pygame.draw.circle(surf, color, (self.size - 4, self.size - 2), 5)
            pygame.draw.circle(surf, color, (self.size + 4, self.size - 2), 5)
        elif self.type == "diamond":
            color = (255, 20, 60, self.alpha)
            points = [(self.size, self.size - 8), (self.size - 6, self.size), 
                      (self.size, self.size + 8), (self.size + 6, self.size)]
            pygame.draw.polygon(surf, color, points)
        elif self.type == "club":
            color = (255, 255, 255, self.alpha)
            pygame.draw.circle(surf, color, (self.size, self.size - 4), 5)
            pygame.draw.circle(surf, color, (self.size - 5, self.size + 2), 5)
            pygame.draw.circle(surf, color, (self.size + 5, self.size + 2), 5)
        
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class GoldenSparkle:
    """Small golden sparkle particles"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.5, 0.5)
        self.lifetime = random.randint(60, 180)
        self.age = 0
        self.max_brightness = random.randint(150, 255)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.age += 1
        
        if self.x < 0:
            self.x = self.width
        if self.x > self.width:
            self.x = 0
        if self.y < 0:
            self.y = self.height
        if self.y > self.height:
            self.y = 0
        
        return self.age < self.lifetime
    
    def draw(self, screen):
        progress = self.age / self.lifetime
        brightness = int(self.max_brightness * math.sin(progress * math.pi))
        if brightness > 0:
            color = (brightness, int(brightness * 0.8), 0, brightness)
            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (3, 3), 2)
            screen.blit(surf, (int(self.x) - 3, int(self.y) - 3))


class ConfettiParticle:
    """Confetti particle for win celebration"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-15, -5)
        self.color = random.choice([GOLD, RED, CYAN, NEON_GREEN, NEON_PINK, ORANGE])
        self.size = random.randint(4, 10)
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.randint(-15, 15)
        self.lifetime = random.randint(60, 120)
        self.age = 0
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4  # Gravity
        self.vx *= 0.99  # Air resistance
        self.rotation += self.rotation_speed
        self.age += 1
        return self.age < self.lifetime
    
    def draw(self, screen):
        alpha = int(255 * (1 - self.age / self.lifetime))
        if alpha > 0:
            surf = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*self.color[:3], alpha), (0, 0, self.size * 2, self.size))
            rotated = pygame.transform.rotate(surf, self.rotation)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect)


class Card:
    """Represents a playing card with visual animation"""
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.face_up = False
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.flip_progress = 0  # 0 = face down, 1 = face up
        self.flip_speed = 0.1
        self.is_flipping = False
        self.deal_progress = 0
        self.deal_speed = 0.15
        self.is_dealing = False
        self.start_x = 0
        self.start_y = 0
        self.hover_offset = 0
        self.hover_time = random.uniform(0, math.pi * 2)
    
    def get_value(self):
        """Get the blackjack value of the card"""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Ace initially counts as 11
        else:
            return int(self.rank)
    
    def is_red(self):
        return self.suit in ['♥', '♦']
    
    def deal_to(self, x, y, start_x=None, start_y=None):
        """Start dealing animation to target position"""
        self.target_x = x
        self.target_y = y
        self.start_x = start_x if start_x else self.x
        self.start_y = start_y if start_y else self.y
        self.deal_progress = 0
        self.is_dealing = True
    
    def flip(self):
        """Start flip animation"""
        self.is_flipping = True
    
    def update(self):
        """Update card animations"""
        # Deal animation
        if self.is_dealing:
            self.deal_progress += self.deal_speed
            if self.deal_progress >= 1:
                self.deal_progress = 1
                self.is_dealing = False
            
            # Ease-out interpolation
            t = 1 - (1 - self.deal_progress) ** 3
            self.x = self.start_x + (self.target_x - self.start_x) * t
            self.y = self.start_y + (self.target_y - self.start_y) * t
        
        # Flip animation
        if self.is_flipping:
            if self.face_up:
                self.flip_progress -= self.flip_speed
                if self.flip_progress <= 0:
                    self.flip_progress = 0
                    self.is_flipping = False
                    self.face_up = False
            else:
                self.flip_progress += self.flip_speed
                if self.flip_progress >= 1:
                    self.flip_progress = 1
                    self.is_flipping = False
                    self.face_up = True
        
        # Hover animation
        self.hover_time += 0.05
        self.hover_offset = math.sin(self.hover_time) * 2
    
    def draw(self, screen, font_large, font_small):
        """Draw the card"""
        # Calculate card width based on flip progress
        flip_scale = abs(math.cos(self.flip_progress * math.pi))
        current_width = max(4, int(CARD_WIDTH * flip_scale))
        
        # Determine if showing front or back
        show_front = self.flip_progress > 0.5
        
        # Card rectangle
        card_rect = pygame.Rect(
            int(self.x - current_width // 2),
            int(self.y - CARD_HEIGHT // 2 + self.hover_offset),
            current_width,
            CARD_HEIGHT
        )
        
        # Card shadow
        shadow_rect = card_rect.move(3, 3)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        if show_front and self.face_up:
            # Draw card front with golden border
            pygame.draw.rect(screen, WHITE, card_rect, border_radius=8)
            pygame.draw.rect(screen, (218, 165, 32), card_rect, 3, border_radius=8)
            pygame.draw.rect(screen, (200, 150, 20), card_rect.inflate(-4, -4), 1, border_radius=6)
            
            # Only draw content if card is wide enough
            if current_width > CARD_WIDTH * 0.7:
                # Card content
                color = RED if self.is_red() else BLACK
                
                # Rank in top-left corner
                rank_text = font_large.render(self.rank, True, color)
                rank_rect = rank_text.get_rect(topleft=(card_rect.left + 5, card_rect.top + 5))
                screen.blit(rank_text, rank_rect)
                
                # Small suit icon under rank in top-left
                draw_suit_icon(screen, self.suit, card_rect.left + 14, card_rect.top + 38, 0.4, color)
                
                # Large suit icon in center
                draw_suit_icon(screen, self.suit, card_rect.centerx, card_rect.centery, 1.2, color)
                
                # Decorative corner elements (gold dots)
                corner_color = (218, 165, 32)
                pygame.draw.circle(screen, corner_color, (card_rect.left + 6, card_rect.top + 6), 2)
                pygame.draw.circle(screen, corner_color, (card_rect.right - 6, card_rect.top + 6), 2)
                pygame.draw.circle(screen, corner_color, (card_rect.left + 6, card_rect.bottom - 6), 2)
                pygame.draw.circle(screen, corner_color, (card_rect.right - 6, card_rect.bottom - 6), 2)
        else:
            # Draw card back (casino pattern)
            pygame.draw.rect(screen, CASINO_RED, card_rect, border_radius=8)
            pygame.draw.rect(screen, GOLD, card_rect, 3, border_radius=8)
            
            # Draw pattern on back
            if current_width > 20:
                inner_rect = card_rect.inflate(-10, -10)
                pygame.draw.rect(screen, (100, 0, 0), inner_rect, border_radius=4)
                pygame.draw.rect(screen, GOLD, inner_rect, 1, border_radius=4)
                
                # Diamond pattern
                cx, cy = card_rect.center
                if current_width > 40:
                    for dy in range(-30, 31, 15):
                        for dx in range(-15, 16, 15):
                            diamond_x = cx + dx
                            diamond_y = cy + dy
                            if inner_rect.collidepoint(diamond_x, diamond_y):
                                points = [
                                    (diamond_x, diamond_y - 4),
                                    (diamond_x - 3, diamond_y),
                                    (diamond_x, diamond_y + 4),
                                    (diamond_x + 3, diamond_y)
                                ]
                                pygame.draw.polygon(screen, GOLD, points)


class Deck:
    """Represents a deck of cards"""
    
    def __init__(self, num_decks=1):
        self.num_decks = num_decks
        self.cards = []
        self.reset()
    
    def reset(self):
        """Reset and shuffle the deck"""
        self.cards = []
        for _ in range(self.num_decks):
            for suit in SUITS:
                for rank in RANKS:
                    self.cards.append(Card(suit, rank))
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def draw(self):
        """Draw a card from the deck"""
        if len(self.cards) == 0:
            self.reset()
        return self.cards.pop()


class BlackjackGame:
    """Main blackjack game logic"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.deck = Deck(num_decks=2)
        self.player_hand = []
        self.dealer_hand = []
        self.state = STATE_BETTING
        self.bet_amount = 10
        self.tokens = 100
        self.last_win = 0
        self.message = ""
        self.message_timer = 0
        
        # Animation state
        self.deal_queue = []  # Queue of cards to deal
        self.deal_delay = 0
        self.dealer_reveal_delay = 0
        
        # Visual effects
        self.casino_floaters = [CasinoFloater(width, height) for _ in range(12)]
        self.golden_sparkles = [GoldenSparkle(width, height) for _ in range(40)]
        self.confetti = []
        
        # Pulse effects
        self.pulse_time = 0
        self.win_effect_timer = 0
        
        # Fonts
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)
        
        # Button rects (will be set during draw)
        self.hit_button = pygame.Rect(0, 0, 100, 45)
        self.stand_button = pygame.Rect(0, 0, 100, 45)
        self.double_button = pygame.Rect(0, 0, 120, 45)
        self.deal_button = pygame.Rect(0, 0, 120, 50)
    
    def calculate_hand_value(self, hand):
        """Calculate the value of a hand, adjusting for aces"""
        value = 0
        aces = 0
        
        for card in hand:
            if card.face_up or hand == self.player_hand:
                card_val = card.get_value()
                if card.rank == 'A':
                    aces += 1
                value += card_val
        
        # Adjust for aces
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def get_visible_dealer_value(self):
        """Get the dealer's visible value (only face-up cards)"""
        value = 0
        aces = 0
        
        for card in self.dealer_hand:
            if card.face_up:
                card_val = card.get_value()
                if card.rank == 'A':
                    aces += 1
                value += card_val
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def start_new_game(self):
        """Start a new hand"""
        if self.tokens < self.bet_amount:
            self.message = "Not enough tokens!"
            self.message_timer = 120
            return
        
        self.tokens -= self.bet_amount
        self.player_hand = []
        self.dealer_hand = []
        self.last_win = 0
        self.message = ""
        self.confetti = []
        
        # Deal cards with animation
        deck_x = self.width - 80
        deck_y = 50
        
        # Queue up the initial deal
        self.deal_queue = [
            ('player', 0),
            ('dealer', 0),
            ('player', 1),
            ('dealer', 1),
        ]
        self.deal_delay = 0
        self.state = STATE_PLAYING
    
    def deal_card_to(self, target, index):
        """Deal a card to player or dealer"""
        card = self.deck.draw()
        deck_x = self.width - 80
        deck_y = 50
        card.x = deck_x
        card.y = deck_y
        
        if target == 'player':
            # Center cards horizontally
            card_spacing = 85
            total_width = (index + 1) * card_spacing
            start_x = (self.width - total_width) // 2 + card_spacing // 2
            target_x = start_x + index * card_spacing
            target_y = self.height - 160
            card.deal_to(target_x, target_y, deck_x, deck_y)
            card.face_up = True
            card.flip_progress = 1
            self.player_hand.append(card)
        else:
            # Center dealer cards horizontally
            card_spacing = 85
            total_width = (index + 1) * card_spacing
            start_x = (self.width - total_width) // 2 + card_spacing // 2
            target_x = start_x + index * card_spacing
            target_y = 140
            card.deal_to(target_x, target_y, deck_x, deck_y)
            # Second dealer card is face down
            if index == 1:
                card.face_up = False
                card.flip_progress = 0
            else:
                card.face_up = True
                card.flip_progress = 1
            self.dealer_hand.append(card)
    
    def hit(self):
        """Player takes another card"""
        if self.state != STATE_PLAYING:
            return
        
        card = self.deck.draw()
        deck_x = self.width - 80
        deck_y = 50
        card.x = deck_x
        card.y = deck_y
        
        index = len(self.player_hand)
        # Center cards horizontally
        card_spacing = 85
        total_width = (index + 1) * card_spacing
        start_x = (self.width - total_width) // 2 + card_spacing // 2
        target_x = start_x + index * card_spacing
        target_y = self.height - 160
        
        card.deal_to(target_x, target_y, deck_x, deck_y)
        card.face_up = True
        card.flip_progress = 1
        self.player_hand.append(card)
        
        # Check for bust
        if self.calculate_hand_value(self.player_hand) > 21:
            self.end_game("BUST! You lose.")
    
    def stand(self):
        """Player stands, dealer's turn"""
        if self.state != STATE_PLAYING:
            return
        
        self.state = STATE_DEALER_TURN
        self.dealer_reveal_delay = 30  # Delay before revealing
        
        # Flip dealer's hidden card
        if len(self.dealer_hand) > 1 and not self.dealer_hand[1].face_up:
            self.dealer_hand[1].flip()
    
    def double_down(self):
        """Double the bet and take exactly one more card"""
        if self.state != STATE_PLAYING:
            return
        if len(self.player_hand) != 2:
            return
        if self.tokens < self.bet_amount:
            self.message = "Not enough tokens to double!"
            self.message_timer = 120
            return
        
        self.tokens -= self.bet_amount
        self.bet_amount *= 2
        
        self.hit()
        
        if self.state == STATE_PLAYING:  # If not bust
            self.stand()
    
    def dealer_play(self):
        """Dealer takes cards until 17 or higher"""
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        
        if dealer_value < 17:
            card = self.deck.draw()
            deck_x = self.width - 80
            deck_y = 50
            card.x = deck_x
            card.y = deck_y
            
            index = len(self.dealer_hand)
            # Center dealer cards horizontally
            card_spacing = 85
            total_width = (index + 1) * card_spacing
            start_x = (self.width - total_width) // 2 + card_spacing // 2
            target_x = start_x + index * card_spacing
            target_y = 140
            
            card.deal_to(target_x, target_y, deck_x, deck_y)
            card.face_up = True
            card.flip_progress = 1
            self.dealer_hand.append(card)
            
            self.dealer_reveal_delay = 40  # Delay before next action
        else:
            self.determine_winner()
    
    def determine_winner(self):
        """Determine the winner of the hand"""
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        
        if dealer_value > 21:
            self.end_game("Dealer BUSTS! You win!", win_multiplier=2)
        elif dealer_value > player_value:
            self.end_game("Dealer wins.")
        elif player_value > dealer_value:
            self.end_game("You WIN!", win_multiplier=2)
        else:
            self.end_game("Push - Tie!", win_multiplier=1)
    
    def end_game(self, message, win_multiplier=0):
        """End the current hand"""
        self.state = STATE_GAME_OVER
        self.message = message
        self.message_timer = 180
        
        if win_multiplier > 0:
            winnings = self.bet_amount * win_multiplier
            self.tokens += winnings
            self.last_win = winnings - self.bet_amount if win_multiplier > 1 else 0
            
            if self.last_win > 0:
                self.win_effect_timer = 120
                # Create confetti
                for _ in range(50):
                    self.confetti.append(ConfettiParticle(
                        self.width // 2,
                        self.height // 2
                    ))
        
        # Reset bet amount if doubled
        self.bet_amount = min(self.bet_amount, 100)
        if self.bet_amount > self.tokens and self.tokens > 0:
            self.bet_amount = max(10, (self.tokens // 10) * 10)
    
    def change_bet(self, increase):
        """Change the bet amount"""
        if self.state not in [STATE_BETTING, STATE_GAME_OVER]:
            return
        
        if increase:
            new_bet = min(self.bet_amount + 10, self.tokens, 100)
        else:
            new_bet = max(self.bet_amount - 10, 10)
        
        self.bet_amount = new_bet
    
    def update(self):
        """Update game state"""
        self.pulse_time += 0.05
        
        # Update card animations
        for card in self.player_hand + self.dealer_hand:
            card.update()
        
        # Process deal queue
        if self.deal_queue and self.deal_delay <= 0:
            target, index = self.deal_queue.pop(0)
            self.deal_card_to(target, index)
            self.deal_delay = 15
        elif self.deal_delay > 0:
            self.deal_delay -= 1
        
        # Check for blackjack after initial deal
        if self.state == STATE_PLAYING and len(self.player_hand) == 2 and len(self.deal_queue) == 0:
            if self.calculate_hand_value(self.player_hand) == 21:
                # Check if all cards are done dealing
                all_dealt = all(not card.is_dealing for card in self.player_hand + self.dealer_hand)
                if all_dealt:
                    self.stand()  # Auto-stand on blackjack
        
        # Dealer turn logic
        if self.state == STATE_DEALER_TURN:
            # Wait for cards to finish dealing
            all_dealt = all(not card.is_dealing for card in self.player_hand + self.dealer_hand)
            all_flipped = all(not card.is_flipping for card in self.dealer_hand)
            
            if all_dealt and all_flipped:
                if self.dealer_reveal_delay > 0:
                    self.dealer_reveal_delay -= 1
                else:
                    self.dealer_play()
        
        # Update effects
        for floater in self.casino_floaters:
            floater.update()
        
        self.golden_sparkles = [s for s in self.golden_sparkles if s.update()]
        while len(self.golden_sparkles) < 40:
            self.golden_sparkles.append(GoldenSparkle(self.width, self.height))
        
        self.confetti = [p for p in self.confetti if p.update()]
        
        if self.message_timer > 0:
            self.message_timer -= 1
        
        if self.win_effect_timer > 0:
            self.win_effect_timer -= 1
    
    def draw(self, screen):
        """Draw the game"""
        # Draw background
        self.draw_background(screen)
        
        # Draw felt table
        table_rect = pygame.Rect(50, 50, self.width - 100, self.height - 100)
        pygame.draw.rect(screen, FELT_GREEN, table_rect, border_radius=20)
        pygame.draw.rect(screen, GOLD, table_rect, 4, border_radius=20)
        
        # Draw golden sparkles
        for sparkle in self.golden_sparkles:
            sparkle.draw(screen)
        
        # Draw deck
        deck_x = self.width - 80
        deck_y = 50
        for i in range(min(5, len(self.deck.cards) // 10)):
            deck_rect = pygame.Rect(deck_x - CARD_WIDTH // 2 - i * 2, 
                                   deck_y - CARD_HEIGHT // 2 + i * 2,
                                   CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(screen, CASINO_RED, deck_rect, border_radius=8)
            pygame.draw.rect(screen, GOLD, deck_rect, 2, border_radius=8)
        
        # Draw dealer label (centered)
        dealer_label = self.font_medium.render("DEALER", True, GOLD)
        dealer_label_rect = dealer_label.get_rect(centerx=self.width // 2, top=60)
        screen.blit(dealer_label, dealer_label_rect)
        
        # Draw dealer hand
        for card in self.dealer_hand:
            card.draw(screen, self.font_large, self.font_small)
        
        # Draw dealer value (centered below dealer area)
        if len(self.dealer_hand) > 0:
            if self.state in [STATE_DEALER_TURN, STATE_GAME_OVER]:
                dealer_val = self.calculate_hand_value(self.dealer_hand)
            else:
                dealer_val = self.get_visible_dealer_value()
            
            val_text = self.font_medium.render(f"Value: {dealer_val}", True, WHITE)
            val_rect = val_text.get_rect(centerx=self.width // 2, top=200)
            screen.blit(val_text, val_rect)
        
        # Draw player label (centered)
        player_label = self.font_medium.render("YOUR HAND", True, GOLD)
        player_label_rect = player_label.get_rect(centerx=self.width // 2, bottom=self.height - 220)
        screen.blit(player_label, player_label_rect)
        
        # Draw player hand
        for card in self.player_hand:
            card.draw(screen, self.font_large, self.font_small)
        
        # Draw player value (centered below cards)
        if len(self.player_hand) > 0:
            player_val = self.calculate_hand_value(self.player_hand)
            color = RED if player_val > 21 else (NEON_GREEN if player_val == 21 else WHITE)
            val_text = self.font_medium.render(f"Value: {player_val}", True, color)
            val_rect = val_text.get_rect(centerx=self.width // 2, top=self.height - 95)
            screen.blit(val_text, val_rect)
        
        # Draw UI
        self.draw_ui(screen)
        
        # Draw confetti
        for particle in self.confetti:
            particle.draw(screen)
        
        # Draw message
        if self.message and self.message_timer > 0:
            self.draw_message(screen)
    
    def draw_background(self, screen):
        """Draw the casino background"""
        # Gradient background
        for y in range(self.height):
            progress = y / self.height
            r = int(20 * (1 - progress) + 10 * progress)
            g = int(60 * (1 - progress) + 30 * progress)
            b = int(20 * (1 - progress) + 10 * progress)
            pygame.draw.line(screen, (r, g, b), (0, y), (self.width, y))
        
        # Draw floating elements
        for floater in self.casino_floaters:
            floater.draw(screen)
    
    def draw_ui(self, screen):
        """Draw UI elements"""
        # Token display
        token_text = f"Tokens: {self.tokens}"
        token_surf = self.font_medium.render(token_text, True, GOLD)
        token_rect = token_surf.get_rect(topleft=(70, 70))
        pygame.draw.rect(screen, (0, 0, 0, 150), token_rect.inflate(20, 10), border_radius=8)
        screen.blit(token_surf, token_rect)
        
        # Bet display
        bet_text = f"Bet: {self.bet_amount}"
        bet_surf = self.font_medium.render(bet_text, True, WHITE)
        bet_rect = bet_surf.get_rect(topleft=(70, 100))
        screen.blit(bet_surf, bet_rect)
        
        # Last win display
        if self.last_win > 0:
            pulse = abs(math.sin(self.pulse_time * 3))
            color = (
                int(255 * (0.7 + 0.3 * pulse)),
                int(215 * (0.7 + 0.3 * pulse)),
                0
            )
            win_text = f"+{self.last_win}"
            win_surf = self.font_large.render(win_text, True, color)
            win_rect = win_surf.get_rect(topleft=(70, 130))
            screen.blit(win_surf, win_rect)
        
        # Draw buttons based on state
        mouse_pos = pygame.mouse.get_pos()
        
        if self.state in [STATE_BETTING, STATE_GAME_OVER]:
            # Deal button (centered at bottom)
            self.deal_button.center = (self.width // 2, self.height - 50)
            self.draw_button(screen, self.deal_button, "DEAL", mouse_pos, NEON_GREEN)
            
            # Bet adjustment hint below button
            hint_text = "UP/DOWN to change bet"
            hint_surf = self.font_small.render(hint_text, True, (200, 200, 200))
            hint_rect = hint_surf.get_rect(center=(self.width // 2, self.height - 18))
            screen.blit(hint_surf, hint_rect)
        
        elif self.state == STATE_PLAYING:
            # Check if all cards are done dealing
            all_dealt = all(not card.is_dealing for card in self.player_hand + self.dealer_hand)
            if all_dealt and len(self.deal_queue) == 0:
                btn_y = self.height - 50
                
                # Check if double is available to determine button count
                has_double = len(self.player_hand) == 2 and self.tokens >= self.bet_amount
                
                if has_double:
                    # 3 buttons: center them with spacing
                    btn_spacing = 140
                    center_x = self.width // 2
                    
                    self.hit_button.center = (center_x - btn_spacing, btn_y)
                    self.stand_button.center = (center_x, btn_y)
                    self.double_button.center = (center_x + btn_spacing, btn_y)
                    
                    self.draw_button(screen, self.hit_button, "HIT", mouse_pos, CYAN)
                    self.draw_button(screen, self.stand_button, "STAND", mouse_pos, ORANGE)
                    self.draw_button(screen, self.double_button, "DOUBLE", mouse_pos, NEON_PINK)
                else:
                    # 2 buttons: center them
                    btn_spacing = 120
                    center_x = self.width // 2
                    
                    self.hit_button.center = (center_x - btn_spacing // 2 - 50, btn_y)
                    self.stand_button.center = (center_x + btn_spacing // 2 + 50, btn_y)
                    
                    self.draw_button(screen, self.hit_button, "HIT", mouse_pos, CYAN)
                    self.draw_button(screen, self.stand_button, "STAND", mouse_pos, ORANGE)
        
        # Controls hint (positioned in bottom-right corner)
        controls = []
        if self.state in [STATE_BETTING, STATE_GAME_OVER]:
            controls = ["SPACE - Deal", "UP/DOWN - Bet", "ESC - Back"]
        elif self.state == STATE_PLAYING:
            controls = ["H - Hit", "S - Stand", "D - Double", "ESC - Back"]
        else:
            controls = ["ESC - Back"]
        
        hint_y = 70
        for i, hint in enumerate(controls):
            hint_surf = self.font_small.render(hint, True, (180, 180, 180))
            hint_rect = hint_surf.get_rect(right=self.width - 70, top=hint_y + i * 22)
            screen.blit(hint_surf, hint_rect)
    
    def draw_button(self, screen, rect, text, mouse_pos, color):
        """Draw a styled button"""
        is_hovered = rect.collidepoint(mouse_pos)
        
        # Button glow on hover
        if is_hovered:
            glow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color[:3], 100), (0, 0, rect.width + 10, rect.height + 10), border_radius=12)
            screen.blit(glow_surf, (rect.left - 5, rect.top - 5))
        
        # Button background
        btn_color = tuple(min(255, c + 30) for c in color[:3]) if is_hovered else color[:3]
        pygame.draw.rect(screen, btn_color, rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
        
        # Button text
        text_surf = self.font_medium.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
    
    def draw_message(self, screen):
        """Draw game message"""
        # Semi-transparent backdrop
        backdrop = pygame.Surface((self.width, 80), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 180))
        screen.blit(backdrop, (0, self.height // 2 - 40))
        
        # Message text with pulse effect
        pulse = abs(math.sin(self.pulse_time * 2))
        scale = 1.0 + 0.1 * pulse
        
        # Determine color based on message
        if "WIN" in self.message or "BUST" in self.message.upper() and "Dealer" in self.message:
            color = GOLD
        elif "lose" in self.message.lower() or "BUST" in self.message:
            color = RED
        elif "Tie" in self.message or "Push" in self.message:
            color = CYAN
        else:
            color = WHITE
        
        font_size = int(42 * scale)
        msg_font = pygame.font.Font(None, font_size)
        msg_surf = msg_font.render(self.message, True, color)
        msg_rect = msg_surf.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(msg_surf, msg_rect)
    
    def handle_click(self, pos):
        """Handle mouse click"""
        if self.state in [STATE_BETTING, STATE_GAME_OVER]:
            if self.deal_button.collidepoint(pos):
                self.start_new_game()
        elif self.state == STATE_PLAYING:
            all_dealt = all(not card.is_dealing for card in self.player_hand + self.dealer_hand)
            if all_dealt and len(self.deal_queue) == 0:
                if self.hit_button.collidepoint(pos):
                    self.hit()
                elif self.stand_button.collidepoint(pos):
                    self.stand()
                elif self.double_button.collidepoint(pos) and len(self.player_hand) == 2:
                    self.double_down()
    
    def handle_keypress(self, key):
        """Handle keyboard input"""
        if key == pygame.K_SPACE:
            if self.state in [STATE_BETTING, STATE_GAME_OVER]:
                self.start_new_game()
        elif key == pygame.K_h:
            if self.state == STATE_PLAYING:
                self.hit()
        elif key == pygame.K_s:
            if self.state == STATE_PLAYING:
                self.stand()
        elif key == pygame.K_d:
            if self.state == STATE_PLAYING and len(self.player_hand) == 2:
                self.double_down()
        elif key == pygame.K_UP:
            self.change_bet(True)
        elif key == pygame.K_DOWN:
            self.change_bet(False)


# === Functions to be called from main.py ===

def draw_blackjack_scene(surface: pygame.Surface, game_state: dict, font: pygame.font.Font) -> dict:
    """Draw and update blackjack game on the given surface."""
    if "game" not in game_state:
        tokens = game_state.get("tokens", 100)
        surf_w, surf_h = surface.get_size()
        game = BlackjackGame(surf_w, surf_h)
        game.tokens = tokens
        
        game_state = {
            "game": game,
            "tokens": tokens,
        }
    
    game: BlackjackGame = game_state["game"]
    game.update()
    game.draw(surface)
    
    # Sync tokens
    game_state["tokens"] = game.tokens
    
    return game_state


def handle_blackjack_click(game_state: dict, pos: tuple) -> dict:
    """Handle mouse click in blackjack game."""
    if "game" in game_state:
        game_state["game"].handle_click(pos)
    return game_state


def handle_blackjack_keypress(game_state: dict, key: int) -> dict:
    """Handle keypress in blackjack game."""
    if "game" in game_state:
        game_state["game"].handle_keypress(key)
    return game_state


def change_blackjack_bet(game_state: dict, increase: bool) -> dict:
    """Change blackjack bet amount."""
    if "game" in game_state:
        game_state["game"].change_bet(increase)
    return game_state
