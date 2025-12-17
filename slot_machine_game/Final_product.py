import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Slot machine settings
REEL_WIDTH = 150
REEL_HEIGHT = 150
SYMBOL_SIZE = 120
NUM_REELS = 3
SPIN_DURATION = 2000  # milliseconds
SPIN_SPEED_INCREMENT = 300  # Each reel stops 300ms after the previous
BOUNCE_DURATION = 200  # Bounce effect duration in ms
COOLDOWN_DURATION = 1000  # 1 second cooldown after results

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
BRIGHT_GOLD = (255, 223, 0)
CASINO_RED = (220, 20, 60)
NEON_GREEN = (57, 255, 20)
CYAN = (0, 255, 255)
DEEP_RED = (139, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (147, 112, 219)
PINK = (255, 192, 203)
YELLOW = (255, 255, 0)
DEEP_PURPLE = (75, 0, 130)
DARK_BLUE = (0, 0, 50)
NEON_PINK = (255, 16, 240)
NEON_BLUE = (4, 217, 255)

class CasinoFloater:
    """Floating casino elements like chips, cards, dice"""
    def __init__(self):
        self.x = random. randint(0, SCREEN_WIDTH)
        self.y = random. randint(0, SCREEN_HEIGHT)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1, -0.3)
        self.type = random.choice(['chip', 'spade', 'heart', 'diamond', 'club', 'dollar', 'dice'])
        self.size = random.randint(15, 30)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.alpha = random.randint(30, 80)
        
    def update(self):
        self.x += self.vx
        self.y += self. vy
        self.rotation += self.rotation_speed
        
        # Wrap around screen
        if self.y < -50:
            self.y = SCREEN_HEIGHT + 50
            self.x = random.randint(0, SCREEN_WIDTH)
        if self.x < -50:
            self. x = SCREEN_WIDTH + 50
        elif self.x > SCREEN_WIDTH + 50:
            self. x = -50
    
    def draw(self, screen):
        # Create a surface with alpha
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        if self.type == 'chip': 
            # Casino chip
            pygame.draw.circle(surf, (255, 0, 0, self.alpha), (self.size, self.size), self.size)
            pygame.draw.circle(surf, (255, 255, 255, self.alpha), (self.size, self.size), self.size, 3)
        elif self.type == 'spade':
            # Spade symbol (simplified)
            color = (255, 255, 255, self.alpha)
            points = [
                (self.size, self.size - 10),
                (self. size - 8, self.size + 5),
                (self.size + 8, self.size + 5)
            ]
            pygame.draw.polygon(surf, color, points)
            pygame.draw.circle(surf, color, (self.size - 5, self.size), 6)
            pygame.draw.circle(surf, color, (self.size + 5, self.size), 6)
        elif self.type == 'heart':
            # Heart symbol
            color = (255, 20, 60, self.alpha)
            pygame.draw.circle(surf, color, (self.size - 5, self.size - 3), 7)
            pygame.draw.circle(surf, color, (self. size + 5, self.size - 3), 7)
            points = [
                (self.size - 12, self.size),
                (self.size, self.size + 12),
                (self. size + 12, self.size)
            ]
            pygame.draw.polygon(surf, color, points)
        elif self.type == 'diamond':
            # Diamond symbol
            color = (255, 20, 60, self.alpha)
            points = [
                (self.size, self.size - 10),
                (self.size - 8, self.size),
                (self.size, self.size + 10),
                (self.size + 8, self.size)
            ]
            pygame.draw.polygon(surf, color, points)
        elif self.type == 'club':
            # Club symbol
            color = (255, 255, 255, self.alpha)
            pygame.draw.circle(surf, color, (self.size, self.size - 5), 6)
            pygame.draw.circle(surf, color, (self.size - 6, self.size + 2), 6)
            pygame. draw.circle(surf, color, (self.size + 6, self.size + 2), 6)
        elif self.type == 'dollar':
            # Dollar sign
            font = pygame.font.Font(None, self.size)
            text = font.render('$', True, (0, 255, 100, self.alpha))
            surf.blit(text, (self.size - 8, self.size - 10))
        elif self.type == 'dice':
            # Dice
            rect = pygame.Rect(self. size - 8, self.size - 8, 16, 16)
            pygame.draw.rect(surf, (255, 255, 255, self.alpha), rect, border_radius=3)
            pygame.draw.circle(surf, (0, 0, 0, self.alpha), (self.size, self.size), 2)
        
        screen.blit(surf, (int(self.x - self.size), int(self.y - self. size)))

class LightRay:
    """Rotating spotlight effect"""
    def __init__(self, angle_offset):
        self.angle = angle_offset
        self.speed = 0.5
        self.length = 800
        self.width = 40
        
    def update(self):
        self.angle += self.speed
        if self.angle >= 360:
            self.angle -= 360
    
    def draw(self, screen):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Calculate end point
        rad = math.radians(self. angle)
        end_x = center_x + math.cos(rad) * self.length
        end_y = center_y + math.sin(rad) * self.length
        
        # Create light ray surface with alpha
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Draw light ray as a polygon with gradient effect
        angle_rad = math.radians(self.angle)
        perpendicular = angle_rad + math.pi / 2
        
        # Calculate 4 corners of the light beam
        hw = self.width / 2
        points = [
            (center_x + math.cos(perpendicular) * hw, center_y + math.sin(perpendicular) * hw),
            (center_x - math.cos(perpendicular) * hw, center_y - math.sin(perpendicular) * hw),
            (end_x - math.cos(perpendicular) * hw, end_y - math.sin(perpendicular) * hw),
            (end_x + math.cos(perpendicular) * hw, end_y + math.sin(perpendicular) * hw)
        ]
        
        pygame.draw.polygon(surf, (255, 215, 0, 15), points)
        screen.blit(surf, (0, 0))

class GoldenSparkle:
    """Small golden sparkle particles"""
    def __init__(self):
        self.x = random. randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.5, 0.5)
        self.lifetime = random.randint(60, 180)
        self.age = 0
        self.max_brightness = random.randint(150, 255)
        
    def update(self):
        self.x += self.vx
        self.y += self. vy
        self.age += 1
        
        # Wrap around
        if self.x < 0: self.x = SCREEN_WIDTH
        if self.x > SCREEN_WIDTH: self.x = 0
        if self.y < 0: self.y = SCREEN_HEIGHT
        if self. y > SCREEN_HEIGHT: self.y = 0
        
        return self.age < self.lifetime
    
    def draw(self, screen):
        progress = self.age / self.lifetime
        brightness = int(self.max_brightness * (1 - progress))
        size = 1 if progress > 0.5 else 2
        color = (brightness, brightness, int(brightness * 0.7))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)

class Confetti:
    """Single confetti particle"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-8, -3)
        self.gravity = 0.3
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.color = random.choice([GOLD, RED, GREEN, CYAN, PURPLE, PINK, YELLOW, ORANGE])
        self.size = random. randint(4, 8)
        self.lifetime = random.randint(60, 120)  # frames
        self.age = 0
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self. vy += self.gravity
        self.rotation += self.rotation_speed
        self.age += 1
        return self.age < self.lifetime
    
    def draw(self, screen):
        alpha = 1 - (self.age / self.lifetime)
        if alpha > 0:
            points = []
            for i in range(4):
                angle = math.radians(self.rotation + i * 90)
                px = self.x + math.cos(angle) * self.size
                py = self.y + math.sin(angle) * self.size
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points)

class StarBurst:
    """Star burst effect for wins"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 0
        self.max_radius = 100
        self.growing = True
        self.lifetime = 30
        self.age = 0
        
    def update(self):
        if self.growing:
            self. radius += 5
            if self.radius >= self.max_radius:
                self.growing = False
        self.age += 1
        return self.age < self.lifetime
    
    def draw(self, screen):
        alpha = 1 - (self.age / self.lifetime)
        if alpha > 0:
            for i in range(8):
                angle = math.radians(i * 45 + self.age * 5)
                end_x = self.x + math.cos(angle) * self.radius
                end_y = self.y + math.sin(angle) * self.radius
                pygame.draw.line(screen, BRIGHT_GOLD, (self. x, self.y), (end_x, end_y), 3)

class SlotMachine: 
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pygame Casino - Slot Machine")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_title = pygame.font.Font(None, 80)
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 42)
        self.font_small = pygame.font. Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 22)
        self.font_button = pygame.font.Font(None, 44)
        
        # Load images
        self.load_images()
        
        # Game state
        self.symbols = ['cherry', 'lemon', 'orange', 'plum', 'bell', 'bar', 'seven']
        self.visible_symbols = [[random.choice(self.symbols) for _ in range(3)] for _ in range(NUM_REELS)]
        self.spinning = False
        self.spin_start_time = 0
        self.reel_stop_times = []
        self.credits = 10000
        self.bet_amount = 500
        self.last_win = 0
        
        # Cooldown system
        self.cooldown_active = False
        self.cooldown_end_time = 0
        
        # Animation
        self.spin_offsets = [0, 0, 0]
        self.spin_speeds = [15, 15, 15]
        self. reel_stopped = [False, False, False]
        self.bounce_start_times = [0, 0, 0]
        self.is_bouncing = [False, False, False]
        
        # Symbol queue for smooth scrolling
        self.symbol_queues = [[random.choice(self.symbols) for _ in range(20)] for _ in range(NUM_REELS)]
        
        # Title animation
        self.title_pulse = 0
        
        # Win effects
        self.confetti_particles = []
        self.star_bursts = []
        self.win_text_scale = 1.0
        self.win_text_pulse = 0
        self.show_win_effect = False
        
        # Enhanced background effects
        self.casino_floaters = [CasinoFloater() for _ in range(25)]
        self.light_rays = [LightRay(i * 90) for i in range(4)]
        self.golden_sparkles = [GoldenSparkle() for _ in range(100)]
        self.vignette_pulse = 0
        self.neon_border_offset = 0
        
    def load_images(self):
        """Load all symbol images"""
        self.images = {}
        symbols = ['cherry', 'lemon', 'orange', 'plum', 'bell', 'bar', 'seven']
        
        for symbol in symbols:
            try:
                img = pygame.image.load(f'images/{symbol}.png')
                self.images[symbol] = pygame.transform.scale(img, (SYMBOL_SIZE, SYMBOL_SIZE))
            except: 
                self.images[symbol] = self.create_placeholder(symbol)
    
    def create_placeholder(self, symbol):
        """Create a placeholder image for symbols"""
        surface = pygame.Surface((SYMBOL_SIZE, SYMBOL_SIZE))
        colors = {
            'cherry': (255, 0, 0),
            'lemon': (255, 255, 0),
            'orange': (255, 165, 0),
            'plum': (128, 0, 128),
            'bell': (192, 192, 192),
            'bar': (139, 69, 19),
            'seven': (255, 215, 0)
        }
        surface.fill(colors. get(symbol, (100, 100, 100)))
        pygame.draw.rect(surface, BLACK, surface.get_rect(), 3)
        
        font = pygame.font.Font(None, 32)
        text = font.render(symbol[: 3]. upper(), True, BLACK)
        text_rect = text.get_rect(center=(SYMBOL_SIZE // 2, SYMBOL_SIZE // 2))
        surface.blit(text, text_rect)
        
        return surface
    
    def create_confetti_burst(self, x, y, amount=50):
        """Create a burst of confetti at position"""
        for _ in range(amount):
            self.confetti_particles.append(Confetti(x, y))
    
    def create_star_burst(self, x, y):
        """Create a star burst effect"""
        self.star_bursts.append(StarBurst(x, y))
    
    def can_spin(self):
        """Check if player can spin (not in cooldown, has credits, not already spinning)"""
        current_time = pygame.time.get_ticks()
        
        # Check cooldown
        if self.cooldown_active and current_time < self.cooldown_end_time:
            return False
        
        # Clear cooldown if time has passed
        if self.cooldown_active and current_time >= self.cooldown_end_time:
            self.cooldown_active = False
        
        # Check other conditions
        if self.spinning or self.credits < self.bet_amount:
            return False
        
        return True
    
    def get_cooldown_remaining(self):
        """Get remaining cooldown time in seconds"""
        if not self.cooldown_active:
            return 0
        
        current_time = pygame.time.get_ticks()
        remaining_ms = max(0, self.cooldown_end_time - current_time)
        return remaining_ms / 1000.0
    
    def spin(self):
        """Start spinning the reels"""
        if not self.can_spin():
            return
        
        self. credits -= self.bet_amount
        self.spinning = True
        self.spin_start_time = pygame.time.get_ticks()
        self.last_win = 0
        self.show_win_effect = False
        
        # Set stop times for each reel (staggered)
        self.reel_stop_times = [
            self.spin_start_time + SPIN_DURATION,
            self.spin_start_time + SPIN_DURATION + SPIN_SPEED_INCREMENT,
            self.spin_start_time + SPIN_DURATION + SPIN_SPEED_INCREMENT * 2
        ]
        
        # Initialize spin speeds and states
        self.spin_speeds = [15, 15, 15]
        self.spin_offsets = [0, 0, 0]
        self.reel_stopped = [False, False, False]
        self.is_bouncing = [False, False, False]
        
        # Generate new symbol queues for smooth scrolling
        for i in range(NUM_REELS):
            self.symbol_queues[i] = [random.choice(self.symbols) for _ in range(20)]
            self.visible_symbols[i] = [
                random.choice(self.symbols),
                random.choice(self. symbols),
                random.choice(self.symbols)
            ]
    
    def update_spin(self):
        """Update spinning animation"""
        if not self.spinning:
            return
        
        current_time = pygame.time. get_ticks()
        all_stopped = True
        
        for i in range(NUM_REELS):
            if current_time < self.reel_stop_times[i]:
                self.spin_offsets[i] += self.spin_speeds[i]
                
                if self.spin_offsets[i] >= REEL_HEIGHT:
                    self.spin_offsets[i] = 0
                    self.symbol_queues[i]. append(self.symbol_queues[i].pop(0))
                
                all_stopped = False
                self.reel_stopped[i] = False
            elif not self.reel_stopped[i]:
                self.reel_stopped[i] = True
                self.is_bouncing[i] = True
                self.bounce_start_times[i] = current_time
                self.spin_offsets[i] = 0
            elif self.is_bouncing[i]:
                bounce_elapsed = current_time - self.bounce_start_times[i]
                if bounce_elapsed < BOUNCE_DURATION:
                    bounce_progress = bounce_elapsed / BOUNCE_DURATION
                    self.spin_offsets[i] = int(20 * abs(1 - 2 * bounce_progress))
                    all_stopped = False
                else:
                    self.is_bouncing[i] = False
                    self.spin_offsets[i] = 0
        
        if all_stopped and not any(self.is_bouncing):
            self.spinning = False
            self.check_win()
            
            # Start cooldown timer AFTER results are shown
            self.cooldown_active = True
            self.cooldown_end_time = pygame.time.get_ticks() + COOLDOWN_DURATION
    
    def check_win(self):
        """Check if the player won"""
        # Get middle row symbols
        symbol_0 = self.visible_symbols[0][1]
        symbol_1 = self.visible_symbols[1][1]
        symbol_2 = self.visible_symbols[2][1]
        
        # Count matching symbols
        num_matches = 0
        if symbol_0 == symbol_1 == symbol_2:
            num_matches = 3
        elif symbol_0 == symbol_1 or symbol_0 == symbol_2 or symbol_1 == symbol_2:
            num_matches = 2
        
        # Process wins
        if num_matches == 3:
            # THREE OF A KIND - BIG WIN! 
            symbol = symbol_0
            payouts = {
                'seven': 100,
                'bar': 50,
                'bell': 30,
                'plum': 20,
                'orange': 15,
                'lemon': 10,
                'cherry': 5
            }
            multiplier = payouts. get(symbol, 5)
            self.last_win = self.bet_amount * multiplier
            self.credits += self.last_win
            
            # BIG WIN EFFECTS! 
            self.show_win_effect = True
            self.win_text_pulse = 0
            
            # Create confetti bursts from each reel
            reel_spacing = (SCREEN_WIDTH - (REEL_WIDTH * NUM_REELS)) // (NUM_REELS + 1)
            for i in range(NUM_REELS):
                x_pos = reel_spacing + i * (REEL_WIDTH + reel_spacing) + REEL_WIDTH // 2
                y_pos = 120 + REEL_HEIGHT  # Updated to match new y_start
                self.create_confetti_burst(x_pos, y_pos, amount=30)
                self.create_star_burst(x_pos, y_pos)
            
            # Extra confetti from center
            self.create_confetti_burst(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, amount=40)
            
        elif num_matches == 2:
            # TWO OF A KIND - Small win
            self.last_win = self.bet_amount * 2
            self.credits += self.last_win
            self.show_win_effect = True
            self.win_text_pulse = 0
            
            # Smaller confetti burst
            self.create_confetti_burst(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, amount=20)
    
    def update_effects(self):
        """Update all visual effects"""
        # Update confetti
        self.confetti_particles = [p for p in self.confetti_particles if p.update()]
        
        # Update star bursts
        self.star_bursts = [s for s in self.star_bursts if s.update()]
        
        # Update win text animation
        if self.show_win_effect:
            self.win_text_pulse += 0.15
            self.win_text_scale = 1.0 + 0.15 * abs(math.sin(self.win_text_pulse))
        
        # Update casino background effects
        for floater in self.casino_floaters:
            floater.update()
        
        for ray in self.light_rays:
            ray.update()
        
        self.golden_sparkles = [s for s in self.golden_sparkles if s.update()]
        
        # Add new sparkles to maintain count
        while len(self.golden_sparkles) < 100:
            self.golden_sparkles.append(GoldenSparkle())
        
        self.vignette_pulse += 0.05
        self.neon_border_offset = (self.neon_border_offset + 2) % 20
    
    def draw_background(self):
        """Draw animated casino-style background"""
        # Rich gradient background (deep red/purple to dark)
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(DEEP_RED[0] * (1 - progress) + DARK_BLUE[0] * progress)
            g = int(DEEP_RED[1] * (1 - progress) + DARK_BLUE[1] * progress)
            b = int(DEEP_RED[2] * (1 - progress) + DEEP_PURPLE[2] * progress)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw rotating light rays
        for ray in self.light_rays:
            ray.draw(self.screen)
        
        # Draw golden sparkles
        for sparkle in self.golden_sparkles:
            sparkle.draw(self. screen)
        
        # Draw floating casino elements
        for floater in self.casino_floaters:
            floater.draw(self. screen)
        
        # Draw pulsing vignette effect (darker edges)
        vignette_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        vignette_alpha = int(100 + 30 * math.sin(self. vignette_pulse))
        
        # Top and bottom gradients
        for i in range(100):
            alpha = int((vignette_alpha * i) / 100)
            pygame.draw.line(vignette_surf, (0, 0, 0, alpha), (0, i), (SCREEN_WIDTH, i))
            pygame.draw.line(vignette_surf, (0, 0, 0, alpha), (0, SCREEN_HEIGHT - i), (SCREEN_WIDTH, SCREEN_HEIGHT - i))
        
        # Side gradients
        for i in range(100):
            alpha = int((vignette_alpha * i) / 100)
            pygame.draw.line(vignette_surf, (0, 0, 0, alpha), (i, 0), (i, SCREEN_HEIGHT))
            pygame. draw.line(vignette_surf, (0, 0, 0, alpha), (SCREEN_WIDTH - i, 0), (SCREEN_WIDTH - i, SCREEN_HEIGHT))
        
        self.screen.blit(vignette_surf, (0, 0))
        
        # Draw animated neon border
        border_colors = [NEON_PINK, NEON_BLUE, NEON_GREEN, GOLD]
        for i, color in enumerate(border_colors):
            offset = (self.neon_border_offset + i * 5) % 20
            pygame. draw.rect(self.screen, color, (offset, offset, SCREEN_WIDTH - offset * 2, SCREEN_HEIGHT - offset * 2), 2)
    
    def draw_reel(self, reel_index, x_pos):
        """Draw a single reel with glow effect"""
        y_start = 120  # Reels positioned nicely centered
        
        # Draw glow effect behind reel
        glow_rect = pygame.Rect(x_pos - 3, y_start - 3, REEL_WIDTH + 6, REEL_HEIGHT * 3 + 6)
        for i in range(3):
            glow_color = (GOLD[0] // (i + 2), GOLD[1] // (i + 2), GOLD[2] // (i + 2))
            pygame.draw.rect(self.screen, glow_color, glow_rect. inflate(i * 2, i * 2), 2)
        
        # Draw reel background
        reel_rect = pygame.Rect(x_pos, y_start, REEL_WIDTH, REEL_HEIGHT * 3)
        pygame.draw.rect(self.screen, WHITE, reel_rect)
        pygame.draw.rect(self.screen, GOLD, reel_rect, 5)
        
        # Create a clipping surface
        reel_surface = pygame.Surface((REEL_WIDTH, REEL_HEIGHT * 3))
        reel_surface.fill(WHITE)
        
        symbol_x = (REEL_WIDTH - SYMBOL_SIZE) // 2
        
        if self.reel_stopped[reel_index] and not self.is_bouncing[reel_index]:
            for i in range(3):
                y_pos = (REEL_HEIGHT - SYMBOL_SIZE) // 2 + i * REEL_HEIGHT
                reel_surface.blit(self.images[self.visible_symbols[reel_index][i]], (symbol_x, y_pos))
        
        elif self.is_bouncing[reel_index]:
            for i in range(3):
                y_pos = (REEL_HEIGHT - SYMBOL_SIZE) // 2 + i * REEL_HEIGHT
                if i == 1:
                    y_pos += self.spin_offsets[reel_index]
                reel_surface. blit(self.images[self.visible_symbols[reel_index][i]], (symbol_x, y_pos))
        
        else:
            for i in range(5):
                symbol = self.symbol_queues[reel_index][i % len(self.symbol_queues[reel_index])]
                y_pos = (REEL_HEIGHT - SYMBOL_SIZE) // 2 + i * REEL_HEIGHT - self.spin_offsets[reel_index]
                
                if -REEL_HEIGHT <= y_pos <= REEL_HEIGHT * 3:
                    reel_surface.blit(self.images[symbol], (symbol_x, y_pos))
        
        self.screen.blit(reel_surface, (x_pos, y_start))
        pygame.draw.rect(self.screen, GOLD, reel_rect, 5)
        
        # Highlight winning row with animated glow
        if self.reel_stopped[reel_index] and not self.is_bouncing[reel_index]: 
            highlight_rect = pygame.Rect(x_pos, y_start + REEL_HEIGHT, REEL_WIDTH, REEL_HEIGHT)
            glow_intensity = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.005))
            glow_color = (0, glow_intensity, 0)
            pygame.draw. rect(self.screen, glow_color, highlight_rect, 4)
    
    def draw_fancy_title(self):
        """Draw an animated, colorful title"""
        self.title_pulse = (self.title_pulse + 0.1) % (2 * math.pi)
        pulse_scale = 1 + 0.05 * math.sin(self.title_pulse)
        
        title_text = "SLOT MACHINE"
        title_font_size = int(80 * pulse_scale)
        title_font = pygame. font.Font(None, title_font_size)
        title_x = SCREEN_WIDTH // 2
        
        # Shadow
        shadow = title_font.render(title_text, True, BLACK)
        shadow_rect = shadow. get_rect(center=(title_x + 4, 54))
        self.screen.blit(shadow, shadow_rect)
        
        # Red outline
        outline = title_font.render(title_text, True, CASINO_RED)
        outline_rect = outline.get_rect(center=(title_x, 50))
        self.screen.blit(outline, outline_rect)
        
        # Main gold
        title = title_font.render(title_text, True, GOLD)
        title_rect = title.get_rect(center=(title_x, 50))
        self.screen.blit(title, title_rect)
        
        # Highlight
        highlight = title_font. render(title_text, True, BRIGHT_GOLD)
        highlight_rect = highlight.get_rect(center=(title_x, 48))
        
        clip_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 45)
        self.screen.set_clip(clip_rect)
        self.screen.blit(highlight, highlight_rect)
        self.screen.set_clip(None)
        
        # Sparkles
        sparkle_positions = [
            (title_x - 180, 30),
            (title_x + 180, 30),
            (title_x - 200, 60),
            (title_x + 200, 60)
        ]
        
        sparkle_size = int(3 + 2 * abs(math.sin(self.title_pulse * 2)))
        for pos in sparkle_positions:
            pygame.draw.circle(self.screen, WHITE, pos, sparkle_size)
    
    def draw_ui(self):
        """Draw the user interface"""
        self.draw_fancy_title()
        
        # Credits with smaller, compact box
        credits_box = pygame.Rect(15, 15, 110, 50)
        pygame.draw.rect(self.screen, (40, 40, 40), credits_box, border_radius=8)
        pygame.draw.rect(self.screen, CYAN, credits_box, 2, border_radius=8)
        
        credits_label = self.font_tiny.render("CREDITS", True, CYAN)
        self.screen.blit(credits_label, (20, 18))
        
        credits_text = self.font_small.render(f"${self.credits:,}", True, NEON_GREEN)
        self.screen.blit(credits_text, (20, 38))
        
        # Bet with smaller, compact box
        bet_box = pygame.Rect(15, 70, 80, 45)
        pygame.draw.rect(self.screen, (40, 40, 40), bet_box, border_radius=8)
        pygame.draw.rect(self.screen, CASINO_RED, bet_box, 2, border_radius=8)
        
        bet_label = self.font_tiny.render("BET", True, CYAN)
        self.screen.blit(bet_label, (20, 73))
        
        bet_text = self.font_small.render(f"${self.bet_amount}", True, CASINO_RED)
        self.screen.blit(bet_text, (20, 90))
        
        # Win message with animation
        if self.last_win > 0 and self.show_win_effect:
            win_font_size = int(56 * self.win_text_scale)
            win_font = pygame.font.Font(None, win_font_size)
            
            # Animated background box
            win_bg_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 110, 400, 70)
            pygame.draw.rect(self.screen, GOLD, win_bg_rect, border_radius=15)
            pygame.draw.rect(self.screen, NEON_GREEN, win_bg_rect, 4, border_radius=15)
            
            # Pulsing glow
            glow_intensity = int(50 + 50 * math. sin(self.win_text_pulse * 2))
            for i in range(3):
                glow_rect = win_bg_rect.inflate(i * 4, i * 4)
                glow_color = (0, glow_intensity, 0)
                pygame.draw.rect(self.screen, glow_color, glow_rect, 2, border_radius=15)
            
            win_text = win_font.render(f"WIN ${self.last_win:,}!", True, BLACK)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 75))
            self.screen.blit(win_text, win_rect)
        
        # Spin button
        button_rect = pygame.Rect(SCREEN_WIDTH - 150, 25, 130, 55)
        
        # Determine button color and state
        if self.cooldown_active:
            button_color = ORANGE  # Orange during cooldown
        elif self.spinning or self.credits < self.bet_amount:
            button_color = RED
        else:
            button_color = NEON_GREEN
        
        shadow_rect = button_rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, BLACK, shadow_rect, border_radius=10)
        
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD, button_rect, 4, border_radius=10)
        
        # Show cooldown timer on button if active (FIXED - NO SPACE!)
        if self.cooldown_active:
            cooldown_remaining = self.get_cooldown_remaining()
            button_text = self.font_small.render(f"{cooldown_remaining:.1f}s", True, WHITE)
        else:
            button_text = self.font_button.render("SPIN", True, BLACK if button_color == NEON_GREEN else WHITE)
        
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Cooldown hint text (below button)
        if self.cooldown_active:
            cooldown_hint = self.font_tiny.render("Cooldown.. .", True, ORANGE)
            cooldown_hint_rect = cooldown_hint.get_rect(center=(SCREEN_WIDTH - 85, 90))
            self.screen.blit(cooldown_hint, cooldown_hint_rect)
        else:
            space_hint = self.font_tiny.render("SPACE", True, LIGHT_GRAY)
            space_hint_rect = space_hint. get_rect(center=(SCREEN_WIDTH - 85, 90))
            self.screen.blit(space_hint, space_hint_rect)
        
        return button_rect
    
    def draw(self):
        """Draw everything"""
        self.draw_background()
        
        # Draw star bursts (behind reels)
        for star in self.star_bursts:
            star.draw(self.screen)
        
        # Draw reels
        reel_spacing = (SCREEN_WIDTH - (REEL_WIDTH * NUM_REELS)) // (NUM_REELS + 1)
        for i in range(NUM_REELS):
            x_pos = reel_spacing + i * (REEL_WIDTH + reel_spacing)
            self.draw_reel(i, x_pos)
        
        # Draw confetti (on top of everything)
        for confetti in self.confetti_particles:
            confetti.draw(self.screen)
        
        # Draw UI
        button_rect = self.draw_ui()
        
        pygame.display.flip()
        return button_rect
    
    def handle_events(self, button_rect):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    self.spin()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self. spin()
                elif event.key == pygame.K_UP and not self.spinning and not self.cooldown_active:
                    self.bet_amount = min(self.bet_amount + 100, 5000)
                elif event.key == pygame.K_DOWN and not self.spinning and not self.cooldown_active:
                    self.bet_amount = max(self.bet_amount - 100, 100)
        
        return True
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            self.update_spin()
            self.update_effects()
            button_rect = self.draw()
            running = self.handle_events(button_rect)
            self.clock.tick(FPS)
        
        pygame. quit()
        sys.exit()

if __name__ == "__main__": 
    game = SlotMachine()
    game.run()