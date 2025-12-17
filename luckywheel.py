import pygame
import math
import random

class Particle:
    """Particle class for confetti and sparkle effects"""
    def __init__(self, x, y, color, velocity_x, velocity_y, lifetime=60):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self. lifetime = lifetime
        self.max_lifetime = lifetime
        self. size = random.randint(3, 8)
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.randint(-10, 10)
    
    def update(self):
        self.x += self.velocity_x
        self.y += self. velocity_y
        self.velocity_y += 0.3  # Gravity
        self.lifetime -= 1
        self.rotation += self.rotation_speed
    
    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            # Draw as a rotated rectangle for confetti effect
            particle_surface = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)
            pygame.draw.rect(particle_surface, (*self.color, alpha), (0, 0, self.size * 2, self.size))
            rotated = pygame.transform.rotate(particle_surface, self.rotation)
            rect = rotated.get_rect(center=(self.x, self. y))
            surface.blit(rotated, rect)
    
    def is_dead(self):
        return self.lifetime <= 0


class LuckyWheel:
    def __init__(self, x, y, radius, num_slots=10):
        """
        Initialize the Lucky Wheel
        
        Args:
            x, y: Center position of the wheel
            radius: Radius of the wheel
            num_slots: Number of slots on the wheel (default 10)
        """
        self.x = x
        self. y = y
        self.radius = radius
        self.num_slots = num_slots
        self.angle = 0  # Current rotation angle
        self.angular_velocity = 0  # Rotation speed
        self.is_spinning = False
        self. friction = 0.98  # Deceleration factor
        
        # Alternating rich casino colors (red and black like roulette, with gold accents)
        self.colors = [
            (220, 20, 20),    # Rich Red
            (20, 20, 20),     # Black
            (220, 20, 20),    # Rich Red
            (20, 20, 20),     # Black
            (220, 20, 20),    # Rich Red
            (20, 20, 20),     # Black
            (220, 20, 20),    # Rich Red
            (20, 20, 20),     # Black
            (220, 20, 20),    # Rich Red
            (20, 20, 20),     # Black
        ]
        
        # Prizes for each slot (you can customize these later)
        self.prizes = [
            "Prize 1",
            "Prize 2",
            "Prize 3",
            "Prize 4",
            "Prize 5",
            "Prize 6",
            "Prize 7",
            "Prize 8",
            "Prize 9",
            "Prize 10",
        ]
        
        self.winner = None
        self. glow_intensity = 0
        self.glow_direction = 1
        self.particles = []
        self.sparkles = []
        self.light_rays = []
        self.winner_announced = False
        self.celebration_timer = 0
        
        # Create initial sparkles around the wheel
        self.create_idle_sparkles()
    
    def create_idle_sparkles(self):
        """Create sparkles that appear around the wheel when idle"""
        for i in range(5):
            angle = random.uniform(0, 2 * math.pi)
            distance = self.radius + random.randint(10, 40)
            x = self.x + distance * math.cos(angle)
            y = self.y + distance * math.sin(angle)
            self.sparkles.append({
                'x': x,
                'y': y,
                'life': random.randint(20, 40),
                'max_life': 40,
                'size': random.randint(2, 5)
            })
    
    def spin(self, force=None):
        """Start spinning the wheel"""
        if not self.is_spinning:
            self.is_spinning = True
            # Random spin force between 20 and 40 if not specified
            if force is None: 
                force = random.uniform(20, 40)
            self.angular_velocity = force
            self.winner = None
            self.winner_announced = False
            self. particles. clear()
    
    def update(self):
        """Update wheel rotation"""
        if self.is_spinning:
            # Update angle
            self.angle += self.angular_velocity
            self.angle %= 360  # Keep angle between 0-360
            
            # Apply friction
            self.angular_velocity *= self.friction
            
            # Create sparkle trail while spinning fast
            if abs(self.angular_velocity) > 5:
                if random.random() < 0.3:
                    angle = random.uniform(0, 2 * math.pi)
                    distance = self.radius + random.randint(-10, 10)
                    x = self.x + distance * math.cos(angle)
                    y = self.y + distance * math.sin(angle)
                    self.sparkles.append({
                        'x': x,
                        'y': y,
                        'life': random. randint(10, 20),
                        'max_life': 20,
                        'size': random.randint(3, 6)
                    })
            
            # Stop spinning when velocity is very low
            if abs(self.angular_velocity) < 0.1:
                self.is_spinning = False
                self.angular_velocity = 0
                self.determine_winner()
        
        # Update glow effect
        self.glow_intensity += self.glow_direction * 3
        if self.glow_intensity >= 100:
            self.glow_intensity = 100
            self.glow_direction = -1
        elif self.glow_intensity <= 0:
            self. glow_intensity = 0
            self.glow_direction = 1
        
        # Update particles
        for particle in self.particles[: ]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
        
        # Update sparkles
        for sparkle in self.sparkles[:]:
            sparkle['life'] -= 1
            if sparkle['life'] <= 0:
                self. sparkles.remove(sparkle)
        
        # Create new idle sparkles occasionally
        if not self.is_spinning and len(self.sparkles) < 8 and random.random() < 0.05:
            self.create_idle_sparkles()
        
        # Winner celebration
        if self.winner and not self.is_spinning:
            self.celebration_timer += 1
            
            # Trigger confetti explosion once
            if not self.winner_announced:
                self.winner_announced = True
                self.create_confetti_explosion()
            
            # Continue adding particles during celebration
            if self.celebration_timer < 120 and random.random() < 0.2:
                self.create_winner_particles()
    
    def create_confetti_explosion(self):
        """Create a confetti explosion effect when winning"""
        confetti_colors = [
            (255, 215, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 0, 255), (0, 255, 255), (255, 128, 0), (255, 255, 255)
        ]
        
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            velocity_x = speed * math.cos(angle)
            velocity_y = speed * math.sin(angle) - random.uniform(5, 10)
            color = random.choice(confetti_colors)
            
            # Start from wheel center
            particle = Particle(self.x, self.y, color, velocity_x, velocity_y, lifetime=random.randint(60, 120))
            self.particles.append(particle)
    
    def create_winner_particles(self):
        """Create sparkle particles around the winning slot"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(50, 150)
        x = self.x + distance * math. cos(angle)
        y = self.y + distance * math. sin(angle)
        
        color = random.choice([(255, 215, 0), (255, 255, 0), (255, 255, 255)])
        velocity_x = random.uniform(-2, 2)
        velocity_y = random.uniform(-5, -2)
        
        particle = Particle(x, y, color, velocity_x, velocity_y, lifetime=random.randint(30, 60))
        self.particles.append(particle)
    
    def determine_winner(self):
        """Determine which slot won based on the pointer position at the TOP"""
        degrees_per_slot = 360 / self.num_slots
        
        # The pointer is at the TOP of the wheel (straight up)
        # In our coordinate system, we start drawing slots from angle 0 (right side)
        # and the wheel rotates clockwise based on self.angle
        # The top position is 270 degrees in standard math coordinates (or -90)
        
        # To find which slot is at the top: 
        # We need to check where the top pointer (270 degrees) intersects with our rotating wheel
        # The wheel's current rotation is self.angle (clockwise)
        # So the effective angle at the top pointer is: (270 - self.angle) % 360
        
        pointer_angle = 270  # Top of the wheel in standard coordinates
        # Subtract wheel rotation to find which slot is at the pointer
        adjusted_angle = (pointer_angle - self.angle) % 360
        
        # Calculate which slot index is at this angle
        winning_slot = int(adjusted_angle / degrees_per_slot)
        
        self.winner = self.prizes[winning_slot]
        self.celebration_timer = 0
        return self.winner
    
    def draw(self, surface):
        """Draw the wheel on the surface with fancy casino effects"""
        degrees_per_slot = 360 / self.num_slots
        
        # Draw light rays from center when winning
        if self.winner and not self.is_spinning and self.celebration_timer < 60:
            self.draw_light_rays(surface)
        
        # Draw outer glow effect
        for i in range(8, 0, -1):
            glow_radius = self.radius + i * 8
            glow_alpha = int(30 * (i / 8) * (self.glow_intensity / 100))
            glow_color = (255, 215, 0)  # Gold glow
            
            glow_surface = pygame.Surface((glow_radius * 2 + 50, glow_radius * 2 + 50), pygame.SRCALPHA)
            pygame. draw.circle(glow_surface, (*glow_color, glow_alpha), 
                             (glow_radius + 25, glow_radius + 25), glow_radius)
            surface.blit(glow_surface, (self.x - glow_radius - 25, self.y - glow_radius - 25))
        
        # Draw outer decorative rings
        ring_colors = [(139, 69, 19), (218, 165, 32), (184, 134, 11), (255, 215, 0)]
        ring_widths = [15, 10, 6, 3]
        ring_offsets = [25, 18, 12, 7]
        
        for color, width, offset in zip(ring_colors, ring_widths, ring_offsets):
            pygame.draw.circle(surface, color, (self.x, self. y), self.radius + offset, width)
        
        # Draw metallic outer rim with gradient effect
        for i in range(20):
            rim_color_value = 100 + int(50 * math.sin(i / 5))
            pygame.draw.circle(surface, (rim_color_value, rim_color_value, rim_color_value), 
                             (self.x, self.y), self.radius + 5 - i, 1)
        
        # Draw each slot with 3D effect
        for i in range(self.num_slots):
            start_angle = math.radians(self.angle + i * degrees_per_slot)
            end_angle = math.radians(self. angle + (i + 1) * degrees_per_slot)
            
            # Create points for the pie slice
            points = [(self.x, self.y)]
            
            # Add points along the arc
            num_points = 40
            for j in range(num_points + 1):
                angle = start_angle + (end_angle - start_angle) * j / num_points
                point_x = self.x + self.radius * math.cos(angle)
                point_y = self.y + self.radius * math.sin(angle)
                points.append((point_x, point_y))
            
            # Draw the slice with base color
            base_color = self.colors[i % len(self.colors)]
            pygame.draw.polygon(surface, base_color, points)
            
            # Add gradient/shine effect to each slice
            shine_surface = pygame.Surface((self.radius * 2 + 100, self.radius * 2 + 100), pygame.SRCALPHA)
            shine_points = [(self.x, self. y)]
            for j in range(num_points + 1):
                angle = start_angle + (end_angle - start_angle) * j / num_points
                # Inner radius for shine effect
                inner_rad = self.radius * 0.5
                point_x = self.x + inner_rad * math.cos(angle)
                point_y = self.y + inner_rad * math.sin(angle)
                shine_points.append((point_x, point_y))
            
            # Lighter color for shine
            shine_color = tuple(min(c + 60, 255) for c in base_color)
            pygame.draw.polygon(shine_surface, (*shine_color, 80), shine_points)
            surface.blit(shine_surface, (0, 0))
            
            # Draw separator lines with gold color
            line_end_x = self.x + self.radius * math.cos(start_angle)
            line_end_y = self.y + self.radius * math.sin(start_angle)
            pygame.draw.line(surface, (255, 215, 0), (self.x, self.y), 
                           (line_end_x, line_end_y), 4)
            
            # Draw prize text in the middle of each slice with better styling
            text_angle = start_angle + (end_angle - start_angle) / 2
            text_radius = self.radius * 0.75
            text_x = self.x + text_radius * math.cos(text_angle)
            text_y = self.y + text_radius * math.sin(text_angle)
            
            # Rotate text to align with slice
            font = pygame.font.Font(None, 32)
            prize_text = self.prizes[i] if i < len(self.prizes) else str(i + 1)
            
            # Create text with outline
            text_surface = font. render(prize_text, True, (255, 255, 255))
            outline_surface = font.render(prize_text, True, (0, 0, 0))
            
            # Rotate text
            angle_deg = math.degrees(text_angle) + 90
            rotated_text = pygame.transform.rotate(text_surface, -angle_deg)
            rotated_outline = pygame.transform.rotate(outline_surface, -angle_deg)
            
            text_rect = rotated_text. get_rect(center=(text_x, text_y))
            outline_rect = rotated_outline.get_rect(center=(text_x, text_y))
            
            # Draw outline first (in multiple positions for thickness)
            for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1), (-2,0), (2,0), (0,-2), (0,2)]:
                surface.blit(rotated_outline, outline_rect.move(ox, oy))
            surface.blit(rotated_text, text_rect)
            
            # Draw decorative dots between sections
            dot_radius = self.radius + 15
            dot_x = self.x + dot_radius * math.cos(start_angle)
            dot_y = self.y + dot_radius * math.sin(start_angle)
            pygame.draw.circle(surface, (255, 215, 0), (int(dot_x), int(dot_y)), 6)
            pygame.draw.circle(surface, (255, 255, 255), (int(dot_x), int(dot_y)), 4)
            pygame.draw.circle(surface, (255, 215, 0), (int(dot_x), int(dot_y)), 2)
        
        # Draw sparkles
        for sparkle in self.sparkles:
            alpha = int(255 * (sparkle['life'] / sparkle['max_life']))
            if alpha > 0:
                sparkle_surface = pygame.Surface((sparkle['size'] * 4, sparkle['size'] * 4), pygame.SRCALPHA)
                # Draw a star shape
                points = []
                for i in range(8):
                    angle = math. radians(i * 45)
                    radius = sparkle['size'] if i % 2 == 0 else sparkle['size'] // 2
                    px = sparkle['size'] * 2 + radius * math.cos(angle)
                    py = sparkle['size'] * 2 + radius * math.sin(angle)
                    points.append((px, py))
                pygame.draw. polygon(sparkle_surface, (255, 255, 255, alpha), points)
                pygame.draw.polygon(sparkle_surface, (255, 215, 0, alpha), points, 1)
                surface.blit(sparkle_surface, (sparkle['x'] - sparkle['size'] * 2, sparkle['y'] - sparkle['size'] * 2))
        
        # Draw particles (confetti)
        for particle in self.particles:
            particle.draw(surface)
        
        # Draw center hub with 3D effect
        # Outer shadow
        for i in range(10, 0, -1):
            shadow_alpha = int(20 * (i / 10))
            shadow_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surface, (0, 0, 0, shadow_alpha), (50, 50), 45 + i)
            surface.blit(shadow_surface, (self.x - 50, self. y - 50))
        
        # Gold rim of center
        pygame.draw.circle(surface, (255, 215, 0), (self.x, self.y), 45)
        pygame.draw.circle(surface, (218, 165, 32), (self.x, self.y), 42)
        
        # Center circle with gradient
        for i in range(40, 0, -1):
            gray_value = 50 + int(150 * (i / 40))
            pygame.draw.circle(surface, (gray_value, gray_value, gray_value), 
                             (self.x, self.y), i)
        
        # Center logo/emblem
        pygame.draw.circle(surface, (255, 215, 0), (self.x, self.y), 25)
        pygame.draw.circle(surface, (0, 0, 0), (self.x, self.y), 22)
        
        # Draw star in center
        self.draw_center_star(surface, self.x, self.y, 18, (255, 215, 0))
        
        # Draw pointer at the top with 3D effect
        pointer_length = 50
        pointer_width = 20
        pointer_y_pos = self.y - self.radius - 30
        
        # Pointer shadow
        shadow_points = [
            (self.x, self.y - self.radius - 15),
            (self.x - pointer_width - 2, pointer_y_pos - 2),
            (self.x + pointer_width + 2, pointer_y_pos - 2)
        ]
        pygame.draw.polygon(surface, (0, 0, 0), shadow_points)
        
        # Pointer base (dark red)
        pointer_points = [
            (self.x, self.y - self.radius - 15),
            (self.x - pointer_width, pointer_y_pos),
            (self.x + pointer_width, pointer_y_pos)
        ]
        pygame. draw.polygon(surface, (180, 0, 0), pointer_points)
        
        # Pointer highlight (bright red)
        highlight_points = [
            (self.x, self.y - self.radius - 15),
            (self. x - pointer_width + 5, pointer_y_pos),
            (self.x, pointer_y_pos + 10)
        ]
        pygame. draw.polygon(surface, (255, 50, 50), highlight_points)
        
        # Pointer outline
        pygame.draw.polygon(surface, (255, 215, 0), pointer_points, 3)
        
        # Pointer mounting point
        mount_y = self.y - self.radius - 15
        pygame.draw.circle(surface, (255, 215, 0), (self.x, mount_y), 12)
        pygame.draw.circle(surface, (139, 69, 19), (self.x, mount_y), 9)
        pygame.draw.circle(surface, (255, 215, 0), (self.x, mount_y), 5)
    
    def draw_center_star(self, surface, x, y, size, color):
        """Draw a star in the center of the wheel"""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90 + self.angle * 0.5)  # Rotate with wheel
            radius = size if i % 2 == 0 else size // 2.5
            point_x = x + radius * math.cos(angle)
            point_y = y + radius * math.sin(angle)
            points.append((point_x, point_y))
        
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (255, 255, 100), points, 2)
    
    def draw_light_rays(self, surface):
        """Draw animated light rays emanating from center when winning"""
        num_rays = 12
        for i in range(num_rays):
            angle = math.radians(i * (360 / num_rays) + self.celebration_timer * 3)
            
            # Create a fading light ray
            ray_length = 300
            ray_width = 40
            
            # Calculate ray points
            x1 = self.x + 50 * math.cos(angle)
            y1 = self. y + 50 * math. sin(angle)
            x2 = self.x + ray_length * math.cos(angle)
            y2 = self. y + ray_length * math. sin(angle)
            
            # Create perpendicular points for width
            perp_angle = angle + math.pi / 2
            dx = ray_width / 2 * math.cos(perp_angle)
            dy = ray_width / 2 * math.sin(perp_angle)
            
            # Ray as a triangle/trapezoid
            points = [
                (x1 + dx * 0.3, y1 + dy * 0.3),
                (x1 - dx * 0.3, y1 - dy * 0.3),
                (x2 - dx, y2 - dy),
                (x2 + dx, y2 + dy)
            ]
            
            # Draw with transparency
            ray_surface = pygame.Surface((1000, 700), pygame.SRCALPHA)
            alpha = 30 + int(20 * math.sin(self.celebration_timer * 0.1 + i))
            color = (255, 215, 0, alpha)
            pygame.draw.polygon(ray_surface, color, points)
            surface.blit(ray_surface, (0, 0))


def draw_fancy_title(surface, width):
    """Draw an eye-catching LUCKY WHEEL title with decorative elements"""
    # Create large bold title font
    title_font = pygame.font.Font(None, 120)
    subtitle_font = pygame.font.Font(None, 40)
    
    # Main title text
    title_text = "LUCKY WHEEL"
    
    # Draw shadow/outline effect (multiple layers for depth)
    shadow_colors = [(0, 0, 0), (50, 50, 50), (100, 100, 0)]
    offsets = [6, 4, 2]
    
    for i, (shadow_color, offset) in enumerate(zip(shadow_colors, offsets)):
        shadow_surface = title_font.render(title_text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect(center=(width // 2 + offset, 60 + offset))
        surface.blit(shadow_surface, shadow_rect)
    
    # Main title in gold gradient effect (simulate with multiple colors)
    title_surface = title_font.render(title_text, True, (255, 215, 0))  # Gold
    title_rect = title_surface.get_rect(center=(width // 2, 60))
    surface.blit(title_surface, title_rect)
    
    # Add bright highlight on top
    highlight_surface = title_font.render(title_text, True, (255, 255, 150))
    highlight_surface.set_alpha(100)  # Semi-transparent
    surface.blit(highlight_surface, title_rect. move(0, -2))
    
    # Decorative stars around the title
    star_positions = [
        (width // 2 - 350, 50),
        (width // 2 - 320, 70),
        (width // 2 + 350, 50),
        (width // 2 + 320, 70),
    ]
    
    for pos in star_positions:
        draw_star(surface, pos[0], pos[1], 15, (255, 215, 0), (255, 255, 0))
    
    # Subtitle/tagline
    tagline = "~ Spin Your Fortune ~"
    tagline_surface = subtitle_font.render(tagline, True, (255, 215, 0))
    tagline_rect = tagline_surface. get_rect(center=(width // 2, 110))
    
    # Tagline shadow
    tagline_shadow = subtitle_font. render(tagline, True, (0, 0, 0))
    surface.blit(tagline_shadow, tagline_rect.move(2, 2))
    surface.blit(tagline_surface, tagline_rect)
    
    # Decorative line under title
    line_y = 130
    pygame.draw.line(surface, (255, 215, 0), (width // 2 - 200, line_y), 
                     (width // 2 + 200, line_y), 3)
    
    # Small diamonds on the line
    diamond_positions = [width // 2 - 200, width // 2, width // 2 + 200]
    for x in diamond_positions:
        draw_diamond(surface, x, line_y, 8, (255, 215, 0))


def draw_star(surface, x, y, size, color1, color2):
    """Draw a decorative star"""
    points = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        radius = size if i % 2 == 0 else size // 2
        point_x = x + radius * math.cos(angle)
        point_y = y + radius * math.sin(angle)
        points.append((point_x, point_y))
    
    pygame.draw.polygon(surface, color1, points)
    pygame.draw.polygon(surface, color2, points, 2)


def draw_diamond(surface, x, y, size, color):
    """Draw a small diamond shape"""
    points = [
        (x, y - size),      # Top
        (x + size, y),      # Right
        (x, y + size),      # Bottom
        (x - size, y),      # Left
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (255, 255, 255), points, 2)


def draw_decorative_border(surface, width, height):
    """Draw decorative border around the screen"""
    border_color = (255, 215, 0)  # Gold
    border_width = 8
    
    # Outer border
    pygame.draw. rect(surface, border_color, (10, 10, width - 20, height - 20), border_width)
    
    # Inner border
    pygame.draw.rect(surface, (139, 69, 19), (18, 18, width - 36, height - 36), 4)
    
    # Corner decorations
    corner_size = 30
    corners = [
        (20, 20), (width - 20, 20), 
        (20, height - 20), (width - 20, height - 20)
    ]
    
    for i, (cx, cy) in enumerate(corners):
        # Draw small circles in corners
        pygame.draw.circle(surface, border_color, (cx, cy), corner_size // 2)
        pygame.draw.circle(surface, (139, 69, 19), (cx, cy), corner_size // 2 - 3)
        pygame.draw.circle(surface, border_color, (cx, cy), corner_size // 4)


def draw_spin_button(surface, x, y, width, height, mouse_pos, is_spinning):
    """Draw an attractive spin button"""
    button_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
    
    # Check if mouse is hovering
    is_hovered = button_rect. collidepoint(mouse_pos) and not is_spinning
    
    # Button colors
    if is_spinning:
        main_color = (100, 100, 100)
        border_color = (80, 80, 80)
        text_color = (150, 150, 150)
    elif is_hovered:
        main_color = (255, 200, 0)  # Brighter gold
        border_color = (255, 215, 0)
        text_color = (0, 0, 0)
    else:
        main_color = (218, 165, 32)  # Gold
        border_color = (255, 215, 0)
        text_color = (255, 255, 255)
    
    # Draw button shadow
    shadow_rect = button_rect.copy()
    shadow_rect.y += 5
    pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=15)
    
    # Draw button
    pygame.draw.rect(surface, main_color, button_rect, border_radius=15)
    pygame.draw.rect(surface, border_color, button_rect, 4, border_radius=15)
    
    # Draw button text
    font = pygame.font.Font(None, 48)
    text = "SPIN!" if not is_spinning else "SPINNING..."
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)
    
    return button_rect


def draw_winner_announcement(surface, winner_text, celebration_timer, center_x=500, center_y=400):
    """Draw a clean, centered winner announcement"""
    
    # Semi-transparent overlay background
    overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 150), (0, 0, 1000, 700))
    surface.blit(overlay, (0, 0))
    
    # Main banner
    banner_width = 500
    banner_height = 200
    banner_x = center_x - banner_width // 2
    banner_y = center_y - banner_height // 2
    
    # Banner background
    pygame.draw.rect(surface, (50, 30, 20), (banner_x, banner_y, banner_width, banner_height), border_radius=20)
    pygame.draw.rect(surface, (255, 215, 0), (banner_x, banner_y, banner_width, banner_height), 5, border_radius=20)
    pygame.draw.rect(surface, (218, 165, 32), (banner_x + 8, banner_y + 8, banner_width - 16, banner_height - 16), 3, border_radius=15)
    
    # "YOU WON!" text at top
    top_font = pygame.font.Font(None, 56)
    top_text = "YOU WON!"
    
    top_surface = top_font.render(top_text, True, (255, 255, 255))
    top_rect = top_surface.get_rect(center=(center_x, center_y - 50))
    surface.blit(top_surface, top_rect)
    
    # Prize text - static
    prize_font = pygame.font.Font(None, 100)
    prize_surface = prize_font.render(winner_text, True, (255, 215, 0))
    prize_rect = prize_surface.get_rect(center=(center_x, center_y + 20))
    surface.blit(prize_surface, prize_rect)
    
    # "Click to spin again" at bottom
    bottom_font = pygame.font.Font(None, 36)
    bottom_text = "Click to spin again!"
    
    bottom_surface = bottom_font.render(bottom_text, True, (255, 255, 255))
    bottom_rect = bottom_surface.get_rect(center=(center_x, banner_y + banner_height - 30))
    surface.blit(bottom_surface, bottom_rect)


# Example usage / Demo
def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Lucky Wheel Casino")
    clock = pygame.time.Clock()
    
    # Create wheel in the center of the screen (lower position for title)
    wheel = LuckyWheel(500, 400, 180, num_slots=10)
    
    # Customize prizes (optional)
    wheel.prizes = [
        "$10", "$50", "$100", "$25", "$5",
        "$500", "$15", "$75", "$200", "JACKPOT"
    ]
    
    font = pygame.font.Font(None, 36)
    button_font = pygame.font.Font(None, 48)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event. get():
            if event.type == pygame.QUIT:
                running = False
            
            # Click to spin or press SPACE
            if event.type == pygame.MOUSEBUTTONDOWN: 
                button_rect = pygame.Rect(400, 615, 200, 60)
                if button_rect. collidepoint(event.pos) and not wheel.is_spinning:
                    wheel.spin()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not wheel.is_spinning:
                    wheel.spin()
        
        # Update
        wheel.update()
        
        # Draw
        # Gradient background (dark to light green)
        for y in range(700):
            color_value = int(20 + (y / 700) * 40)
            pygame.draw.line(screen, (0, color_value, 0), (0, y), (1000, y))
        
        # Draw decorative border
        draw_decorative_border(screen, 1000, 700)
        
        # Draw fancy title
        draw_fancy_title(screen, 1000)
        
        # Draw wheel
        wheel.draw(screen)
        
        # Draw spin button
        draw_spin_button(screen, 500, 645, 200, 60, mouse_pos, wheel.is_spinning)
        
        # Draw winner announcement (centered overlay)
        if wheel.winner and not wheel.is_spinning:
            draw_winner_announcement(screen, wheel.winner, wheel.celebration_timer)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__": 
    main()