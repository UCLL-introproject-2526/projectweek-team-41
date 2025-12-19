import pygame
import os
import math
from typing import Optional, Dict, Tuple

WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
DARK_GOLD = (184, 134, 11)

_LOADING_BG_ORIGINAL: Optional[pygame.Surface] = None
_LOADING_BG_SCALED: Dict[Tuple[int, int], pygame.Surface] = {}


def _get_loading_bg() -> Optional[pygame.Surface]:
    global _LOADING_BG_ORIGINAL
    if _LOADING_BG_ORIGINAL is not None:
        return _LOADING_BG_ORIGINAL

    try:
        img_path = os.path.join(os.path.dirname(__file__), "assets", "img", "outside.png")
    except:
        img_path = os.path.join("assets", "img", "outside.png")
    try:
        _LOADING_BG_ORIGINAL = pygame.image.load(img_path).convert_alpha()
    except Exception:
        _LOADING_BG_ORIGINAL = None
    return _LOADING_BG_ORIGINAL


def _get_scaled_bg(bg: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    cached = _LOADING_BG_SCALED.get(size)
    if cached is not None:
        return cached
    scaled = pygame.transform.smoothscale(bg, size)
    _LOADING_BG_SCALED[size] = scaled
    return scaled


def _draw_center_text(surface: pygame.Surface, text: str, y: int, font, color=WHITE) -> None:
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(surf, rect)

def draw_game_screen(surface: pygame.Surface, title_font, hint_font, progress: float = 0.0, elapsed_time: float = 0.0) -> None:
    bg = _get_loading_bg()
    if bg is not None:
        surface.blit(_get_scaled_bg(bg, surface.get_size()), (0, 0))
    
    w = surface.get_width()
    h = surface.get_height()
    
    # Draw title
    _draw_center_text(surface, "Game loading...", h // 2 - 40, font=title_font)
    
    # Draw spinning dots animation
    center_x = w // 2
    center_y = h // 2 + 30
    num_dots = 8
    radius = 25
    dot_radius = 5
    
    for i in range(num_dots):
        angle = (2 * math.pi * i / num_dots) - (elapsed_time * 4)  # Rotate over time
        x = center_x + int(radius * math.cos(angle))
        y = center_y + int(radius * math.sin(angle))
        
        # Fade dots based on position in rotation
        alpha = (i / num_dots)
        color = (
            int(255 * alpha + 100 * (1 - alpha)),
            int(215 * alpha + 100 * (1 - alpha)),
            int(0 * alpha + 100 * (1 - alpha))
        )
        pygame.draw.circle(surface, color, (x, y), dot_radius)
    
    # Draw progress bar
    bar_width = 200
    bar_height = 8
    bar_x = (w - bar_width) // 2
    bar_y = h // 2 + 80
    
    # Background bar
    pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
    # Progress fill
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        pygame.draw.rect(surface, GOLD, (bar_x, bar_y, fill_width, bar_height), border_radius=4)
    # Border
    pygame.draw.rect(surface, DARK_GOLD, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=4)
    
    # Draw hint
    _draw_center_text(
        surface,
        "TIP: press ESC to return to menu.",
        h // 2 + 120,
        font=hint_font,
        color=(200, 200, 200),
    )