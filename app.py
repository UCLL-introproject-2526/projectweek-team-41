import sys
import os
import pygame
from loading import draw_game_screen
from move import Player
from testscene import draw_test_scene

# Initialize Pygame
pygame.init()

BASE_WIDTH, BASE_HEIGHT = 900, 600


def _get_letterbox_mapping(window_size: tuple[int, int]) -> tuple[float, int, int]:
    win_w, win_h = window_size
    scale = min(win_w / BASE_WIDTH, win_h / BASE_HEIGHT)
    render_w = int(BASE_WIDTH * scale)
    render_h = int(BASE_HEIGHT * scale)
    offset_x = (win_w - render_w) // 2
    offset_y = (win_h - render_h) // 2
    return scale, offset_x, offset_y


def _window_to_canvas_pos(window_pos: tuple[int, int], window_size: tuple[int, int]) -> tuple[int, int] | None:
    mx, my = window_pos
    scale, offset_x, offset_y = _get_letterbox_mapping(window_size)
    if scale <= 0:
        return None

    x = (mx - offset_x) / scale
    y = (my - offset_y) / scale

    if x < 0 or y < 0 or x >= BASE_WIDTH or y >= BASE_HEIGHT:
        return None
    return int(x), int(y)


def _present(canvas: pygame.Surface, window: pygame.Surface) -> None:
    window.fill(BG)
    win_size = window.get_size()
    scale, offset_x, offset_y = _get_letterbox_mapping(win_size)
    render_size = (int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale))
    if render_size[0] <= 0 or render_size[1] <= 0:
        return
    scaled = pygame.transform.smoothscale(canvas, render_size)
    window.blit(scaled, (offset_x, offset_y))
pygame.display.set_caption("Merge Casino")

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

LOADING_DURATION_SECONDS = 3.0


def _circle_rect_distance(cx: float, cy: float, rect: pygame.Rect) -> float:
    closest_x = min(max(cx, rect.left), rect.right)
    closest_y = min(max(cy, rect.top), rect.bottom)
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) ** 0.5


def _player_can_interact(player: Player | None, rects: list[pygame.Rect], near_px: float) -> bool:
    if player is None:
        return False
    for r in rects:
        if _circle_rect_distance(player.x, player.y, r) <= near_px:
            return True
    return False


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
    rect = surf.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(surf, rect)


def main():
    # Scenes: "menu" / "loading" / "game"
    scene = "menu"
    player: Player | None = None

    loading_elapsed = 0.0

    window = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Merge Casino")
    canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    is_fullscreen = False

    menu_bg = None
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        menu_bg_path = os.path.join(base_dir, "img", "mainmenu.png")
        menu_bg = pygame.image.load(menu_bg_path).convert_alpha()
        menu_bg = pygame.transform.smoothscale(menu_bg, (BASE_WIDTH, BASE_HEIGHT))
    except Exception:
        menu_bg = None

    btn_width, btn_height = 200, 60
    spacing = 40
    start_btn_x = (BASE_WIDTH - (btn_width * 2 + spacing)) // 2
    start_btn = Button(pygame.Rect(start_btn_x, 475, btn_width, btn_height), "Start game")
    leave_btn = Button(pygame.Rect(start_btn_x + btn_width + spacing, 475, btn_width, btn_height), "Leave")

    # 2 interactie-vierkanten aan de rand
    interact_rects = [
        pygame.Rect(30, 80, 50, 50),
        pygame.Rect(BASE_WIDTH - 80, BASE_HEIGHT - 120, 50, 50),
    ]
    interact_near_px = 22.0

    running = True
    while running:
        dt = CLOCK.tick(60) / 1000.0
        window_mouse_pos = pygame.mouse.get_pos()
        mouse_pos = _window_to_canvas_pos(window_mouse_pos, window.get_size())
        if mouse_pos is None:
            mouse_pos = (-1, -1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and (
                event.key == pygame.K_F11
                or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT))
            ):
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    info = pygame.display.Info()
                    window = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                else:
                    window = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
                pygame.display.set_caption("Merge Casino")

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if scene == "testscene":
                    # Terug naar de blauwe map (game) i.p.v. menu
                    scene = "game"
                elif scene in ("game", "loading"):
                    scene = "menu"
                    player = None
                    loading_elapsed = 0.0
                else:
                    running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if scene == "game" and _player_can_interact(player, interact_rects, interact_near_px):
                    scene = "testscene"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if scene == "menu":
                    if start_btn.handle_click(mouse_pos):
                        scene = "loading"
                        loading_elapsed = 0.0
                        player = None
                    elif leave_btn.handle_click(mouse_pos):
                        running = False

        # Draw
        canvas.fill(BG)

        if scene == "menu":
            if menu_bg is not None:
                canvas.blit(menu_bg, (0, 0))
            draw_center_text(canvas, "Main Menu", 180, font=FONT)
            start_btn.draw(canvas, mouse_pos)
            leave_btn.draw(canvas, mouse_pos)
            draw_center_text(canvas, "Tip: ESC = afsluiten (menu) / terug (game)", 580, font=FONT_TIP, color=(200, 200, 200))

        elif scene == "loading":
            loading_elapsed += dt
            draw_game_screen(canvas, title_font=FONT, hint_font=FONT_GAME_HINT)
            if loading_elapsed >= LOADING_DURATION_SECONDS:
                scene = "game"
                player = Player((BASE_WIDTH // 2, BASE_HEIGHT // 2))

        elif scene == "testscene":
            draw_test_scene(canvas, font=FONT)

        else:  # scene == "game"
            # Map = blauwe vlakte; personage = bol.
            canvas.fill((40, 120, 220))

            if player is None:
                player = Player((BASE_WIDTH // 2, BASE_HEIGHT // 2))

            keys = pygame.key.get_pressed()
            player.update(dt, keys, canvas.get_rect(), obstacles=interact_rects)
            player.draw(canvas)

            # Interactie-vierkanten
            for r in interact_rects:
                pygame.draw.rect(canvas, (30, 30, 30), r)
                pygame.draw.rect(canvas, (255, 255, 255), r, width=2)

            # Popup: toon 'E' als je dichtbij staat
            if _player_can_interact(player, interact_rects, interact_near_px):
                popup = pygame.Rect(0, 0, 26, 26)
                popup.center = (int(player.x), int(player.y - (player.radius + 18)))
                popup.clamp_ip(canvas.get_rect())
                pygame.draw.rect(canvas, (20, 20, 25), popup, border_radius=4)
                pygame.draw.rect(canvas, (255, 255, 255), popup, width=2, border_radius=4)
                e_surf = FONT_TIP.render("E", True, (255, 255, 255))
                e_rect = e_surf.get_rect(center=popup.center)
                canvas.blit(e_surf, e_rect)

        _present(canvas, window)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

