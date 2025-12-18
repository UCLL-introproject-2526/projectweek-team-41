"""
Higher or Lower - Casino Style Card Game
=========================================
Guess if the next card is higher or lower than the current one.
"""

import pygame
import random
import math

# Constants
SCREEN_WIDTH = 800
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
PURPLE = (147, 112, 219)
PINK = (255, 192, 203)
YELLOW = (255, 255, 0)
COLOR_BACKGROUND = (20, 60, 20)


# =============================================================================
# VFX CLASSES
# =============================================================================

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


# =============================================================================
# CARD DRAWING FUNCTIONS
# =============================================================================

def draw_heart(surface, x, y, size, color):
    """Draw a heart symbol at (x, y) with given size."""
    points = []
    for i in range(360):
        angle = math.radians(i)
        # Parametric heart equation
        hx = size * (16 * math.sin(angle) ** 3)
        hy = -size * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        points.append((x + hx, y + hy))
    
    if len(points) > 2:
        pygame.draw.polygon(surface, color, points)


def create_card_surface(value, width=140, height=200):
    """
    Create a beautiful casino-style card surface for the given value (1-13).
    Returns a pygame Surface with rounded corners.
    """
    card = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw rounded rectangle for card shape
    border_radius = 12
    pygame.draw.rect(card, (255, 255, 255), (0, 0, width, height), border_radius=border_radius)
    
    # Main card border - golden casino style
    border_color = (218, 165, 32)  # Goldenrod
    pygame.draw.rect(card, border_color, (0, 0, width, height), width=4, border_radius=border_radius)
    pygame.draw.rect(card, (200, 150, 20), (2, 2, width-4, height-4), width=2, border_radius=border_radius-1)
    
    # Red color for hearts
    heart_color = (220, 20, 60)  # Crimson
    
    # Convert value to display string
    def value_to_str(v):
        if v == 1:
            return "A"
        elif v == 11:
            return "J"
        elif v == 12:
            return "Q"
        elif v == 13:
            return "K"
        else:
            return str(v)
    
    display_value = value_to_str(value)
    
    # Create fonts
    try:
        large_font = pygame.font.SysFont('serifbold', 60)
        small_font = pygame.font.SysFont('serifbold', 24)
    except:
        large_font = pygame.font.SysFont(None, 60)
        small_font = pygame.font.SysFont(None, 24)
    
    # Top-left corner value
    text_surface = small_font.render(display_value, True, heart_color)
    card.blit(text_surface, (12, 8))
    draw_heart(card, 20, 38, 0.6, heart_color)
    
    # Bottom-right corner value (upside down)
    text_surface = small_font.render(display_value, True, heart_color)
    text_surface = pygame.transform.rotate(text_surface, 180)
    card.blit(text_surface, (width - text_surface.get_width() - 12, height - text_surface.get_height() - 8))
    draw_heart(card, width - 20, height - 38, 0.6, heart_color)
    
    # Center design based on value
    center_x = width // 2
    center_y = height // 2
    
    if value == 1:  # Ace - one large heart
        draw_heart(card, center_x, center_y, 2.2, heart_color)
    elif value <= 10:
        # Draw hearts in pattern
        heart_size = 0.9
        if value == 2:
            draw_heart(card, center_x, center_y - 40, heart_size, heart_color)
            draw_heart(card, center_x, center_y + 40, heart_size, heart_color)
        elif value == 3:
            draw_heart(card, center_x, center_y - 50, heart_size, heart_color)
            draw_heart(card, center_x, center_y, heart_size, heart_color)
            draw_heart(card, center_x, center_y + 50, heart_size, heart_color)
        elif value == 4:
            draw_heart(card, center_x - 25, center_y - 40, heart_size, heart_color)
            draw_heart(card, center_x + 25, center_y - 40, heart_size, heart_color)
            draw_heart(card, center_x - 25, center_y + 40, heart_size, heart_color)
            draw_heart(card, center_x + 25, center_y + 40, heart_size, heart_color)
        elif value == 5:
            draw_heart(card, center_x - 25, center_y - 40, heart_size, heart_color)
            draw_heart(card, center_x + 25, center_y - 40, heart_size, heart_color)
            draw_heart(card, center_x, center_y, heart_size, heart_color)
            draw_heart(card, center_x - 25, center_y + 40, heart_size, heart_color)
            draw_heart(card, center_x + 25, center_y + 40, heart_size, heart_color)
        else:
            # For 6-10, draw large value + heart
            large_text = large_font.render(display_value, True, heart_color)
            text_rect = large_text.get_rect(center=(center_x, center_y - 20))
            card.blit(large_text, text_rect)
            draw_heart(card, center_x, center_y + 35, 1.5, heart_color)
    else:
        # Face cards (J, Q, K) - large letter with decorative heart
        large_text = large_font.render(display_value, True, heart_color)
        text_rect = large_text.get_rect(center=(center_x, center_y - 15))
        card.blit(large_text, text_rect)
        draw_heart(card, center_x, center_y + 40, 1.3, heart_color)
    
    # Decorative corner elements
    corner_color = (218, 165, 32)
    for cx, cy in [(8, 8), (width-8, 8), (8, height-8), (width-8, height-8)]:
        pygame.draw.circle(card, corner_color, (cx, cy), 3)
    
    return card


def create_card_back(width=140, height=200):
    """
    Create a beautiful card back with casino pattern.
    Returns a pygame Surface with rounded corners.
    """
    card = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Deep red casino background with rounded corners
    border_radius = 12
    pygame.draw.rect(card, (160, 20, 20), (0, 0, width, height), border_radius=border_radius)
    border_color = (218, 165, 32)  # Gold
    pygame.draw.rect(card, border_color, (0, 0, width, height), width=4, border_radius=border_radius)
    pygame.draw.rect(card, (255, 215, 0), (2, 2, width-4, height-4), width=2, border_radius=border_radius-1)
    
    # Create diamond pattern
    diamond_color = (255, 215, 0)  # Solid gold
    spacing = 20
    
    for y in range(-20, height + 20, spacing):
        for x in range(-20, width + 20, spacing):
            # Diamond shape
            diamond_size = 8
            points = [
                (x, y - diamond_size),
                (x + diamond_size, y),
                (x, y + diamond_size),
                (x - diamond_size, y)
            ]
            pygame.draw.polygon(card, diamond_color, points)
    
    # Center decorative circle
    center_x = width // 2
    center_y = height // 2
    
    # Outer circle
    pygame.draw.circle(card, (255, 215, 0), (center_x, center_y), 35, width=3)
    pygame.draw.circle(card, (218, 165, 32), (center_x, center_y), 32, width=2)
    
    # Inner pattern
    for i in range(8):
        angle = i * math.pi / 4
        x1 = center_x + int(20 * math.cos(angle))
        y1 = center_y + int(20 * math.sin(angle))
        x2 = center_x + int(28 * math.cos(angle))
        y2 = center_y + int(28 * math.sin(angle))
        pygame.draw.line(card, (255, 215, 0), (x1, y1), (x2, y2), 2)
    
    # Center star
    for i in range(12):
        angle = i * math.pi / 6
        length = 15 if i % 2 == 0 else 8
        x = center_x + int(length * math.cos(angle))
        y = center_y + int(length * math.sin(angle))
        pygame.draw.circle(card, (255, 215, 0), (x, y), 2)
    
    return card


def generate_all_cards(width=140, height=200):
    """
    Generate all card surfaces (1-13) and card back.
    Returns (card_dict, card_back_surface).
    """
    card_dict = {}
    for value in range(1, 14):
        card_dict[value] = create_card_surface(value, width, height)
    
    card_back = create_card_back(width, height)
    
    return card_dict, card_back


# =============================================================================
# MAIN GAME CLASS
# =============================================================================

class HigherLowerGame:
    """Main Higher or Lower game logic"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Generate card images
        self.card_images, self.card_back = generate_all_cards(width=120, height=170)
        
        # Game state
        self.current_card = random.randint(1, 13)
        self.next_card = self._get_new_card(self.current_card)
        self.tokens = 100
        self.bet_amount = 10
        self.message = ""
        self.message_timer = 0
        
        # Animation state
        self.flip_progress = 0.0  # 0 = card back, 2 = card front
        self.flip_speed = 0.08
        self.is_flipping = False
        self.flip_complete = False
        self.waiting_reveal = False
        self.reveal_timer = 0
        self.reveal_duration = 90  # frames
        
        # Win tracking
        self.last_result = None  # "win", "lose", or None
        
        # Visual effects
        self.casino_floaters = [CasinoFloater(width, height) for _ in range(15)]
        self.golden_sparkles = []
        for _ in range(40):
            sparkle = GoldenSparkle(width, height)
            sparkle.age = random.randint(0, sparkle.lifetime - 1)
            self.golden_sparkles.append(sparkle)
        self.confetti = []
        
        # Pulse effects
        self.pulse_time = 0
        
        # Fonts
        self.font_large = pygame.font.Font(None, 42)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_button = pygame.font.Font(None, 36)
        
        # Button rects
        self.higher_button = pygame.Rect(0, 0, 120, 50)
        self.lower_button = pygame.Rect(0, 0, 120, 50)
        self.bet_minus_button = pygame.Rect(0, 0, 40, 40)
        self.bet_plus_button = pygame.Rect(0, 0, 40, 40)
        self.bet_50_button = pygame.Rect(0, 0, 60, 40)
        self.bet_100_button = pygame.Rect(0, 0, 70, 40)
        self.allin_button = pygame.Rect(0, 0, 80, 40)
    
    def _get_new_card(self, exclude):
        """Get a new random card, excluding a specific value."""
        new_card = random.randint(1, 13)
        while new_card == exclude:
            new_card = random.randint(1, 13)
        return new_card
    
    def guess(self, guess_higher):
        """Make a guess: True for higher, False for lower."""
        if self.waiting_reveal or self.is_flipping:
            return
        
        if self.tokens < self.bet_amount:
            self.message = "Not enough tokens!"
            self.message_timer = 90
            return
        
        # Deduct bet
        self.tokens -= self.bet_amount
        
        # Check result
        result_higher = self.next_card > self.current_card
        correct = (guess_higher == result_higher)
        
        if correct:
            winnings = self.bet_amount * 2
            self.tokens += winnings
            self.message = f"Correct! +{winnings} tokens!"
            self.last_result = "win"
            # Spawn confetti
            for _ in range(20):
                self.confetti.append(ConfettiParticle(self.width // 2, self.height // 2))
        else:
            self.message = f"Wrong! Lost {self.bet_amount} tokens!"
            self.last_result = "lose"
        
        self.message_timer = 120
        self.is_flipping = True
        self.flip_progress = 0.0
        self.waiting_reveal = True
        self.reveal_timer = 0
    
    def change_bet(self, increase, amount=10):
        """Change the bet amount."""
        if self.waiting_reveal or self.is_flipping:
            return
        
        if increase:
            if self.bet_amount + amount <= self.tokens:
                self.bet_amount = min(self.bet_amount + amount, 1000)
        else:
            self.bet_amount = max(self.bet_amount - amount, 10)
    
    def set_bet(self, amount):
        """Set bet to a specific amount."""
        if self.waiting_reveal or self.is_flipping:
            return
        
        if amount <= self.tokens:
            self.bet_amount = max(10, min(amount, 1000))
        else:
            self.bet_amount = max(10, self.tokens)
    
    def all_in(self):
        """Set bet to all tokens."""
        if self.waiting_reveal or self.is_flipping:
            return
        self.bet_amount = max(10, self.tokens)
    
    def update(self):
        """Update game state and animations."""
        self.pulse_time += 1
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ""
        
        # Update flip animation
        if self.is_flipping:
            self.flip_progress += self.flip_speed
            if self.flip_progress >= 2.0:
                self.flip_progress = 2.0
                self.is_flipping = False
                self.flip_complete = True
        
        # Update reveal timer
        if self.waiting_reveal and self.flip_complete:
            self.reveal_timer += 1
            if self.reveal_timer >= self.reveal_duration:
                # Start next round
                if self.tokens > 0:
                    self.current_card = self.next_card
                    self.next_card = self._get_new_card(self.current_card)
                    self.flip_progress = 0.0
                    self.flip_complete = False
                    self.waiting_reveal = False
                    self.reveal_timer = 0
                    self.last_result = None
                    # Adjust bet if needed
                    if self.bet_amount > self.tokens:
                        self.bet_amount = max(10, self.tokens)
                else:
                    self.message = "Game Over! Out of tokens!"
                    self.message_timer = 999999
        
        # Update VFX
        for floater in self.casino_floaters:
            floater.update()
        
        new_sparkles = []
        for sparkle in self.golden_sparkles:
            if sparkle.update():
                new_sparkles.append(sparkle)
            else:
                new_sparkles.append(GoldenSparkle(self.width, self.height))
        self.golden_sparkles = new_sparkles
        
        self.confetti = [c for c in self.confetti if c.update()]
    
    def draw_flipped_card(self, screen, card_img, x, y):
        """Draw a card with horizontal flip animation."""
        width = card_img.get_width()
        height = card_img.get_height()
        
        # Calculate scaled width based on flip progress (0->1->0)
        if self.flip_progress <= 1.0:
            scale_x = 1.0 - self.flip_progress
        else:
            scale_x = self.flip_progress - 1.0
        
        if scale_x < 0.01:
            scale_x = 0.01  # Prevent zero width
        
        scaled_width = int(width * scale_x)
        scaled_card = pygame.transform.scale(card_img, (scaled_width, height))
        
        # Center the scaled card
        offset_x = (width - scaled_width) // 2
        screen.blit(scaled_card, (x + offset_x, y))
    
    def draw(self, surface):
        """Draw the game."""
        # Background
        surface.fill(COLOR_BACKGROUND)
        
        # Draw VFX (background layer)
        for floater in self.casino_floaters:
            floater.update()
            floater.draw(surface)
        
        for sparkle in self.golden_sparkles:
            sparkle.draw(surface)
        
        # Draw title
        title_text = self.font_large.render("Higher or Lower", True, GOLD)
        title_rect = title_text.get_rect(centerx=self.width // 2, top=20)
        surface.blit(title_text, title_rect)
        
        # Draw balance
        balance_text = self.font_medium.render(f"Tokens: {self.tokens}", True, GOLD)
        balance_rect = balance_text.get_rect(centerx=self.width // 2, top=60)
        surface.blit(balance_text, balance_rect)
        
        # Draw bet info and buttons
        bet_y = 110
        bet_text = self.font_small.render(f"Current Bet: {self.bet_amount}", True, WHITE)
        surface.blit(bet_text, (30, bet_y))
        
        # Bet adjustment buttons
        button_y = bet_y + 30
        self.bet_minus_button = pygame.Rect(30, button_y, 40, 40)
        self.bet_plus_button = pygame.Rect(80, button_y, 40, 40)
        self.allin_button = pygame.Rect(130, button_y, 80, 40)
        self.bet_50_button = pygame.Rect(30, button_y + 50, 60, 40)
        self.bet_100_button = pygame.Rect(100, button_y + 50, 70, 40)
        
        # Draw buttons
        pygame.draw.rect(surface, (180, 50, 50), self.bet_minus_button, border_radius=8)
        pygame.draw.rect(surface, (50, 180, 50), self.bet_plus_button, border_radius=8)
        pygame.draw.rect(surface, (218, 165, 32), self.allin_button, border_radius=8)
        pygame.draw.rect(surface, (70, 130, 180), self.bet_50_button, border_radius=8)
        pygame.draw.rect(surface, (130, 70, 180), self.bet_100_button, border_radius=8)
        
        # Button borders
        pygame.draw.rect(surface, WHITE, self.bet_minus_button, width=2, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.bet_plus_button, width=2, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.allin_button, width=2, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.bet_50_button, width=2, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.bet_100_button, width=2, border_radius=8)
        
        # Button text
        button_font = pygame.font.Font(None, 48)
        small_button_font = pygame.font.Font(None, 24)
        
        minus_text = button_font.render("-", True, WHITE)
        plus_text = button_font.render("+", True, WHITE)
        allin_text = small_button_font.render("ALL IN", True, WHITE)
        bet50_text = small_button_font.render("50", True, WHITE)
        bet100_text = small_button_font.render("100", True, WHITE)
        
        surface.blit(minus_text, minus_text.get_rect(center=self.bet_minus_button.center))
        surface.blit(plus_text, plus_text.get_rect(center=self.bet_plus_button.center))
        surface.blit(allin_text, allin_text.get_rect(center=self.allin_button.center))
        surface.blit(bet50_text, bet50_text.get_rect(center=self.bet_50_button.center))
        surface.blit(bet100_text, bet100_text.get_rect(center=self.bet_100_button.center))
        
        # Cards layout
        card_w = self.card_images[1].get_width()
        card_h = self.card_images[1].get_height()
        gap = 60
        left_x = self.width // 2 - card_w - gap // 2
        right_x = self.width // 2 + gap // 2
        card_y = self.height // 2 - card_h // 2 + 10
        
        # Right card - always visible with current value
        if self.current_card in self.card_images:
            surface.blit(self.card_images[self.current_card], (right_x, card_y))
        
        # Left card - animates flip from back to front
        if self.flip_progress == 0.0:
            # Show card back (not flipping)
            surface.blit(self.card_back, (left_x, card_y))
        elif self.flip_progress >= 2.0:
            # Flip complete - show next card value
            if self.next_card in self.card_images:
                surface.blit(self.card_images[self.next_card], (left_x, card_y))
        else:
            # Flipping animation in progress
            if self.flip_progress < 1.0:
                # First half: show card back shrinking
                self.draw_flipped_card(surface, self.card_back, left_x, card_y)
            else:
                # Second half: show card front growing
                if self.next_card in self.card_images:
                    self.draw_flipped_card(surface, self.card_images[self.next_card], left_x, card_y)
        
        # Card labels
        label_y = card_y + card_h + 10
        current_label = self.font_small.render("Current Card", True, WHITE)
        next_label = self.font_small.render("Next Card", True, WHITE)
        surface.blit(current_label, current_label.get_rect(centerx=right_x + card_w // 2, top=label_y))
        surface.blit(next_label, next_label.get_rect(centerx=left_x + card_w // 2, top=label_y))
        
        # Higher/Lower buttons
        if not self.waiting_reveal:
            button_y = self.height - 100
            self.higher_button = pygame.Rect(self.width // 2 - 140, button_y, 120, 50)
            self.lower_button = pygame.Rect(self.width // 2 + 20, button_y, 120, 50)
            
            # Draw buttons with pulse effect
            pulse = math.sin(self.pulse_time * 0.1) * 5
            
            # Higher button (green)
            pygame.draw.rect(surface, (50, 180, 50), self.higher_button, border_radius=10)
            pygame.draw.rect(surface, GOLD, self.higher_button, width=3, border_radius=10)
            higher_text = self.font_button.render("HIGHER", True, WHITE)
            surface.blit(higher_text, higher_text.get_rect(center=self.higher_button.center))
            
            # Lower button (red)
            pygame.draw.rect(surface, (180, 50, 50), self.lower_button, border_radius=10)
            pygame.draw.rect(surface, GOLD, self.lower_button, width=3, border_radius=10)
            lower_text = self.font_button.render("LOWER", True, WHITE)
            surface.blit(lower_text, lower_text.get_rect(center=self.lower_button.center))
        
        # Draw message
        if self.message:
            if self.last_result == "win":
                msg_color = NEON_GREEN
            elif self.last_result == "lose":
                msg_color = RED
            else:
                msg_color = YELLOW
            msg_text = self.font_medium.render(self.message, True, msg_color)
            msg_rect = msg_text.get_rect(centerx=self.width // 2, top=self.height - 150)
            
            # Background for message
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect, border_radius=8)
            surface.blit(msg_text, msg_rect)
        
        # Instructions
        inst_text = self.font_small.render("UP = Higher | DOWN = Lower | ESC = Exit", True, (200, 200, 200))
        inst_rect = inst_text.get_rect(centerx=self.width // 2, bottom=self.height - 10)
        surface.blit(inst_text, inst_rect)
        
        # Draw confetti (foreground)
        for c in self.confetti:
            c.draw(surface)
    
    def handle_click(self, pos):
        """Handle mouse click."""
        if self.waiting_reveal or self.is_flipping:
            # Only allow bet changes when not in reveal
            if self.bet_minus_button.collidepoint(pos):
                self.change_bet(False)
            elif self.bet_plus_button.collidepoint(pos):
                self.change_bet(True)
            elif self.allin_button.collidepoint(pos):
                self.all_in()
            elif self.bet_50_button.collidepoint(pos):
                self.set_bet(50)
            elif self.bet_100_button.collidepoint(pos):
                self.set_bet(100)
            return
        
        if self.higher_button.collidepoint(pos):
            self.guess(True)
        elif self.lower_button.collidepoint(pos):
            self.guess(False)
        elif self.bet_minus_button.collidepoint(pos):
            self.change_bet(False)
        elif self.bet_plus_button.collidepoint(pos):
            self.change_bet(True)
        elif self.allin_button.collidepoint(pos):
            self.all_in()
        elif self.bet_50_button.collidepoint(pos):
            self.set_bet(50)
        elif self.bet_100_button.collidepoint(pos):
            self.set_bet(100)
    
    def handle_keypress(self, key):
        """Handle keypress."""
        if key == pygame.K_UP:
            if not self.waiting_reveal and not self.is_flipping:
                self.guess(True)
        elif key == pygame.K_DOWN:
            if not self.waiting_reveal and not self.is_flipping:
                self.guess(False)


# =============================================================================
# FUNCTIONS CALLED FROM MAIN.PY
# =============================================================================

def draw_higherlower_scene(surface: pygame.Surface, game_state: dict, font: pygame.font.Font) -> dict:
    """Draw and update higher/lower game on the given surface."""
    if "game" not in game_state:
        tokens = game_state.get("tokens", 100)
        surf_w, surf_h = surface.get_size()
        game = HigherLowerGame(surf_w, surf_h)
        game.tokens = tokens
        
        game_state = {
            "game": game,
            "tokens": tokens,
        }
    
    game: HigherLowerGame = game_state["game"]
    game.update()
    game.draw(surface)
    
    # Sync tokens
    game_state["tokens"] = game.tokens
    
    return game_state


def handle_higherlower_click(game_state: dict, pos: tuple) -> dict:
    """Handle mouse click in higher/lower game."""
    if "game" in game_state:
        game_state["game"].handle_click(pos)
    return game_state


def handle_higherlower_keypress(game_state: dict, key: int) -> dict:
    """Handle keypress in higher/lower game."""
    if "game" in game_state:
        game_state["game"].handle_keypress(key)
    return game_state


def change_higherlower_bet(game_state: dict, increase: bool) -> dict:
    """Change higher/lower bet amount."""
    if "game" in game_state:
        game_state["game"].change_bet(increase)
    return game_state
