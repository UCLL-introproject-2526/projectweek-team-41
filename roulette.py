"""
European Roulette Wheel - Deterministic Implementation
======================================================
The result is derived ONLY from the ball's final angle relative to the wheel.
No hidden randomizer after spin starts.
"""

import pygame
import math
import random

# =============================================================================
# CONSTANTS
# =============================================================================

# Window settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
FPS = 60

# Wheel settings
WHEEL_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
WHEEL_RADIUS = 300
POCKET_RADIUS = 250  # Inner radius where numbers are drawn
BALL_ORBIT_RADIUS = 270  # Where the ball orbits

# European roulette pockets in clockwise order (as seen on a real wheel)
POCKETS = [
    0,
    32, 15, 19, 4, 21, 2, 25, 17, 34, 6,
    27, 13, 36, 11, 30, 8, 23, 10, 5,
    24, 16, 33, 1, 20, 14, 31, 9, 22,
    18, 29, 7, 28, 12, 35, 3, 26
]

NUM_POCKETS = len(POCKETS)  # 37
POCKET_ANGLE = 360.0 / NUM_POCKETS  # ~9.73 degrees per pocket

# Red numbers in European roulette (official rules)
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

# Colors
COLOR_GREEN = (0, 128, 0)
COLOR_RED = (180, 30, 30)
COLOR_BLACK = (30, 30, 30)
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (218, 165, 32)
COLOR_BALL = (255, 255, 255)
COLOR_BACKGROUND = (20, 60, 20)
BRIGHT_GOLD = (255, 223, 0)
CYAN = (0, 255, 255)
PURPLE = (147, 112, 219)
PINK = (255, 192, 203)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Physics settings
WHEEL_FRICTION = 0.995  # How fast wheel slows down (closer to 1 = slower)
BALL_FRICTION = 0.990   # How fast ball slows down (closer to 1 = slower)
BALL_STOP_THRESHOLD = 0.1  # Ball "lands" when speed drops below this


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
        self.type = random.choice(["chip", "spade", "heart", "diamond", "club", "dollar"])
        self.size = random.randint(15, 30)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.alpha = random.randint(30, 80)

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
            pygame.draw.circle(surf, (255, 255, 255, self.alpha), (self.size, self.size), self.size, 3)
        elif self.type == "spade":
            color = (255, 255, 255, self.alpha)
            points = [(self.size, self.size - 10), (self.size - 8, self.size + 5), (self.size + 8, self.size + 5)]
            pygame.draw.polygon(surf, color, points)
            pygame.draw.circle(surf, color, (self.size - 5, self.size), 6)
            pygame.draw.circle(surf, color, (self.size + 5, self.size), 6)
        elif self.type == "heart":
            color = (255, 20, 60, self.alpha)
            pygame.draw.circle(surf, color, (self.size - 5, self.size - 3), 7)
            pygame.draw.circle(surf, color, (self.size + 5, self.size - 3), 7)
            points = [(self.size - 12, self.size), (self.size, self.size + 12), (self.size + 12, self.size)]
            pygame.draw.polygon(surf, color, points)
        elif self.type == "diamond":
            color = (255, 20, 60, self.alpha)
            points = [(self.size, self.size - 10), (self.size - 8, self.size), (self.size, self.size + 10), (self.size + 8, self.size)]
            pygame.draw.polygon(surf, color, points)
        elif self.type == "club":
            color = (255, 255, 255, self.alpha)
            pygame.draw.circle(surf, color, (self.size, self.size - 5), 6)
            pygame.draw.circle(surf, color, (self.size - 6, self.size + 2), 6)
            pygame.draw.circle(surf, color, (self.size + 6, self.size + 2), 6)
        elif self.type == "dollar":
            font = pygame.font.Font(None, self.size)
            text = font.render("$", True, (0, 255, 100, self.alpha))
            surf.blit(text, (self.size - 8, self.size - 10))

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

        if self.x < 0: self.x = self.width
        if self.x > self.width: self.x = 0
        if self.y < 0: self.y = self.height
        if self.y > self.height: self.y = 0

        if self.age >= self.lifetime:
            self.age = 0
            self.x = random.randint(0, self.width)
            self.y = random.randint(0, self.height)

    def draw(self, screen):
        progress = self.age / self.lifetime
        brightness = int(self.max_brightness * (1 - progress * 0.5))
        size = 1 if progress > 0.5 else 2
        color = (brightness, brightness, int(brightness * 0.7))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)


class LightRay:
    """Rotating spotlight effect"""

    def __init__(self, width, height, angle_offset):
        self.width = width
        self.height = height
        self.angle = angle_offset
        self.speed = 0.5
        self.length = max(width, height)
        self.ray_width = 40

    def update(self):
        self.angle += self.speed
        if self.angle >= 360:
            self.angle -= 360

    def draw(self, screen):
        center_x = self.width // 2
        center_y = self.height // 2

        rad = math.radians(self.angle)
        end_x = center_x + math.cos(rad) * self.length
        end_y = center_y + math.sin(rad) * self.length

        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        perpendicular = rad + math.pi / 2
        hw = self.ray_width / 2
        points = [
            (center_x + math.cos(perpendicular) * hw, center_y + math.sin(perpendicular) * hw),
            (center_x - math.cos(perpendicular) * hw, center_y - math.sin(perpendicular) * hw),
            (end_x - math.cos(perpendicular) * hw, end_y - math.sin(perpendicular) * hw),
            (end_x + math.cos(perpendicular) * hw, end_y + math.sin(perpendicular) * hw),
        ]

        pygame.draw.polygon(surf, (255, 215, 0, 15), points)
        screen.blit(surf, (0, 0))


class Confetti:
    """Single confetti particle for wins"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-8, -3)
        self.gravity = 0.3
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.color = random.choice([COLOR_GOLD, COLOR_RED, (0, 255, 0), CYAN, PURPLE, PINK, YELLOW, ORANGE])
        self.size = random.randint(4, 8)
        self.lifetime = random.randint(60, 120)
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.rotation += self.rotation_speed
        self.age += 1
        return self.age < self.lifetime

    def draw(self, screen):
        if self.age < self.lifetime:
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
            self.radius += 5
            if self.radius >= self.max_radius:
                self.growing = False
        self.age += 1
        return self.age < self.lifetime

    def draw(self, screen):
        if self.age < self.lifetime:
            for i in range(8):
                angle = math.radians(i * 45 + self.age * 5)
                end_x = self.x + math.cos(angle) * self.radius
                end_y = self.y + math.sin(angle) * self.radius
                pygame.draw.line(screen, BRIGHT_GOLD, (self.x, self.y), (end_x, end_y), 3)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_pocket_color(number):
    """
    Returns the color for a pocket number.
    0 = Green, Red numbers = Red, otherwise Black.
    """
    if number == 0:
        return COLOR_GREEN
    elif number in RED_NUMBERS:
        return COLOR_RED
    else:
        return COLOR_BLACK


def calculate_result(ball_angle, wheel_angle):
    """
    Calculate which pocket the ball landed in based on angles.
    
    This is the ONLY place where the result is determined.
    It uses pure angle math with no randomization.
    
    Args:
        ball_angle: The ball's absolute angle in degrees (0-360)
        wheel_angle: The wheel's rotation angle in degrees
    
    Returns:
        tuple: (pocket_index, result_number)
    """
    # Calculate ball's position relative to the wheel
    # This gives us which pocket the ball is in, independent of wheel rotation
    relative_angle = (ball_angle - wheel_angle) % 360
    
    # Determine which pocket index this angle falls into
    pocket_index = int(relative_angle // POCKET_ANGLE)
    
    # Clamp to valid range (safety check)
    pocket_index = pocket_index % NUM_POCKETS
    
    # Get the actual number from the pocket
    result_number = POCKETS[pocket_index]
    
    return pocket_index, result_number


# =============================================================================
# GAME STATE
# =============================================================================

class RouletteGame:
    """
    Main game class handling all state, physics, and rendering.
    """
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("European Roulette - Deterministic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # State variables
        self.reset()
    
    def reset(self):
        """Reset the game state for a new spin."""
        # Wheel state
        self.wheel_angle = 0.0  # Current rotation of the wheel (degrees)
        self.wheel_speed = 0.0  # Angular velocity (degrees per frame)
        
        # Ball state
        self.ball_angle = 0.0   # Ball's position around the wheel (degrees)
        self.ball_speed = 0.0   # Ball's angular velocity (degrees per frame)
        self.ball_active = False  # Is the ball spinning?
        self.ball_landed = False  # Has the ball stopped?
        
        # When ball lands, store its position RELATIVE to the wheel
        # so it can rotate with the wheel
        self.ball_relative_angle = 0.0
        
        # Result
        self.result_number = None
        self.result_pocket_index = None
    
    def spin(self):
        """
        Start a new spin with random initial velocities.
        
        NOTE: The randomness is ONLY in the initial speeds.
        Once the spin starts, physics is deterministic.
        """
        self.reset()
        
        # Random initial wheel speed (positive = clockwise)
        self.wheel_speed = random.uniform(3.0, 6.0)
        
        # Ball spins in OPPOSITE direction (negative = counter-clockwise)
        self.ball_speed = -random.uniform(8.0, 12.0)
        
        # Random starting position for the ball
        self.ball_angle = random.uniform(0, 360)
        
        self.ball_active = True
        self.ball_landed = False
        self.result_number = None
        self.result_pocket_index = None
    
    # =========================================================================
    # PHYSICS UPDATE - Separated from rendering
    # =========================================================================
    
    def update_physics(self):
        """
        Update all physics: wheel rotation and ball movement.
        This is pure physics with no randomization.
        """
        # Update wheel rotation (wheel always keeps spinning)
        self.wheel_angle = (self.wheel_angle + self.wheel_speed) % 360
        self.wheel_speed *= WHEEL_FRICTION
        
        # Update ball if active
        if self.ball_active:
            if not self.ball_landed:
                # Ball is still spinning freely
                self.ball_angle = (self.ball_angle + self.ball_speed) % 360
                
                # Apply friction to ball
                self.ball_speed *= BALL_FRICTION
                
                # Check if ball has stopped
                if abs(self.ball_speed) < BALL_STOP_THRESHOLD:
                    self.ball_landed = True
                    self.ball_speed = 0
                    
                    # Store ball's position RELATIVE to the wheel
                    # This is the angle within the wheel's frame of reference
                    self.ball_relative_angle = (self.ball_angle - self.wheel_angle) % 360
                    
                    # Calculate result using ONLY angle math
                    # The ball's relative angle determines which pocket it's in
                    self.result_pocket_index, self.result_number = calculate_result(
                        self.ball_angle, self.wheel_angle
                    )
            else:
                # Ball has landed - it now rotates WITH the wheel
                # Update ball's absolute angle based on its fixed relative position
                self.ball_angle = (self.ball_relative_angle + self.wheel_angle) % 360
    
    # =========================================================================
    # RENDERING - Separated from physics
    # =========================================================================
    
    def draw_wheel(self):
        """
        Draw the roulette wheel with all pockets.
        The wheel rotates based on wheel_angle.
        """
        cx, cy = WHEEL_CENTER
        
        # Draw outer rim
        pygame.draw.circle(self.screen, COLOR_GOLD, WHEEL_CENTER, WHEEL_RADIUS + 10)
        pygame.draw.circle(self.screen, COLOR_BLACK, WHEEL_CENTER, WHEEL_RADIUS)
        
        # Draw each pocket wedge
        for i, number in enumerate(POCKETS):
            # Calculate the start and end angles for this pocket
            # Account for wheel rotation
            start_angle = math.radians(i * POCKET_ANGLE + self.wheel_angle)
            end_angle = math.radians((i + 1) * POCKET_ANGLE + self.wheel_angle)
            mid_angle = (start_angle + end_angle) / 2
            
            # Get pocket color
            color = get_pocket_color(number)
            
            # Draw filled wedge using polygon
            points = [WHEEL_CENTER]
            num_arc_points = 10
            for j in range(num_arc_points + 1):
                angle = start_angle + (end_angle - start_angle) * j / num_arc_points
                x = cx + WHEEL_RADIUS * math.cos(angle)
                y = cy + WHEEL_RADIUS * math.sin(angle)
                points.append((x, y))
            
            pygame.draw.polygon(self.screen, color, points)
            
            # Draw wedge border lines for clarity
            line_start_x = cx + 50 * math.cos(start_angle)
            line_start_y = cy + 50 * math.sin(start_angle)
            line_end_x = cx + WHEEL_RADIUS * math.cos(start_angle)
            line_end_y = cy + WHEEL_RADIUS * math.sin(start_angle)
            pygame.draw.line(self.screen, COLOR_GOLD, 
                           (line_start_x, line_start_y), 
                           (line_end_x, line_end_y), 2)
            
            # Draw number in the pocket
            text_radius = POCKET_RADIUS
            text_x = cx + text_radius * math.cos(mid_angle)
            text_y = cy + text_radius * math.sin(mid_angle)
            
            # Render number text
            text = self.small_font.render(str(number), True, COLOR_WHITE)
            text_rect = text.get_rect(center=(text_x, text_y))
            self.screen.blit(text, text_rect)
        
        # Draw center hub
        pygame.draw.circle(self.screen, COLOR_GOLD, WHEEL_CENTER, 50)
        pygame.draw.circle(self.screen, COLOR_BLACK, WHEEL_CENTER, 45)
    
    def draw_ball(self):
        """
        Draw the ball at its current position.
        The ball position is absolute (not relative to wheel).
        """
        if not self.ball_active:
            return
        
        cx, cy = WHEEL_CENTER
        
        # Calculate ball position from its angle
        ball_rad = math.radians(self.ball_angle)
        ball_x = cx + BALL_ORBIT_RADIUS * math.cos(ball_rad)
        ball_y = cy + BALL_ORBIT_RADIUS * math.sin(ball_rad)
        
        # Draw ball with highlight
        pygame.draw.circle(self.screen, COLOR_BALL, (int(ball_x), int(ball_y)), 12)
        pygame.draw.circle(self.screen, (200, 200, 200), (int(ball_x) - 3, int(ball_y) - 3), 4)
    
    def draw_ui(self):
        """Draw user interface elements."""
        # Instructions
        instructions = [
            "SPACE - Spin the wheel",
            "R - Reset",
            "ESC - Quit"
        ]
        
        y = 20
        for text in instructions:
            surface = self.small_font.render(text, True, COLOR_WHITE)
            self.screen.blit(surface, (20, y))
            y += 25
        
        # Show result if ball has landed
        if self.ball_landed and self.result_number is not None:
            # Result display
            result_color = get_pocket_color(self.result_number)
            result_text = f"Result: {self.result_number}"
            
            # Draw result box
            text_surface = self.font.render(result_text, True, COLOR_WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
            
            # Background box
            box_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, result_color, box_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLOR_GOLD, box_rect, 3, border_radius=10)
            
            self.screen.blit(text_surface, text_rect)
            
            # Debug info (shows the math is correct)
            debug_lines = [
                f"Ball relative angle: {self.ball_relative_angle:.1f}°",
                f"Pocket index: {self.result_pocket_index}",
                f"Ball is in pocket: {POCKETS[self.result_pocket_index]}"
            ]
            
            y = SCREEN_HEIGHT - 120
            for line in debug_lines:
                surface = self.small_font.render(line, True, COLOR_WHITE)
                self.screen.blit(surface, (20, y))
                y += 22
        
        # Show current speeds while spinning
        elif self.ball_active and not self.ball_landed:
            speed_text = f"Ball speed: {abs(self.ball_speed):.2f}"
            surface = self.small_font.render(speed_text, True, COLOR_WHITE)
            self.screen.blit(surface, (20, SCREEN_HEIGHT - 40))
    
    def draw_pocket_highlight(self):
        """
        When ball has landed, highlight the pocket it's in.
        This visually confirms the result matches the ball position.
        """
        if not self.ball_landed or self.result_pocket_index is None:
            return
        
        cx, cy = WHEEL_CENTER
        
        # Calculate the pocket's current visual position (accounting for wheel rotation)
        start_angle = math.radians(self.result_pocket_index * POCKET_ANGLE + self.wheel_angle)
        end_angle = math.radians((self.result_pocket_index + 1) * POCKET_ANGLE + self.wheel_angle)
        
        # Draw highlight arc around the winning pocket
        points = []
        num_arc_points = 10
        for j in range(num_arc_points + 1):
            angle = start_angle + (end_angle - start_angle) * j / num_arc_points
            x = cx + (WHEEL_RADIUS + 5) * math.cos(angle)
            y = cy + (WHEEL_RADIUS + 5) * math.sin(angle)
            points.append((x, y))
        
        if len(points) >= 2:
            pygame.draw.lines(self.screen, COLOR_WHITE, False, points, 4)
    
    def render(self):
        """Main render method - draws everything."""
        self.screen.fill(COLOR_BACKGROUND)
        
        self.draw_wheel()
        self.draw_pocket_highlight()
        self.draw_ball()
        self.draw_ui()
        
        pygame.display.flip()
    
    # =========================================================================
    # MAIN GAME LOOP
    # =========================================================================
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.spin()
                    elif event.key == pygame.K_r:
                        self.reset()
            
            # Update physics
            self.update_physics()
            
            # Render
            self.render()
            
            # Cap framerate
            self.clock.tick(FPS)
        
        pygame.quit()


# =============================================================================
# ENTRY POINT
# =============================================================================

def draw_roulette_scene(surface: pygame.Surface, game_state: dict, font: pygame.font.Font) -> dict:
    """
    Draw and update roulette game on the given surface.
    
    Args:
        surface: The pygame surface to draw on
        game_state: Dictionary containing the roulette state (or empty for first call)
        font: Font to use for rendering
    
    Returns:
        Updated game_state dictionary
    """
    # Initialize state if needed
    if "initialized" not in game_state:
        tokens = game_state.get("tokens", 100)  # Get tokens passed from app
        surf_w, surf_h = surface.get_size()
        game_state = {
            "initialized": True,
            "wheel_angle": 0.0,
            "wheel_speed": 0.0,
            "ball_angle": 0.0,
            "ball_speed": 0.0,
            "ball_active": False,
            "ball_landed": False,
            "ball_relative_angle": 0.0,
            "result_number": None,
            "result_pocket_index": None,
            "tokens": tokens,
            "current_bet": 10,  # Current bet amount
            "bet_type": "red",  # "red", "black", "green", "odd", "even", or "number"
            "bet_number": None,  # Specific number to bet on (0-36)
            "number_input": "",  # Text input for number betting
            "number_input_active": False,  # Whether number input is focused
            "bet_placed": False,  # Whether a bet is active
            "winnings": 0,  # Last win amount
            # VFX
            "floaters": [CasinoFloater(surf_w, surf_h) for _ in range(20)],
            "sparkles": [GoldenSparkle(surf_w, surf_h) for _ in range(50)],
            "light_rays": [LightRay(surf_w, surf_h, i * 90) for i in range(4)],
            "confetti": [],
            "starbursts": [],
            # Button rects (will be set during drawing)
            "buttons": {},
        }
    
    # Get surface dimensions and calculate scale
    surf_w, surf_h = surface.get_size()
    scale = min(surf_w / SCREEN_WIDTH, surf_h / SCREEN_HEIGHT) * 0.9
    center_x, center_y = surf_w // 2, surf_h // 2
    
    # Scaled dimensions
    wheel_radius = int(WHEEL_RADIUS * scale)
    pocket_radius = int(POCKET_RADIUS * scale)
    ball_orbit_radius = int(BALL_ORBIT_RADIUS * scale)
    
    # Update physics
    game_state["wheel_angle"] = (game_state["wheel_angle"] + game_state["wheel_speed"]) % 360
    game_state["wheel_speed"] *= WHEEL_FRICTION
    
    if game_state["ball_active"]:
        if not game_state["ball_landed"]:
            game_state["ball_angle"] = (game_state["ball_angle"] + game_state["ball_speed"]) % 360
            game_state["ball_speed"] *= BALL_FRICTION
            
            if abs(game_state["ball_speed"]) < BALL_STOP_THRESHOLD:
                game_state["ball_landed"] = True
                game_state["ball_speed"] = 0
                game_state["ball_relative_angle"] = (game_state["ball_angle"] - game_state["wheel_angle"]) % 360
                game_state["result_pocket_index"], game_state["result_number"] = calculate_result(
                    game_state["ball_angle"], game_state["wheel_angle"]
                )
                
                # Calculate winnings if bet was placed
                if game_state["bet_placed"]:
                    result = game_state["result_number"]
                    bet_type = game_state["bet_type"]
                    bet_amount = game_state["current_bet"]
                    bet_number = game_state.get("bet_number")
                    won = False
                    multiplier = 0
                    
                    # Check for number bet first (highest payout)
                    if bet_type == "number" and bet_number is not None and result == bet_number:
                        won = True
                        multiplier = 36  # 35:1 payout + original bet
                    elif bet_type == "red" and result in RED_NUMBERS:
                        won = True
                        multiplier = 2
                    elif bet_type == "black" and result not in RED_NUMBERS and result != 0:
                        won = True
                        multiplier = 2
                    elif bet_type == "green" and result == 0:
                        won = True
                        multiplier = 35
                    elif bet_type == "odd" and result != 0 and result % 2 == 1:
                        won = True
                        multiplier = 2
                    elif bet_type == "even" and result != 0 and result % 2 == 0:
                        won = True
                        multiplier = 2
                    
                    if won:
                        winnings = bet_amount * multiplier
                        game_state["tokens"] += winnings
                        game_state["winnings"] = winnings
                        # Spawn win VFX
                        for _ in range(30):
                            game_state["confetti"].append(Confetti(center_x, center_y))
                        game_state["starbursts"].append(StarBurst(center_x, center_y))
                    else:
                        game_state["winnings"] = -bet_amount
                    
                    game_state["bet_placed"] = False
        else:
            game_state["ball_angle"] = (game_state["ball_relative_angle"] + game_state["wheel_angle"]) % 360
    
    # Update win VFX
    game_state["confetti"] = [c for c in game_state.get("confetti", []) if c.update()]
    game_state["starbursts"] = [s for s in game_state.get("starbursts", []) if s.update()]
    
    # Draw background
    surface.fill(COLOR_BACKGROUND)
    
    # Update and draw VFX (background layer)
    for floater in game_state.get("floaters", []):
        floater.update()
        floater.draw(surface)
    
    for sparkle in game_state.get("sparkles", []):
        sparkle.update()
        sparkle.draw(surface)
    
    for ray in game_state.get("light_rays", []):
        ray.update()
        ray.draw(surface)
    
    # Draw outer rim
    pygame.draw.circle(surface, COLOR_GOLD, (center_x, center_y), wheel_radius + int(10 * scale))
    pygame.draw.circle(surface, COLOR_BLACK, (center_x, center_y), wheel_radius)
    
    # Draw each pocket wedge
    small_font = pygame.font.Font(None, max(12, int(24 * scale)))
    for i, number in enumerate(POCKETS):
        start_angle = math.radians(i * POCKET_ANGLE + game_state["wheel_angle"])
        end_angle = math.radians((i + 1) * POCKET_ANGLE + game_state["wheel_angle"])
        mid_angle = (start_angle + end_angle) / 2
        
        color = get_pocket_color(number)
        
        points = [(center_x, center_y)]
        for j in range(11):
            angle = start_angle + (end_angle - start_angle) * j / 10
            x = center_x + wheel_radius * math.cos(angle)
            y = center_y + wheel_radius * math.sin(angle)
            points.append((x, y))
        
        pygame.draw.polygon(surface, color, points)
        
        # Draw number
        text_x = center_x + pocket_radius * math.cos(mid_angle)
        text_y = center_y + pocket_radius * math.sin(mid_angle)
        text = small_font.render(str(number), True, COLOR_WHITE)
        text_rect = text.get_rect(center=(text_x, text_y))
        surface.blit(text, text_rect)
    
    # Draw center hub
    pygame.draw.circle(surface, COLOR_GOLD, (center_x, center_y), int(50 * scale))
    pygame.draw.circle(surface, COLOR_BLACK, (center_x, center_y), int(45 * scale))
    
    # Draw ball
    if game_state["ball_active"]:
        ball_rad = math.radians(game_state["ball_angle"])
        ball_x = center_x + ball_orbit_radius * math.cos(ball_rad)
        ball_y = center_y + ball_orbit_radius * math.sin(ball_rad)
        pygame.draw.circle(surface, COLOR_BALL, (int(ball_x), int(ball_y)), int(12 * scale))
    
    # Draw UI
    hint_font = pygame.font.Font(None, max(16, int(24 * scale)))
    bet_font = pygame.font.Font(None, max(20, int(28 * scale)))
    btn_font = pygame.font.Font(None, max(18, int(22 * scale)))
    
    # Store button rects for click detection
    buttons = {}
    
    # Button dimensions
    btn_w, btn_h = 70, 30
    btn_spacing = 5
    
    # Left side - Bet type buttons
    btn_x = 15
    btn_y = 20
    
    # Spin button (larger)
    spin_rect = pygame.Rect(btn_x, btn_y, btn_w + 30, btn_h + 5)
    spin_color = (50, 150, 50) if not game_state.get("ball_active", False) else (80, 80, 80)
    pygame.draw.rect(surface, spin_color, spin_rect, border_radius=8)
    pygame.draw.rect(surface, COLOR_GOLD, spin_rect, 2, border_radius=8)
    spin_text = btn_font.render("SPIN", True, COLOR_WHITE)
    surface.blit(spin_text, spin_text.get_rect(center=spin_rect.center))
    buttons["spin"] = spin_rect
    btn_y += btn_h + 15
    
    # Reset button
    reset_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    pygame.draw.rect(surface, (100, 50, 50), reset_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE, reset_rect, 1, border_radius=6)
    reset_text = btn_font.render("Reset", True, COLOR_WHITE)
    surface.blit(reset_text, reset_text.get_rect(center=reset_rect.center))
    buttons["reset"] = reset_rect
    btn_y += btn_h + 15
    
    # Bet amount controls
    amount_label = hint_font.render("Bet Amount:", True, COLOR_WHITE)
    surface.blit(amount_label, (btn_x, btn_y))
    btn_y += 20
    
    # Minus button
    minus_rect = pygame.Rect(btn_x, btn_y, 35, btn_h)
    pygame.draw.rect(surface, (80, 80, 120), minus_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE, minus_rect, 1, border_radius=6)
    minus_text = btn_font.render("-", True, COLOR_WHITE)
    surface.blit(minus_text, minus_text.get_rect(center=minus_rect.center))
    buttons["bet_minus"] = minus_rect
    
    # Plus button
    plus_rect = pygame.Rect(btn_x + 45, btn_y, 35, btn_h)
    pygame.draw.rect(surface, (80, 80, 120), plus_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE, plus_rect, 1, border_radius=6)
    plus_text = btn_font.render("+", True, COLOR_WHITE)
    surface.blit(plus_text, plus_text.get_rect(center=plus_rect.center))
    buttons["bet_plus"] = plus_rect
    btn_y += btn_h + 15
    
    # Bet type label
    type_label = hint_font.render("Bet Type:", True, COLOR_WHITE)
    surface.blit(type_label, (btn_x, btn_y))
    btn_y += 20
    
    # Color bet buttons (row 1)
    bet_type = game_state.get("bet_type", "red")
    
    # Red button
    red_rect = pygame.Rect(btn_x, btn_y, 50, btn_h)
    red_color = (200, 50, 50) if bet_type == "red" else (120, 30, 30)
    pygame.draw.rect(surface, red_color, red_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE if bet_type == "red" else (80, 80, 80), red_rect, 2, border_radius=6)
    red_text = btn_font.render("RED", True, COLOR_WHITE)
    surface.blit(red_text, red_text.get_rect(center=red_rect.center))
    buttons["red"] = red_rect
    
    # Black button
    black_rect = pygame.Rect(btn_x + 55, btn_y, 50, btn_h)
    black_color = (60, 60, 60) if bet_type == "black" else (30, 30, 30)
    pygame.draw.rect(surface, black_color, black_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE if bet_type == "black" else (80, 80, 80), black_rect, 2, border_radius=6)
    black_text = btn_font.render("BLK", True, COLOR_WHITE)
    surface.blit(black_text, black_text.get_rect(center=black_rect.center))
    buttons["black"] = black_rect
    btn_y += btn_h + btn_spacing
    
    # Green button
    green_rect = pygame.Rect(btn_x, btn_y, 50, btn_h)
    green_color = (30, 150, 30) if bet_type == "green" else (20, 80, 20)
    pygame.draw.rect(surface, green_color, green_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE if bet_type == "green" else (80, 80, 80), green_rect, 2, border_radius=6)
    green_text = btn_font.render("GRN", True, COLOR_WHITE)
    surface.blit(green_text, green_text.get_rect(center=green_rect.center))
    buttons["green"] = green_rect
    btn_y += btn_h + btn_spacing
    
    # Odd/Even buttons
    odd_rect = pygame.Rect(btn_x, btn_y, 50, btn_h)
    odd_color = (80, 80, 160) if bet_type == "odd" else (50, 50, 100)
    pygame.draw.rect(surface, odd_color, odd_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE if bet_type == "odd" else (80, 80, 80), odd_rect, 2, border_radius=6)
    odd_text = btn_font.render("ODD", True, COLOR_WHITE)
    surface.blit(odd_text, odd_text.get_rect(center=odd_rect.center))
    buttons["odd"] = odd_rect
    
    even_rect = pygame.Rect(btn_x + 55, btn_y, 50, btn_h)
    even_color = (160, 80, 80) if bet_type == "even" else (100, 50, 50)
    pygame.draw.rect(surface, even_color, even_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE if bet_type == "even" else (80, 80, 80), even_rect, 2, border_radius=6)
    even_text = btn_font.render("EVN", True, COLOR_WHITE)
    surface.blit(even_text, even_text.get_rect(center=even_rect.center))
    buttons["even"] = even_rect
    btn_y += btn_h + 15
    
    # Number bet section
    num_label = hint_font.render("Bet on #:", True, COLOR_WHITE)
    surface.blit(num_label, (btn_x, btn_y))
    btn_y += 20
    
    # Number input field
    input_active = game_state.get("number_input_active", False)
    number_input = game_state.get("number_input", "")
    input_rect = pygame.Rect(btn_x, btn_y, 60, btn_h)
    input_bg = (60, 60, 80) if input_active else (40, 40, 50)
    pygame.draw.rect(surface, input_bg, input_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_GOLD if input_active else (80, 80, 100), input_rect, 2, border_radius=6)
    
    # Display input text or placeholder
    if number_input:
        input_text = btn_font.render(number_input, True, COLOR_WHITE)
    else:
        input_text = btn_font.render("0-36", True, (100, 100, 120))
    surface.blit(input_text, input_text.get_rect(center=input_rect.center))
    buttons["number_input"] = input_rect
    
    # Confirm number button
    confirm_rect = pygame.Rect(btn_x + 65, btn_y, 40, btn_h)
    confirm_color = (50, 120, 50) if bet_type == "number" else (40, 80, 40)
    pygame.draw.rect(surface, confirm_color, confirm_rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_WHITE if bet_type == "number" else (80, 80, 80), confirm_rect, 2, border_radius=6)
    confirm_text = btn_font.render("OK", True, COLOR_WHITE)
    surface.blit(confirm_text, confirm_text.get_rect(center=confirm_rect.center))
    buttons["confirm_number"] = confirm_rect
    btn_y += btn_h + 10
    
    # Show current number bet if active
    bet_number = game_state.get("bet_number")
    if bet_type == "number" and bet_number is not None:
        num_bet_text = hint_font.render(f"Betting on: {bet_number}", True, COLOR_GOLD)
        surface.blit(num_bet_text, (btn_x, btn_y))
    
    # Store buttons in game state for click handling
    game_state["buttons"] = buttons
    
    # Token and bet info on right
    tokens = game_state.get("tokens", 0)
    current_bet = game_state.get("current_bet", 10)
    
    # Token display
    token_text = f"Tokens: {tokens}"
    token_surf = bet_font.render(token_text, True, COLOR_GOLD)
    surface.blit(token_surf, (surf_w - 150, 20))
    
    # Current bet display
    bet_text = f"Bet: {current_bet}"
    bet_surf = bet_font.render(bet_text, True, COLOR_WHITE)
    surface.blit(bet_surf, (surf_w - 150, 50))
    
    # Bet type display with color
    bet_colors = {"red": COLOR_RED, "black": COLOR_BLACK, "green": COLOR_GREEN, "odd": (100, 100, 200), "even": (200, 100, 100), "number": COLOR_GOLD}
    if bet_type == "number" and bet_number is not None:
        type_text = f"Type: #{bet_number}"
    else:
        type_text = f"Type: {bet_type.upper()}"
    type_surf = bet_font.render(type_text, True, bet_colors.get(bet_type, COLOR_WHITE))
    surface.blit(type_surf, (surf_w - 150, 80))
    
    # Show result
    if game_state["ball_landed"] and game_state["result_number"] is not None:
        result_color = get_pocket_color(game_state["result_number"])
        result_text = f"Result: {game_state['result_number']}"
        text_surface = font.render(result_text, True, COLOR_WHITE)
        text_rect = text_surface.get_rect(center=(center_x, 50))
        box_rect = text_rect.inflate(40, 20)
        pygame.draw.rect(surface, result_color, box_rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_GOLD, box_rect, 3, border_radius=10)
        surface.blit(text_surface, text_rect)
        
        # Show winnings/loss
        winnings = game_state.get("winnings", 0)
        if winnings > 0:
            win_text = f"+{winnings} tokens!"
            win_color = (50, 255, 50)
        elif winnings < 0:
            win_text = f"{winnings} tokens"
            win_color = (255, 100, 100)
        else:
            win_text = ""
            win_color = COLOR_WHITE
        
        if win_text:
            win_surf = font.render(win_text, True, win_color)
            win_rect = win_surf.get_rect(center=(center_x, surf_h - 50))
            surface.blit(win_surf, win_rect)
    
    # Draw ESC hint at bottom right
    esc_hint = hint_font.render("ESC - Back to Casino", True, (180, 180, 180))
    surface.blit(esc_hint, (surf_w - 160, surf_h - 25))
    
    # Draw win VFX on top
    for starburst in game_state.get("starbursts", []):
        starburst.draw(surface)
    for confetti in game_state.get("confetti", []):
        confetti.draw(surface)
    
    return game_state


def spin_roulette(game_state: dict) -> dict:
    """Start a new spin with bet."""
    # Check if player has enough tokens
    current_bet = game_state.get("current_bet", 10)
    tokens = game_state.get("tokens", 0)
    
    if tokens < current_bet:
        return game_state  # Not enough tokens
    
    if game_state.get("ball_active", False):
        return game_state  # Already spinning
    
    # Deduct bet
    game_state["tokens"] = tokens - current_bet
    game_state["bet_placed"] = True
    game_state["winnings"] = 0
    
    # Start spin
    game_state["wheel_speed"] = random.uniform(3.0, 6.0)
    game_state["ball_speed"] = -random.uniform(8.0, 12.0)
    game_state["ball_angle"] = random.uniform(0, 360)
    game_state["ball_active"] = True
    game_state["ball_landed"] = False
    game_state["result_number"] = None
    game_state["result_pocket_index"] = None
    return game_state


def reset_roulette(game_state: dict) -> dict:
    """Reset the roulette state (keeps tokens)."""
    tokens = game_state.get("tokens", 100)
    current_bet = game_state.get("current_bet", 10)
    bet_type = game_state.get("bet_type", "red")
    
    game_state["wheel_angle"] = 0.0
    game_state["wheel_speed"] = 0.0
    game_state["ball_angle"] = 0.0
    game_state["ball_speed"] = 0.0
    game_state["ball_active"] = False
    game_state["ball_landed"] = False
    game_state["ball_relative_angle"] = 0.0
    game_state["result_number"] = None
    game_state["result_pocket_index"] = None
    game_state["tokens"] = tokens  # Keep tokens
    game_state["current_bet"] = current_bet  # Keep bet amount
    game_state["bet_type"] = bet_type  # Keep bet type
    game_state["bet_placed"] = False
    game_state["winnings"] = 0
    return game_state


def change_bet_amount(game_state: dict, increase: bool) -> dict:
    """Change the bet amount."""
    if game_state.get("ball_active", False):
        return game_state  # Can't change while spinning
    
    current = game_state.get("current_bet", 10)
    tokens = game_state.get("tokens", 0)
    
    if increase:
        new_bet = min(current + 10, tokens, 100)  # Max bet 100 or available tokens
    else:
        new_bet = max(current - 10, 10)  # Min bet 10
    
    game_state["current_bet"] = new_bet
    return game_state


def change_bet_type(game_state: dict, bet_type: str) -> dict:
    """Change the bet type."""
    if game_state.get("ball_active", False):
        return game_state  # Can't change while spinning
    
    valid_types = ["red", "black", "green", "odd", "even", "number"]
    if bet_type in valid_types:
        game_state["bet_type"] = bet_type
    return game_state


def handle_roulette_click(game_state: dict, mouse_pos: tuple) -> dict:
    """Handle mouse clicks on roulette buttons."""
    if not game_state.get("initialized", False):
        return game_state
    
    buttons = game_state.get("buttons", {})
    
    # Check each button
    for btn_name, btn_rect in buttons.items():
        if btn_rect.collidepoint(mouse_pos):
            if btn_name == "spin":
                return spin_roulette(game_state)
            elif btn_name == "reset":
                return reset_roulette(game_state)
            elif btn_name == "bet_minus":
                return change_bet_amount(game_state, False)
            elif btn_name == "bet_plus":
                return change_bet_amount(game_state, True)
            elif btn_name in ["red", "black", "green", "odd", "even"]:
                return change_bet_type(game_state, btn_name)
            elif btn_name == "number_input":
                game_state["number_input_active"] = True
                return game_state
            elif btn_name == "confirm_number":
                # Confirm number bet
                number_input = game_state.get("number_input", "")
                try:
                    num = int(number_input)
                    if 0 <= num <= 36:
                        game_state["bet_number"] = num
                        game_state["bet_type"] = "number"
                        game_state["number_input_active"] = False
                except ValueError:
                    pass
                return game_state
    
    # Click outside number input deactivates it
    if "number_input" in buttons and not buttons["number_input"].collidepoint(mouse_pos):
        game_state["number_input_active"] = False
    
    return game_state


def handle_roulette_keypress(game_state: dict, event) -> dict:
    """Handle keyboard input for roulette, including number input field."""
    if not game_state.get("initialized", False):
        return game_state
    
    # If number input is active, handle text input
    if game_state.get("number_input_active", False):
        if event.key == pygame.K_RETURN:
            # Confirm number
            number_input = game_state.get("number_input", "")
            try:
                num = int(number_input)
                if 0 <= num <= 36:
                    game_state["bet_number"] = num
                    game_state["bet_type"] = "number"
            except ValueError:
                pass
            game_state["number_input_active"] = False
        elif event.key == pygame.K_ESCAPE:
            game_state["number_input_active"] = False
            game_state["number_input"] = ""
        elif event.key == pygame.K_BACKSPACE:
            game_state["number_input"] = game_state.get("number_input", "")[:-1]
        elif event.unicode.isdigit() and len(game_state.get("number_input", "")) < 2:
            game_state["number_input"] = game_state.get("number_input", "") + event.unicode
        return game_state
    
    return game_state


if __name__ == "__main__":
    game = RouletteGame()
    game.run()
