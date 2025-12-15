import pygame

WHITE = (255, 255, 255)


def _draw_center_text(surface: pygame.Surface, text: str, y: int, font, color=WHITE) -> None:
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(surf, rect)


def draw_game_screen(surface: pygame.Surface, title_font, hint_font) -> None:
    h = surface.get_height()
    _draw_center_text(surface, "Hallo wereld", h // 2, font=title_font)
    _draw_center_text(
        surface,
        "Druk op ESC om terug te gaan naar het menu",
        h // 2 + 60,
        font=hint_font,
        color=(200, 200, 200),
    )