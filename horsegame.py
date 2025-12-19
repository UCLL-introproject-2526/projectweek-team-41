"""
Horse Racing Betting Game - Casino Style
=========================================
Bet on horses and watch them race! 
1st place: bet × 5, 2nd place: bet × 2, 3rd place: bet × 1
"""

import pygame
import random
import math
import os
from pathlib import Path

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
PURPLE = (147, 112, 219)
PINK = (255, 192, 203)
YELLOW = (255, 255, 0)
COLOR_BACKGROUND = (20, 60, 20)
BROWN = (139, 90, 43)
SAND = (194, 178, 128)
TRACK_BROWN = (160, 82, 45)

# Horse colors for fallback (if images don't load)
HORSE_COLORS = {
    "Red": (220, 50, 50),
    "Blue": (50, 100, 220),
    "Yellow": (220, 200, 50),
    "Purple": (150, 50, 200),
    "Orange": (255, 140, 0),
}

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
        self.type = random.choice(["chip", "horseshoe", "star", "clover"])
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
        elif self.type == "horseshoe":
            # Draw a simple horseshoe shape
            pygame.draw.arc(surf, (218, 165, 32, self.alpha), 
                          (self.size - 8, self.size - 8, 16, 16), 
                          0.5, 2.6, 3)
        elif self.type == "star":
            color = (255, 215, 0, self.alpha)
            pygame.draw.circle(surf, color, (self.size, self.size), 4)
        elif self.type == "clover":
            color = (0, 200, 0, self.alpha)
            pygame.draw.circle(surf, color, (self.size - 4, self.size - 2), 4)
            pygame.draw.circle(surf, color, (self.size + 4, self.size - 2), 4)
            pygame.draw.circle(surf, color, (self.size, self.size + 3), 4)
        
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


class DustParticle:
    """Dust kicked up by racing horses"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 0)
        self.vy = random.uniform(-1, 1)
        self.lifetime = random.randint(20, 40)
        self.age = 0
        self.size = random.randint(3, 8)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.age += 1
        return self.age < self.lifetime
    
    def draw(self, screen):
        alpha = int(100 * (1 - self.age / self.lifetime))
        if alpha > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (180, 150, 100, alpha), (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x) - self.size, int(self.y) - self.size))


# =============================================================================
# HORSE CLASS
# =============================================================================

class Horse:
    """Represents a racing horse"""
    
    def __init__(self, name: str, lane: int, color: tuple, image=None):
        self.name = name
        self.lane = lane
        self.color = color
        self.image = image
        self.x = 80  # Starting position
        self.base_speed = random.uniform(2.0, 3.5)  # Base speed varies per horse
        self.current_speed = 0
        self.finished = False
        self.finish_position = 0
        self.finish_time = 0
        self.animation_frame = 0
        self.animation_timer = 0
    
    def reset(self, track_start: int = 80):
        """Reset horse for new race"""
        self.x = track_start
        self.base_speed = random.uniform(2.0, 3.5)
        self.current_speed = 0
        self.finished = False
        self.finish_position = 0
        self.finish_time = 0
    
    def update(self, dt: float, is_racing: bool, finish_line: int) -> bool:
        """Update horse position during race. Returns True if just crossed finish."""
        if self.finished:
            return False
        
        if is_racing:
            # Add some randomness to speed
            speed_variation = random.uniform(-0.5, 0.5)
            # Occasional burst of speed
            if random.random() < 0.02:
                speed_variation += random.uniform(1, 3)
            # Occasional slowdown
            if random.random() < 0.01:
                speed_variation -= random.uniform(0.5, 1.5)
            
            self.current_speed = max(0.5, self.base_speed + speed_variation)
            self.x += self.current_speed
            
            # Animation
            self.animation_timer += dt
            if self.animation_timer > 0.1:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
            
            # Check finish
            if self.x >= finish_line:
                self.finished = True
                return True
        
        return False
    
    def get_y(self, track_top: int, lane_height: int) -> int:
        """Get Y position based on lane"""
        return track_top + self.lane * lane_height + lane_height // 2


# =============================================================================
# HORSE RACING GAME CLASS
# =============================================================================

class HorseRacingGame:
    """Main horse racing betting game"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tokens = 100
        self.bet_amount = 50
        self.selected_horse = 0  # Index of selected horse
        
        # Race state
        self.is_racing = False
        self.race_finished = False
        self.countdown = 0
        self.countdown_timer = 0
        self.finish_order = []
        self.result_message = ""
        self.result_timer = 0
        self.winnings = 0
        
        # Track dimensions
        self.track_top = 150
        self.track_height = 300
        self.lane_height = self.track_height // 5
        self.track_start = 80
        self.finish_line = width - 100
        
        # Load horse images
        self.horse_images = {}
        self._load_horse_images()
        
        # Create horses
        self.horses = []
        horse_names = ["Red", "Blue", "Yellow", "Purple", "Orange"]
        for i, name in enumerate(horse_names):
            color = HORSE_COLORS.get(name, (100, 100, 100))
            image = self.horse_images.get(name)
            self.horses.append(Horse(name, i, color, image))
        
        # VFX
        self.floaters = [CasinoFloater(width, height) for _ in range(15)]
        self.sparkles = [GoldenSparkle(width, height) for _ in range(20)]
        self.confetti = []
        self.dust_particles = []
        
        # Fonts
        self.font_large = pygame.font.SysFont(None, 48)
        self.font_medium = pygame.font.SysFont(None, 36)
        self.font_small = pygame.font.SysFont(None, 28)
        self.font_tiny = pygame.font.SysFont(None, 22)
        
        # Buttons
        btn_y = height - 80
        self.bet_minus_button = pygame.Rect(width // 2 - 220, btn_y, 40, 40)
        self.bet_plus_button = pygame.Rect(width // 2 - 60, btn_y, 40, 40)
        self.start_button = pygame.Rect(width // 2 + 20, btn_y, 120, 40)
        self.allin_button = pygame.Rect(width // 2 + 160, btn_y, 80, 40)
        
        # Horse selection buttons (along left side)
        self.horse_buttons = []
        for i in range(5):
            y = self.track_top + i * self.lane_height + 5
            self.horse_buttons.append(pygame.Rect(10, y, 60, self.lane_height - 10))
    
    def _load_horse_images(self):
        """Load horse images from assets folder"""
        try:
            base_dir = str(Path(__file__).resolve().parent)
        except:
            base_dir = str(Path.cwd())
        
        horse_files = ["Red.png", "Blue.png", "Yellow.png", "Purple.png", "Orange.png"]
        
        for filename in horse_files:
            name = filename.replace(".png", "")
            try:
                path = os.path.join(base_dir, "assets", "img", "horses", filename)
                img = pygame.image.load(path).convert_alpha()
                # Scale to appropriate size
                img = pygame.transform.smoothscale(img, (60, 50))
                self.horse_images[name] = img
            except Exception as e:
                print(f"Could not load horse image {filename}: {e}")
    
    def reset_race(self):
        """Reset for a new race"""
        for horse in self.horses:
            horse.reset(self.track_start)
        self.is_racing = False
        self.race_finished = False
        self.countdown = 0
        self.countdown_timer = 0
        self.finish_order = []
        self.result_message = ""
        self.result_timer = 0
        self.winnings = 0
        self.dust_particles = []
    
    def start_race(self):
        """Start a new race"""
        if self.is_racing or self.race_finished:
            return
        
        if self.tokens < self.bet_amount:
            self.result_message = "Not enough tokens!"
            self.result_timer = 2.0
            return
        
        # Deduct bet
        self.tokens -= self.bet_amount
        
        # Reset horses
        self.reset_race()
        
        # Start countdown
        self.countdown = 3
        self.countdown_timer = 1.0
    
    def change_bet(self, increase: bool):
        """Change bet amount"""
        if self.is_racing or self.countdown > 0:
            return
        
        if increase:
            self.bet_amount = min(self.tokens, self.bet_amount + 10)
        else:
            self.bet_amount = max(50, self.bet_amount - 10)
    
    def all_in(self):
        """Set bet to all tokens"""
        if self.is_racing or self.countdown > 0:
            return
        self.bet_amount = max(50, self.tokens)
    
    def set_bet(self, amount: int):
        """Set specific bet amount"""
        if self.is_racing or self.countdown > 0:
            return
        self.bet_amount = min(amount, self.tokens)
        self.bet_amount = max(50, self.bet_amount)
    
    def select_horse(self, index: int):
        """Select a horse to bet on"""
        if self.is_racing or self.countdown > 0:
            return
        if 0 <= index < len(self.horses):
            self.selected_horse = index
    
    def update(self):
        """Update game state"""
        dt = 1 / 60.0
        
        # Update VFX
        for f in self.floaters:
            f.update()
        
        self.sparkles = [s for s in self.sparkles if s.update()]
        while len(self.sparkles) < 20:
            self.sparkles.append(GoldenSparkle(self.width, self.height))
        
        self.confetti = [c for c in self.confetti if c.update()]
        self.dust_particles = [d for d in self.dust_particles if d.update()]
        
        # Update result timer
        if self.result_timer > 0:
            self.result_timer -= dt
        
        # Handle countdown
        if self.countdown > 0:
            self.countdown_timer -= dt
            if self.countdown_timer <= 0:
                self.countdown -= 1
                self.countdown_timer = 1.0
                if self.countdown == 0:
                    self.is_racing = True
            return
        
        # Update race
        if self.is_racing:
            finish_position = len(self.finish_order) + 1
            
            for horse in self.horses:
                if horse.update(dt, True, self.finish_line):
                    horse.finish_position = finish_position
                    self.finish_order.append(horse)
                    finish_position += 1
                
                # Add dust particles behind running horses
                if not horse.finished and random.random() < 0.3:
                    y = horse.get_y(self.track_top, self.lane_height)
                    self.dust_particles.append(DustParticle(horse.x - 20, y))
            
            # Check if race is over
            if len(self.finish_order) == 5:
                self.is_racing = False
                self.race_finished = True
                self._calculate_winnings()
    
    def _calculate_winnings(self):
        """Calculate winnings based on selected horse's position"""
        selected = self.horses[self.selected_horse]
        position = selected.finish_position
        
        if position == 1:
            self.winnings = self.bet_amount * 5
            self.result_message = f"[1ST] {selected.name} WON! +{self.winnings} tokens!"
            # Spawn confetti
            for _ in range(50):
                self.confetti.append(ConfettiParticle(self.width // 2, self.height // 3))
        elif position == 2:
            self.winnings = self.bet_amount * 2
            self.result_message = f"[2ND] {selected.name} came 2nd! +{self.winnings} tokens!"
            for _ in range(25):
                self.confetti.append(ConfettiParticle(self.width // 2, self.height // 3))
        elif position == 3:
            self.winnings = self.bet_amount
            self.result_message = f"[3RD] {selected.name} came 3rd! +{self.winnings} tokens!"
        elif position == 4:
            self.winnings = 0
            self.result_message = f"{selected.name} came 4th. You lose your bet."
        else:
            self.winnings = 0
            self.result_message = f"{selected.name} came last. You lose your bet."
        
        self.tokens += self.winnings
        self.result_timer = 4.0
    
    def draw(self, surface: pygame.Surface):
        """Draw the complete game"""
        # Background gradient
        for y in range(self.height):
            ratio = y / self.height
            r = int(20 + ratio * 30)
            g = int(60 + ratio * 20)
            b = int(20 + ratio * 30)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.width, y))
        
        # Draw floaters (background)
        for f in self.floaters:
            f.draw(surface)
        
        # Draw sparkles
        for s in self.sparkles:
            s.draw(surface)
        
        # Draw title
        title_text = self.font_large.render("~ HORSE RACING ~", True, GOLD)
        title_rect = title_text.get_rect(centerx=self.width // 2, top=15)
        
        # Title shadow
        shadow = self.font_large.render("~ HORSE RACING ~", True, (50, 50, 50))
        surface.blit(shadow, (title_rect.x + 2, title_rect.y + 2))
        surface.blit(title_text, title_rect)
        
        # Draw token counter
        token_text = self.font_medium.render(f"Tokens: {self.tokens}", True, GOLD)
        surface.blit(token_text, (self.width - 180, 20))
        
        # Draw payout info
        payout_y = 55
        payout_texts = ["1st: 5x", "2nd: 2x", "3rd: 1x"]
        payout_colors = [GOLD, (192, 192, 192), (205, 127, 50)]
        for i, (text, color) in enumerate(zip(payout_texts, payout_colors)):
            payout_surf = self.font_tiny.render(text, True, color)
            surface.blit(payout_surf, (self.width - 170 + i * 55, payout_y))
        
        # Draw race track
        self._draw_track(surface)
        
        # Draw dust particles
        for d in self.dust_particles:
            d.draw(surface)
        
        # Draw horses
        for horse in self.horses:
            self._draw_horse(surface, horse)
        
        # Draw horse selection panel
        self._draw_selection_panel(surface)
        
        # Draw countdown
        if self.countdown > 0:
            countdown_text = self.font_large.render(str(self.countdown), True, RED)
            rect = countdown_text.get_rect(center=(self.width // 2, self.height // 2))
            
            # Pulsing effect
            scale = 1.0 + 0.3 * math.sin(self.countdown_timer * math.pi)
            scaled = pygame.transform.scale(countdown_text, 
                                           (int(countdown_text.get_width() * scale),
                                            int(countdown_text.get_height() * scale)))
            scaled_rect = scaled.get_rect(center=rect.center)
            surface.blit(scaled, scaled_rect)
        
        # Draw GO! when race starts
        if self.is_racing and not self.finish_order:
            go_text = self.font_large.render("GO!", True, NEON_GREEN)
            go_rect = go_text.get_rect(center=(self.width // 2, 100))
            surface.blit(go_text, go_rect)
        
        # Draw betting controls
        self._draw_controls(surface)
        
        # Draw result message
        if self.result_timer > 0 and self.result_message:
            self._draw_result(surface)
        
        # Draw confetti (foreground)
        for c in self.confetti:
            c.draw(surface)
        
        # Draw instructions
        inst_text = self.font_tiny.render("SPACE = Start Race | UP/DOWN = Change Bet | 1-5 = Select Horse | ESC = Exit", True, (200, 200, 200))
        inst_rect = inst_text.get_rect(centerx=self.width // 2, bottom=self.height - 10)
        surface.blit(inst_text, inst_rect)
    
    def _draw_track(self, surface: pygame.Surface):
        """Draw the race track"""
        # Track background
        track_rect = pygame.Rect(70, self.track_top - 10, self.width - 80, self.track_height + 20)
        pygame.draw.rect(surface, TRACK_BROWN, track_rect, border_radius=10)
        pygame.draw.rect(surface, (100, 60, 30), track_rect, width=3, border_radius=10)
        
        # Lane lines
        for i in range(1, 5):
            y = self.track_top + i * self.lane_height
            pygame.draw.line(surface, (120, 80, 40), (75, y), (self.width - 15, y), 2)
        
        # Start line
        pygame.draw.line(surface, WHITE, (self.track_start, self.track_top - 5), 
                        (self.track_start, self.track_top + self.track_height + 5), 4)
        start_text = self.font_tiny.render("START", True, WHITE)
        surface.blit(start_text, (self.track_start - 20, self.track_top - 25))
        
        # Finish line (checkered pattern)
        finish_x = self.finish_line
        for i in range(10):
            for j in range(2):
                color = WHITE if (i + j) % 2 == 0 else BLACK
                rect = pygame.Rect(finish_x + j * 8, self.track_top + i * (self.track_height // 10), 8, self.track_height // 10)
                pygame.draw.rect(surface, color, rect)
        
        finish_text = self.font_tiny.render("FINISH", True, WHITE)
        surface.blit(finish_text, (finish_x - 10, self.track_top - 25))
    
    def _draw_horse(self, surface: pygame.Surface, horse: Horse):
        """Draw a horse on the track"""
        y = horse.get_y(self.track_top, self.lane_height)
        
        if horse.image:
            # Draw the horse image
            img = horse.image
            # Add bouncing animation when racing
            if self.is_racing and not horse.finished:
                bounce = int(3 * math.sin(horse.animation_frame * math.pi / 2))
                y += bounce
            
            rect = img.get_rect(center=(int(horse.x), y))
            surface.blit(img, rect)
        else:
            # Fallback: draw colored circle
            bounce = 0
            if self.is_racing and not horse.finished:
                bounce = int(3 * math.sin(horse.animation_frame * math.pi / 2))
            
            pygame.draw.circle(surface, horse.color, (int(horse.x), y + bounce), 20)
            pygame.draw.circle(surface, WHITE, (int(horse.x), y + bounce), 20, 2)
        
        # Draw position label if finished
        if horse.finished:
            pos_text = self.font_tiny.render(f"#{horse.finish_position}", True, GOLD)
            surface.blit(pos_text, (int(horse.x) + 30, y - 10))
    
    def _draw_selection_panel(self, surface: pygame.Surface):
        """Draw horse selection buttons"""
        for i, (horse, btn) in enumerate(zip(self.horses, self.horse_buttons)):
            # Background
            color = horse.color if i == self.selected_horse else (60, 60, 60)
            pygame.draw.rect(surface, color, btn, border_radius=8)
            
            # Border (gold if selected)
            border_color = GOLD if i == self.selected_horse else (100, 100, 100)
            border_width = 3 if i == self.selected_horse else 1
            pygame.draw.rect(surface, border_color, btn, width=border_width, border_radius=8)
            
            # Horse number
            num_text = self.font_small.render(str(i + 1), True, WHITE)
            num_rect = num_text.get_rect(center=btn.center)
            surface.blit(num_text, num_rect)
    
    def _draw_controls(self, surface: pygame.Surface):
        """Draw betting controls"""
        btn_y = self.height - 80
        
        # Bet display
        bet_text = self.font_small.render(f"Bet: {self.bet_amount}", True, WHITE)
        bet_rect = bet_text.get_rect(midleft=(self.width // 2 - 170, btn_y + 20))
        surface.blit(bet_text, bet_rect)
        
        # Minus button
        pygame.draw.rect(surface, (80, 80, 100), self.bet_minus_button, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.bet_minus_button, width=2, border_radius=8)
        minus_text = self.font_medium.render("-", True, WHITE)
        minus_rect = minus_text.get_rect(center=self.bet_minus_button.center)
        surface.blit(minus_text, minus_rect)
        
        # Plus button
        pygame.draw.rect(surface, (80, 80, 100), self.bet_plus_button, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.bet_plus_button, width=2, border_radius=8)
        plus_text = self.font_medium.render("+", True, WHITE)
        plus_rect = plus_text.get_rect(center=self.bet_plus_button.center)
        surface.blit(plus_text, plus_rect)
        
        # Start/New Race button
        can_start = not self.is_racing and self.countdown == 0 and self.tokens >= self.bet_amount
        btn_color = (0, 150, 0) if can_start else (80, 80, 80)
        btn_text = "NEW RACE" if self.race_finished else "START"
        pygame.draw.rect(surface, btn_color, self.start_button, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.start_button, width=2, border_radius=8)
        start_text = self.font_small.render(btn_text, True, WHITE)
        start_rect = start_text.get_rect(center=self.start_button.center)
        surface.blit(start_text, start_rect)
        
        # All-in button
        pygame.draw.rect(surface, CASINO_RED, self.allin_button, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.allin_button, width=2, border_radius=8)
        allin_text = self.font_small.render("ALL IN", True, WHITE)
        allin_rect = allin_text.get_rect(center=self.allin_button.center)
        surface.blit(allin_text, allin_rect)
        
        # Selected horse display
        selected = self.horses[self.selected_horse]
        horse_text = self.font_small.render(f"Your Horse: {selected.name}", True, selected.color)
        horse_rect = horse_text.get_rect(midleft=(20, btn_y + 20))
        surface.blit(horse_text, horse_rect)
    
    def _draw_result(self, surface: pygame.Surface):
        """Draw race result message"""
        # Semi-transparent background
        overlay = pygame.Surface((self.width, 80), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, self.height // 2 - 40))
        
        # Result text
        text_color = GOLD if self.winnings > 0 else RED
        result_text = self.font_medium.render(self.result_message, True, text_color)
        result_rect = result_text.get_rect(center=(self.width // 2, self.height // 2))
        surface.blit(result_text, result_rect)
        
        # Finish order
        if self.race_finished:
            order_y = self.height // 2 + 25
            order_text = "Finish: "
            for i, horse in enumerate(self.finish_order):
                order_text += f"{i+1}. {horse.name}  "
            order_surf = self.font_tiny.render(order_text, True, WHITE)
            order_rect = order_surf.get_rect(center=(self.width // 2, order_y))
            surface.blit(order_surf, order_rect)
    
    def handle_click(self, pos: tuple):
        """Handle mouse click"""
        # Horse selection
        for i, btn in enumerate(self.horse_buttons):
            if btn.collidepoint(pos):
                self.select_horse(i)
                return
        
        # Bet controls
        if self.bet_minus_button.collidepoint(pos):
            self.change_bet(False)
        elif self.bet_plus_button.collidepoint(pos):
            self.change_bet(True)
        elif self.start_button.collidepoint(pos):
            if self.race_finished:
                self.reset_race()
            else:
                self.start_race()
        elif self.allin_button.collidepoint(pos):
            self.all_in()
    
    def handle_keypress(self, key: int):
        """Handle keypress"""
        if key == pygame.K_SPACE:
            if self.race_finished:
                self.reset_race()
            else:
                self.start_race()
        elif key == pygame.K_UP:
            self.change_bet(True)
        elif key == pygame.K_DOWN:
            self.change_bet(False)
        elif key == pygame.K_1:
            self.select_horse(0)
        elif key == pygame.K_2:
            self.select_horse(1)
        elif key == pygame.K_3:
            self.select_horse(2)
        elif key == pygame.K_4:
            self.select_horse(3)
        elif key == pygame.K_5:
            self.select_horse(4)


# =============================================================================
# FUNCTIONS CALLED FROM MAIN.PY
# =============================================================================

def draw_horsegame_scene(surface: pygame.Surface, game_state: dict, font: pygame.font.Font) -> dict:
    """Draw and update horse racing game on the given surface."""
    if "game" not in game_state:
        tokens = game_state.get("tokens", 100)
        surf_w, surf_h = surface.get_size()
        game = HorseRacingGame(surf_w, surf_h)
        game.tokens = tokens
        
        game_state = {
            "game": game,
            "tokens": tokens,
        }
    
    game: HorseRacingGame = game_state["game"]
    game.update()
    game.draw(surface)
    
    # Sync tokens
    game_state["tokens"] = game.tokens
    
    return game_state


def handle_horsegame_click(game_state: dict, pos: tuple) -> dict:
    """Handle mouse click in horse racing game."""
    if "game" in game_state:
        game_state["game"].handle_click(pos)
    return game_state


def handle_horsegame_keypress(game_state: dict, key: int) -> dict:
    """Handle keypress in horse racing game."""
    if "game" in game_state:
        game_state["game"].handle_keypress(key)
    return game_state


def change_horsegame_bet(game_state: dict, increase: bool) -> dict:
    """Change horse racing bet amount."""
    if "game" in game_state:
        game_state["game"].change_bet(increase)
    return game_state
