import pygame
import math


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
    draw_heart(card, 20, 38, 0.6, heart_color)  # Bigger
    
    # Bottom-right corner value (upside down)
    text_surface = small_font.render(display_value, True, heart_color)
    text_surface = pygame.transform.rotate(text_surface, 180)
    card.blit(text_surface, (width - text_surface.get_width() - 12, height - text_surface.get_height() - 8))
    draw_heart(card, width - 20, height - 38, 0.6, heart_color)  # Bigger
    
    # Center design based on value
    center_x = width // 2
    center_y = height // 2
    
    if value == 1:  # Ace - one large heart
        draw_heart(card, center_x, center_y, 2.2, heart_color)  # Much bigger
    elif value <= 10:
        # Draw hearts in pattern
        heart_size = 0.9  # Bigger
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
            # For 6-10, draw multiple hearts in grid pattern
            large_text = large_font.render(display_value, True, heart_color)
            text_rect = large_text.get_rect(center=(center_x, center_y - 20))
            card.blit(large_text, text_rect)
            draw_heart(card, center_x, center_y + 35, 1.5, heart_color)  # Bigger
    else:
        # Face cards (J, Q, K) - large letter with decorative heart
        large_text = large_font.render(display_value, True, heart_color)
        text_rect = large_text.get_rect(center=(center_x, center_y - 15))
        card.blit(large_text, text_rect)
        draw_heart(card, center_x, center_y + 40, 1.3, heart_color)  # Bigger
    
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
    pygame.init()  # Ensure pygame is initialized
    
    card_dict = {}
    for value in range(1, 14):
        card_dict[value] = create_card_surface(value, width, height)
    
    card_back = create_card_back(width, height)
    
    return card_dict, card_back
