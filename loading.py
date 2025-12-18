import pygame
import os

WHITE = (255, 255, 255)

_LOADING_BG_ORIGINAL: pygame.Surface | None = None
_LOADING_BG_SCALED: dict[tuple[int, int], pygame.Surface] = {}


def _get_loading_bg() -> pygame.Surface | None:
    global _LOADING_BG_ORIGINAL
    if _LOADING_BG_ORIGINAL is not None:
        return _LOADING_BG_ORIGINAL

    img_path = os.path.join(os.path.dirname(__file__), "assets", "img", "outside.png")
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

def draw_game_screen(surface: pygame.Surface, title_font, hint_font) -> None:
    bg = _get_loading_bg()
    if bg is not None:
        surface.blit(_get_scaled_bg(bg, surface.get_size()), (0, 0))
    h = surface.get_height()
    _draw_center_text(surface, "Game loading...", h // 2, font=title_font)
    _draw_center_text(
        surface,
        "TIP: press ESC to return to menu.",
        h // 2 + 60,
        font=hint_font,
        color=(200, 200, 200),
    )