import sys
import os
import pygame
from loading import draw_game_screen
from move import Player
from testscene import draw_test_scene
from roulette import draw_roulette_scene, spin_roulette, reset_roulette, change_bet_amount, change_bet_type

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
    # Scenes: "menu" / "loading" / "game" / "roulette"
    scene = "menu"
    player: Player | None = None

    loading_elapsed = 0.0
    roulette_state = {}  # State for roulette game
    
    # Token currency system
    tokens = 100  # Starting tokens
    token_timer = 0.0  # Timer for passive token income (25 tokens per minute)

    window = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Merge Casino")
    canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    is_fullscreen = False

    menu_bg = None
    roulette_table_img = None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Roulette table (top-left) - only this one opens roulette
    roulette_table = pygame.Rect(30, 80, 175, 125)
    
    # Other tables (bottom-right) - for future games
    other_table = pygame.Rect(BASE_WIDTH - 130, BASE_HEIGHT - 150, 100, 100)
    
    # All tables for collision/rendering
    all_tables = [roulette_table, other_table]
    interact_near_px = 22.0
    
    try:
        menu_bg_path = os.path.join(base_dir, "img", "mainmenu.png")
        menu_bg = pygame.image.load(menu_bg_path).convert_alpha()
        menu_bg = pygame.transform.smoothscale(menu_bg, (BASE_WIDTH, BASE_HEIGHT))
    except Exception:
        menu_bg = None
    
    try:
        # Load roulette table image
        roulette_img_path = os.path.join(base_dir, "img", "roulette top view.png")
        roulette_table_img = pygame.image.load(roulette_img_path).convert_alpha()
        roulette_table_img = pygame.transform.smoothscale(roulette_table_img, (roulette_table.width, roulette_table.height))
    except Exception:
        roulette_table_img = None

    btn_width, btn_height = 200, 60
    spacing = 40
    start_btn_x = (BASE_WIDTH - (btn_width * 2 + spacing)) // 2
    start_btn = Button(pygame.Rect(start_btn_x, 475, btn_width, btn_height), "Start game")
    leave_btn = Button(pygame.Rect(start_btn_x + btn_width + spacing, 475, btn_width, btn_height), "Leave")
    
    def is_near_table(p: Player | None, table: pygame.Rect) -> bool:
        if p is None:
            return False
        return _circle_rect_distance(p.x, p.y, table) <= interact_near_px

    running = True
    while running:
        dt = CLOCK.tick(60) / 1000.0
        
        # Passive token income: 25 tokens every 60 seconds
        token_timer += dt
        if token_timer >= 60.0:
            tokens += 25
            token_timer -= 60.0
        
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
                elif scene == "roulette":
                    scene = "game"
                    roulette_state = {}  # Reset roulette when leaving
                elif scene in ("game", "loading"):
                    scene = "menu"
                    player = None
                    loading_elapsed = 0.0
                else:
                    running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if scene == "game" and is_near_table(player, roulette_table):
                    scene = "roulette"
                    roulette_state = {"tokens": tokens}  # Pass tokens to roulette

            # Roulette controls
            if event.type == pygame.KEYDOWN and scene == "roulette":
                if event.key == pygame.K_SPACE:
                    roulette_state = spin_roulette(roulette_state)
                elif event.key == pygame.K_r:
                    roulette_state = reset_roulette(roulette_state)
                elif event.key == pygame.K_1:
                    roulette_state = change_bet_amount(roulette_state, False)  # Decrease
                elif event.key == pygame.K_2:
                    roulette_state = change_bet_amount(roulette_state, True)   # Increase
                elif event.key == pygame.K_q:
                    roulette_state = change_bet_type(roulette_state, "red")
                elif event.key == pygame.K_w:
                    roulette_state = change_bet_type(roulette_state, "black")
                elif event.key == pygame.K_e:
                    roulette_state = change_bet_type(roulette_state, "green")
                elif event.key == pygame.K_a:
                    roulette_state = change_bet_type(roulette_state, "odd")
                elif event.key == pygame.K_s:
                    roulette_state = change_bet_type(roulette_state, "even")

            # Menu button clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if scene == "menu":
                    if start_btn.handle_click(mouse_pos):
                        scene = "loading"
                        loading_elapsed = 0.0
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

        elif scene == "roulette":
            roulette_state = draw_roulette_scene(canvas, roulette_state, font=FONT)
            tokens = roulette_state.get("tokens", tokens)  # Update tokens from roulette

        else:  # scene == "game"
            # Map = blauwe vlakte; personage = bol.
            canvas.fill((40, 120, 220))

            if player is None:
                player = Player((BASE_WIDTH // 2, BASE_HEIGHT // 2))

            keys = pygame.key.get_pressed()
            player.update(dt, keys, canvas.get_rect(), obstacles=all_tables)
            player.draw(canvas)

            # Draw roulette table (image or fallback to green rect)
            if roulette_table_img is not None:
                canvas.blit(roulette_table_img, roulette_table.topleft)
            else:
                pygame.draw.rect(canvas, (0, 100, 0), roulette_table)
                pygame.draw.rect(canvas, (255, 215, 0), roulette_table, width=2)
                label = FONT_TIP.render("R", True, (255, 255, 255))
                label_rect = label.get_rect(center=roulette_table.center)
                canvas.blit(label, label_rect)
            
            # Draw other table (gray - not yet implemented)
            pygame.draw.rect(canvas, (60, 60, 60), other_table)
            pygame.draw.rect(canvas, (150, 150, 150), other_table, width=2)
            label2 = FONT_TIP.render("?", True, (150, 150, 150))
            label2_rect = label2.get_rect(center=other_table.center)
            canvas.blit(label2, label2_rect)

            # Draw token counter at top
            token_text = f"Tokens: {tokens}"
            token_surf = FONT_SMALL.render(token_text, True, (255, 215, 0))
            token_rect = token_surf.get_rect(topright=(BASE_WIDTH - 20, 20))
            pygame.draw.rect(canvas, (30, 30, 30), token_rect.inflate(20, 10), border_radius=8)
            canvas.blit(token_surf, token_rect)

            # Popup: toon 'E' als je dichtbij roulette table staat
            if is_near_table(player, roulette_table):
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

