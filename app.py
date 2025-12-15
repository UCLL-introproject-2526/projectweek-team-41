import sys
import os
import pygame
from outside import draw_game_screen

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Merge Casino - Menu")

CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 48)
FONT_SMALL = pygame.font.SysFont(None, 32)
FONT_TIP = pygame.font.SysFont(None, 24)
FONT_GAME_HINT = pygame.font.SysFont(None, 28)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG = (25, 28, 36)

BTN_IDLE = (70, 80, 110)
BTN_HOVER = (95, 110, 150)
BTN_TEXT = (255, 255, 255)


class Button:
    def __init__(self, rect: pygame.Rect, text: str):
        self.rect = rect
        self.text = text

    def is_hovered(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, mouse_pos):
        color = BTN_HOVER if self.is_hovered(mouse_pos) else BTN_IDLE
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (20, 20, 25), self.rect, width=2, border_radius=12)

        text_surf = FONT_SMALL.render(self.text, True, BTN_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_click(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)


def draw_center_text(surface: pygame.Surface, text: str, y: int, font=FONT, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(surf, rect)


def main():
    # Scenes: "menu" of "game"
    scene = "menu"

    # Load menu background image
    menu_bg = None
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        menu_bg_path = os.path.join(base_dir, "img", "mainmenu.png")
        menu_bg = pygame.image.load(menu_bg_path).convert_alpha()
        menu_bg = pygame.transform.smoothscale(menu_bg, (WIDTH, HEIGHT))
    except Exception:
        menu_bg = None

    btn_width, btn_height = 200, 60
    spacing = 40
    start_btn_x = (WIDTH - (btn_width * 2 + spacing)) // 2
    start_btn = Button(pygame.Rect(start_btn_x, 475, btn_width, btn_height), "Start game")
    leave_btn = Button(pygame.Rect(start_btn_x + btn_width + spacing, 475, btn_width, btn_height), "Leave")

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if scene == "game":
                        scene = "menu"
                    else:
                        running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if scene == "menu":
                    if start_btn.handle_click(mouse_pos):
                        scene = "game"
                    elif leave_btn.handle_click(mouse_pos):
                        running = False

        # Draw
        SCREEN.fill(BG)

        if scene == "menu":
            if menu_bg is not None:
                SCREEN.blit(menu_bg, (0, 0))
            draw_center_text(SCREEN, "Main Menu", 180, font=FONT)
            start_btn.draw(SCREEN, mouse_pos)
            leave_btn.draw(SCREEN, mouse_pos)
            draw_center_text(
                SCREEN,
                "Tip: ESC = afsluiten (menu) / terug (game)",
                580,
                font=FONT_TIP,
                color=(200, 200, 200),
            )
        else:
            draw_game_screen(SCREEN, title_font=FONT, hint_font=FONT_GAME_HINT)

        pygame.display.flip()
        CLOCK.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

