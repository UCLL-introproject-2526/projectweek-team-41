import sys
import os
from pathlib import Path
import json
import random
import asyncio
import math
import pygame
from typing import Optional, Tuple, List, Dict
from loading import draw_game_screen
from move import Player
from roulette import draw_roulette_scene, spin_roulette, reset_roulette, change_bet_amount, change_bet_type, handle_roulette_click, handle_roulette_keypress
from slotmachine import draw_slotmachine_scene, spin_slotmachine, change_slot_bet_amount
from luckywheel import LuckyWheel, draw_spin_button, draw_winner_announcement
from blackjack import draw_blackjack_scene, handle_blackjack_click, handle_blackjack_keypress, change_blackjack_bet
from higherlower import draw_higherlower_scene, handle_higherlower_click, handle_higherlower_keypress, change_higherlower_bet

# Initialize Pygame
pygame.init()
pygame.mixer.init()

BASE_WIDTH, BASE_HEIGHT = 900, 600

# For pygbag, we use a relative path and handle file operations gracefully
# since file system access is limited in browser environment
try:
    SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
except:
    SETTINGS_FILE = "settings.json"


def _load_settings() -> dict:
    """Load settings from file, or return defaults."""
    defaults = {"music_volume": 100}
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**defaults, **data}
    except Exception:
        pass
    return defaults


def _save_settings(settings: dict) -> None:
    """Save settings to file. May fail in browser environment."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        # In pygbag/browser, file writing may not be supported
        pass


def _get_letterbox_mapping(window_size: tuple[int, int]) -> tuple[float, int, int]:
    win_w, win_h = window_size
    scale = min(win_w / BASE_WIDTH, win_h / BASE_HEIGHT)
    render_w = int(BASE_WIDTH * scale)
    render_h = int(BASE_HEIGHT * scale)
    offset_x = (win_w - render_w) // 2
    offset_y = (win_h - render_h) // 2
    return scale, offset_x, offset_y


def _window_to_canvas_pos(window_pos: tuple[int, int], window_size: tuple[int, int]) -> tuple[int, int] | None:
    """Transform window coordinates to canvas coordinates (simple stretch, no letterboxing)."""
    mx, my = window_pos
    win_w, win_h = window_size
    
    if win_w <= 0 or win_h <= 0:
        return None

    # Simple stretch mapping - canvas fills whole window
    x = mx * BASE_WIDTH / win_w
    y = my * BASE_HEIGHT / win_h

    if x < 0 or y < 0 or x >= BASE_WIDTH or y >= BASE_HEIGHT:
        return None
    return int(x), int(y)


def _present(canvas: pygame.Surface, window: pygame.Surface) -> None:
    # Stretch the canvas to fill the window (no letterboxing)
    win_size = window.get_size()
    scaled = pygame.transform.smoothscale(canvas, win_size)
    window.blit(scaled, (0, 0))


pygame.display.set_caption("Merge Casino")

CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 48)
FONT_TITLE = pygame.font.SysFont(None, 144)  # 3x larger for Main Menu
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

# Table colors for each game
TABLE_COLOR_SLOTS = (139, 69, 19)      # Brown for slot machines
TABLE_COLOR_BLACKJACK = (0, 80, 0)     # Dark green for blackjack
TABLE_COLOR_ROULETTE = (0, 100, 0)     # Green for roulette
TABLE_COLOR_WHEEL = (100, 50, 150)     # Purple for lucky wheel


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


class Slider:
    def __init__(self, rect: pygame.Rect, min_val: int = 0, max_val: int = 100, value: int = 100):
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.dragging = False
    
    def get_knob_x(self) -> int:
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.left + ratio * self.rect.width)
    
    def is_hovered(self, mouse_pos) -> bool:
        knob_rect = pygame.Rect(self.get_knob_x() - 10, self.rect.centery - 12, 20, 24)
        return self.rect.collidepoint(mouse_pos) or knob_rect.collidepoint(mouse_pos)
    
    def handle_event(self, event, mouse_pos) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered(mouse_pos):
                self.dragging = True
                self._update_value(mouse_pos)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(mouse_pos)
            return True
        return False
    
    def _update_value(self, mouse_pos):
        x = mouse_pos[0]
        x = max(self.rect.left, min(self.rect.right, x))
        ratio = (x - self.rect.left) / self.rect.width
        self.value = int(self.min_val + ratio * (self.max_val - self.min_val))
    
    def draw(self, surface: pygame.Surface, mouse_pos):
        # Track background
        pygame.draw.rect(surface, (50, 50, 60), self.rect, border_radius=6)
        
        # Filled portion
        filled_width = self.get_knob_x() - self.rect.left
        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.left, self.rect.top, filled_width, self.rect.height)
            pygame.draw.rect(surface, (80, 140, 200), filled_rect, border_radius=6)
        
        # Border
        pygame.draw.rect(surface, (100, 100, 120), self.rect, width=2, border_radius=6)
        
        # Knob
        knob_x = self.get_knob_x()
        knob_color = (120, 180, 255) if self.is_hovered(mouse_pos) or self.dragging else (100, 150, 220)
        pygame.draw.circle(surface, knob_color, (knob_x, self.rect.centery), 12)
        pygame.draw.circle(surface, (200, 200, 220), (knob_x, self.rect.centery), 12, width=2)


def draw_center_text(surface: pygame.Surface, text: str, y: int, font=FONT, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(surf, rect)


def draw_rainbow_text(surface: pygame.Surface, text: str, y: int, font=FONT, time_offset: float = 0):
    """Draw text with rainbow colors that loop over time."""
    import colorsys
    
    # Render each character separately to get their widths
    char_surfaces = []
    total_width = 0
    for i, char in enumerate(text):
        # Calculate hue based on character position and time
        hue = ((i / len(text)) + time_offset) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        char_surf = font.render(char, True, color)
        char_surfaces.append(char_surf)
        total_width += char_surf.get_width()
    
    # Calculate starting x position to center the text
    start_x = (surface.get_width() - total_width) // 2
    current_x = start_x
    
    # Blit each character
    for char_surf in char_surfaces:
        char_rect = char_surf.get_rect(topleft=(current_x, y - char_surf.get_height() // 2))
        surface.blit(char_surf, char_rect)
        current_x += char_surf.get_width()


def draw_luckywheel_scene(surface: pygame.Surface, game_state: dict, font: pygame.font.Font) -> dict:
    """Draw and update lucky wheel game on the given surface."""
    if "initialized" not in game_state:
        tokens = game_state.get("tokens", 100)
        surf_w, surf_h = surface.get_size()
        wheel = LuckyWheel(surf_w // 2, surf_h // 2 - 20, 180, num_slots=10)
        wheel.prizes = ["10", "20", "100", "25", "5", "500", "15", "75", "200", "100"]
        
        game_state = {
            "initialized": True,
            "wheel": wheel,
            "tokens": tokens,
            "last_win": 0,
        }
    
    wheel: LuckyWheel = game_state["wheel"]
    wheel.update()
    
    # Draw background gradient
    for y in range(surface.get_height()):
        color_value = int(20 + (y / surface.get_height()) * 40)
        pygame.draw.line(surface, (0, color_value, 0), (0, y), (surface.get_width(), y))
    
    wheel.draw(surface)
    
    surf_w, surf_h = surface.get_size()
    mouse_pos = pygame.mouse.get_pos()
    button_rect = draw_spin_button(surface, surf_w // 2, surf_h - 60, 200, 60, mouse_pos, wheel.is_spinning)
    game_state["button_rect"] = button_rect
    
    # Draw token counter
    token_text = f"Tokens: {game_state['tokens']}"
    token_surf = font.render(token_text, True, (255, 215, 0))
    surface.blit(token_surf, (20, 20))
    
    # Draw spin cost
    cost_text = "Spin Cost: 100"
    cost_surf = pygame.font.Font(None, 32).render(cost_text, True, (255, 255, 255))
    surface.blit(cost_surf, (20, 60))
    
    # Draw controls hint
    hint_font = pygame.font.Font(None, 24)
    hints = ["SPACE - Spin", "ESC - Back"]
    for i, hint in enumerate(hints):
        hint_surf = hint_font.render(hint, True, (200, 200, 200))
        surface.blit(hint_surf, (20, surf_h - 60 + i * 22))
    
    # Draw winner announcement if won
    if wheel.winner and not wheel.is_spinning:
        draw_winner_announcement(surface, wheel.winner, wheel.celebration_timer, surf_w // 2, surf_h // 2)
        
        if not game_state.get("win_processed", False):
            try:
                win_amount = int(wheel.winner.replace("$", "").replace(",", ""))
                game_state["tokens"] += win_amount
                game_state["last_win"] = win_amount
            except ValueError:
                pass
            game_state["win_processed"] = True
    
    return game_state


def spin_luckywheel(game_state: dict) -> dict:
    """Start a lucky wheel spin. Fixed cost: 100 tokens."""
    if "wheel" not in game_state:
        return game_state
    
    wheel: LuckyWheel = game_state["wheel"]
    tokens = game_state.get("tokens", 0)
    spin_cost = 100
    
    if wheel.is_spinning or tokens < spin_cost:
        return game_state
    
    game_state["tokens"] = tokens - spin_cost
    game_state["win_processed"] = False
    wheel.spin()
    
    return game_state


async def main():
    # Scenes: "menu" / "loading" / "game" / "roulette" / "settings"
    scene = "menu"
    player: Player | None = None

    loading_elapsed = 0.0
    roulette_state = {}  # State for roulette game
    slotmachine_state = {}
    luckywheel_state = {}  # State for lucky wheel game
    blackjack_state = {}  # State for blackjack game
    higherlower_state = {}  # State for higher/lower game

    # Cocktail/Drunk effect state
    holding_cocktail = False
    cocktail_timer = 0.0
    drunk_active = False
    drunk_timer = 0.0
    drunk_duration = 5.0  # 5 seconds of drunk effect
    cocktail_hold_duration = 1.0  # Hold cocktail for 1 second before drunk
    
    # Dancefloor disco state
    was_on_dancefloor = False
    disco_ball_y = -100  # Start above screen
    disco_ball_target_y = BASE_HEIGHT // 2 - 50
    disco_ball_lowering = False
    disco_ray_timer = 0.0
    disco_music_playing = False
    disco_flash_timer = 0.0
    disco_flash_index = 0
    disco_pulse_timer = 0.0
    disco_flash_colors = [
        (255, 50, 50),    # Red
        (50, 255, 50),    # Green
        (50, 50, 255),    # Blue
        (255, 255, 50),   # Yellow
        (255, 50, 255),   # Magenta
        (50, 255, 255),   # Cyan
        (255, 150, 50),   # Orange
        (150, 50, 255),   # Purple
    ]

    # Token currency system
    tokens = 100  # Starting tokens
    token_timer = 0.0  # Timer for passive token income (25 tokens per minute)
    
    # Load saved settings
    saved_settings = _load_settings()
    music_volume = saved_settings.get("music_volume", 100)  # 0-100

    window = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Merge Casino")
    canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    is_fullscreen = False

    menu_bg = None
    lobby_bg = None
    lobby2_bg = None
    try:
        base_dir = str(Path(__file__).resolve().parent)
    except:
        base_dir = str(Path.cwd())
    
    # Music playlist system
    music_tracks = ["bgm1.mp3", "bgm2.mp3", "bgm3.mp3", "bgm4.mp3", "bgm5.mp3", "bgm6.mp3", "bgm7.mp3"]
    current_track = None
    music_mode = "bgm"  # "bgm" (random playlist) or "disco" (dancefloor)
    
    def play_random_track():
        nonlocal current_track
        # Only allow the playlist to change music while in bgm mode.
        # This prevents queued MUSIC_END_EVENTs from overriding dancefloor music.
        if music_mode != "bgm":
            return
        # Pick a random track, but not the same as the previous one
        available_tracks = [t for t in music_tracks if t != current_track]
        next_track = random.choice(available_tracks)
        current_track = next_track
        try:
            music_path = os.path.join(base_dir, "assets", "music", next_track)
            # Clear any queued music-end events so a previous track can't immediately
            # trigger another random pick after we switch.
            try:
                pygame.event.clear(MUSIC_END_EVENT)
            except Exception:
                pass
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(music_volume / 100.0)
            pygame.mixer.music.play()  # Play once, then we'll pick another
        except Exception as e:
            print(f"Could not load music {next_track}: {e}")
    
    # Set up music end event
    MUSIC_END_EVENT = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END_EVENT)

    def _enter_dancefloor_music() -> None:
        nonlocal music_mode, disco_music_playing
        if music_mode == "disco":
            return
        if not disco_music_path:
            return
        music_mode = "disco"
        disco_music_playing = True
        try:
            # Prevent any queued end events (from bgm) from restarting playlist music.
            try:
                pygame.event.clear(MUSIC_END_EVENT)
            except Exception:
                pass
            # Disable music end events while looping disco.
            try:
                pygame.mixer.music.set_endevent()
            except TypeError:
                pygame.mixer.music.set_endevent(0)

            pygame.mixer.music.stop()
            pygame.mixer.music.load(disco_music_path)
            pygame.mixer.music.set_volume(music_volume / 100.0)
            pygame.mixer.music.play(-1)  # Loop forever
        except Exception as e:
            print(f"Could not play disco music: {e}")
            # Fall back to bgm mode if disco couldn't start.
            disco_music_playing = False
            music_mode = "bgm"
            pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
            play_random_track()

    def _leave_dancefloor_music() -> None:
        nonlocal music_mode, disco_music_playing
        if music_mode != "disco":
            return
        music_mode = "bgm"
        disco_music_playing = False
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        # Re-enable end events for the playlist, then resume with a random track.
        pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
        try:
            pygame.event.clear(MUSIC_END_EVENT)
        except Exception:
            pass
        play_random_track()
    
    # Start playing first random track
    play_random_track()
    
    # Table size and positions (4 corners + center)
    TABLE_WIDTH = 370
    TABLE_HEIGHT = 250
    TABLE_MARGIN = 0
    
    # Top-left: Slot Machines
    table_slots = pygame.Rect(TABLE_MARGIN, TABLE_MARGIN, TABLE_WIDTH, TABLE_HEIGHT)
    # Top-right: Blackjack
    table_blackjack = pygame.Rect(BASE_WIDTH - TABLE_MARGIN - TABLE_WIDTH, TABLE_MARGIN, TABLE_WIDTH, TABLE_HEIGHT)
    # Bottom-left: Roulette
    table_roulette = pygame.Rect(TABLE_MARGIN, BASE_HEIGHT - TABLE_MARGIN - TABLE_HEIGHT, TABLE_WIDTH, TABLE_HEIGHT)
    # Bottom-right: Lucky Wheel
    table_wheel = pygame.Rect(BASE_WIDTH - TABLE_MARGIN - TABLE_WIDTH, BASE_HEIGHT - TABLE_MARGIN - TABLE_HEIGHT, TABLE_WIDTH, TABLE_HEIGHT)
    
    # All tables for collision/rendering
    all_tables = [table_slots, table_blackjack, table_roulette, table_wheel]
    interact_near_px = 22.0
    
    try:
        menu_bg_path = os.path.join(base_dir, "assets", "img", "mainmenu.png")
        menu_bg = pygame.image.load(menu_bg_path).convert_alpha()
        # Remove fixed scaling here
    except Exception:
        menu_bg = None

    try:
        lobby_bg_path = os.path.join(base_dir, "assets", "img", "lobby-bg.png")
        lobby_bg = pygame.image.load(lobby_bg_path).convert_alpha()
    except Exception:
        lobby_bg = None
    
    try:
        lobby2_bg_path = os.path.join(base_dir, "assets", "img", "bg2 (2).png")
        lobby2_bg = pygame.image.load(lobby2_bg_path).convert_alpha()
    except Exception:
        lobby2_bg = None
    
    # Load cocktail image
    cocktail_img = None
    try:
        cocktail_path = os.path.join(base_dir, "assets", "img", "cocktail.png")
        cocktail_img = pygame.image.load(cocktail_path).convert_alpha()
        cocktail_img = pygame.transform.smoothscale(cocktail_img, (40, 40))
    except Exception:
        cocktail_img = None
    
    # Load disco ball image
    disco_ball_img = None
    try:
        disco_ball_path = os.path.join(base_dir, "assets", "img", "discoball.gif")
        disco_ball_img = pygame.image.load(disco_ball_path).convert_alpha()
        disco_ball_img = pygame.transform.smoothscale(disco_ball_img, (100, 100))
    except Exception as e:
        print(f"Could not load disco ball: {e}")
        disco_ball_img = None
    
    # Load disco music
    disco_music_path = None
    try:
        disco_music_path = str(Path(base_dir) / "assets" / "music" / "TECHNOBUNKER.mp3")
        if not Path(disco_music_path).exists():
            print(f"Disco music file not found: {disco_music_path}")
            disco_music_path = None
    except Exception as e:
        print(f"Error setting disco music path: {e}")
        disco_music_path = None
    
    # Transition zones between lobbies
    ZONE_WIDTH = 60
    
    # Lobby 2 tables (same size/positions as lobby 1)
    lobby2_table_topleft = pygame.Rect(TABLE_MARGIN, TABLE_MARGIN, TABLE_WIDTH, TABLE_HEIGHT)
    lobby2_table_topright = pygame.Rect(BASE_WIDTH - TABLE_MARGIN - TABLE_WIDTH, TABLE_MARGIN, TABLE_WIDTH, TABLE_HEIGHT)
    lobby2_table_bottomleft = pygame.Rect(TABLE_MARGIN, BASE_HEIGHT - TABLE_MARGIN - TABLE_HEIGHT, TABLE_WIDTH, TABLE_HEIGHT)
    lobby2_table_bottomright = pygame.Rect(BASE_WIDTH - TABLE_MARGIN - TABLE_WIDTH, BASE_HEIGHT - TABLE_MARGIN - TABLE_HEIGHT, TABLE_WIDTH, TABLE_HEIGHT)
    lobby2_tables = [lobby2_table_topleft, lobby2_table_topright, lobby2_table_bottomleft, lobby2_table_bottomright]

    btn_width, btn_height = 200, 60
    spacing = 40
    start_btn_x = (BASE_WIDTH - (btn_width * 3 + spacing * 2)) // 2
    start_btn = Button(pygame.Rect(start_btn_x, 475, btn_width, btn_height), "Start game")
    settings_btn = Button(pygame.Rect(start_btn_x + btn_width + spacing, 475, btn_width, btn_height), "Settings")
    leave_btn = Button(pygame.Rect(start_btn_x + (btn_width + spacing) * 2, 475, btn_width, btn_height), "Leave")
    
    # Settings UI
    settings_panel_rect = pygame.Rect(BASE_WIDTH // 2 - 200, BASE_HEIGHT // 2 - 120, 400, 240)
    volume_slider = Slider(pygame.Rect(settings_panel_rect.left + 50, settings_panel_rect.centery, 300, 20), 0, 100, music_volume)
    back_btn = Button(pygame.Rect(settings_panel_rect.centerx - 75, settings_panel_rect.bottom - 70, 150, 50), "Back")
    
    def is_near_table(p: Player | None, table: pygame.Rect) -> bool:
        if p is None:
            return False
        return _circle_rect_distance(p.x, p.y, table) <= interact_near_px

    running = True
    while running:
        dt = CLOCK.tick(60) / 1000.0
        
        # Passive token income: 25 tokens every 60 seconds (works in ALL scenes)
        token_timer += dt
        if token_timer >= 60.0:
            tokens += 25
            token_timer -= 60.0

            # Also update active scene state, so income isn't lost
            if scene == "roulette" and "tokens" in roulette_state:
                roulette_state["tokens"] = roulette_state.get("tokens", 0) + 25
            if scene == "slotmachine" and "tokens" in slotmachine_state:
                slotmachine_state["tokens"] = slotmachine_state.get("tokens", 0) + 25
            if scene == "luckywheel" and "tokens" in luckywheel_state:
                luckywheel_state["tokens"] = luckywheel_state.get("tokens", 0) + 25
            if scene == "blackjack" and "tokens" in blackjack_state:
                blackjack_state["tokens"] = blackjack_state.get("tokens", 0) + 25
            if scene == "higherlower" and "tokens" in higherlower_state:
                higherlower_state["tokens"] = higherlower_state.get("tokens", 0) + 25

        # Update cocktail/drunk timers
        if holding_cocktail:
            cocktail_timer += dt
            if cocktail_timer >= cocktail_hold_duration:
                holding_cocktail = False
                drunk_active = True
                drunk_timer = 0.0
        
        if drunk_active:
            drunk_timer += dt
            if drunk_timer >= drunk_duration:
                drunk_active = False

        window_mouse_pos = pygame.mouse.get_pos()
        mouse_pos = _window_to_canvas_pos(window_mouse_pos, window.get_size())
        if mouse_pos is None:
            mouse_pos = (-1, -1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Play next random track when current one ends
            if event.type == MUSIC_END_EVENT:
                if music_mode == "bgm":
                    play_random_track()

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
                if scene == "settings":
                    scene = "menu"
                elif scene == "testscene":
                    scene = "game"
                elif scene == "roulette":
                    scene = "game"
                    roulette_state = {}
                elif scene == "slotmachine":
                    scene = "game"
                    slotmachine_state = {}
                elif scene == "luckywheel":
                    scene = "game"
                    luckywheel_state = {}
                elif scene == "blackjack":
                    scene = "game"
                    blackjack_state = {}
                elif scene == "higherlower":
                    scene = "lobby2"
                    player = Player((BASE_WIDTH - 80, BASE_HEIGHT - 80))
                    higherlower_state = {}
                elif scene == "lobby2":
                    # Ensure disco stops if we leave lobby2 while it is playing.
                    _leave_dancefloor_music()
                    scene = "game"
                    player = Player((BASE_WIDTH - 80, BASE_HEIGHT // 2))
                elif scene in ("game", "loading"):
                    scene = "menu"
                    player = None
                    loading_elapsed = 0.0
                else:
                    running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if scene == "game":
                    if is_near_table(player, table_roulette):
                        scene = "roulette"
                        roulette_state = {"tokens": tokens}
                    elif is_near_table(player, table_slots):
                        scene = "slotmachine"
                        slotmachine_state = {"tokens": tokens}
                    elif is_near_table(player, table_wheel):
                        scene = "luckywheel"
                        luckywheel_state = {"tokens": tokens}
                    elif is_near_table(player, table_blackjack):
                        scene = "blackjack"
                        blackjack_state = {"tokens": tokens}
                elif scene == "lobby2":
                    # Bottom-right: Higher or Lower
                    if is_near_table(player, lobby2_table_bottomright):
                        scene = "higherlower"
                        higherlower_state = {"tokens": tokens}
                    # Top-left: Bar stand (cocktail)
                    elif is_near_table(player, lobby2_table_topleft) and not holding_cocktail and not drunk_active:
                        holding_cocktail = True
                        cocktail_timer = 0.0

            # Smoke emote in lobby (B key)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                if scene in ("game", "lobby2") and player is not None:
                    player.trigger_emote()

            # Roulette controls
            if event.type == pygame.KEYDOWN and scene == "roulette":
                # First check if number input is handling the key
                roulette_state = handle_roulette_keypress(roulette_state, event)
                # Only process other keys if number input is not active
                if not roulette_state.get("number_input_active", False):
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

            # Slotmachine controls
            if event.type == pygame.KEYDOWN and scene == "slotmachine":
                if event.key == pygame.K_SPACE:
                    slotmachine_state = spin_slotmachine(slotmachine_state)
                elif event.key == pygame.K_UP:
                    slotmachine_state = change_slot_bet_amount(slotmachine_state, True)
                elif event.key == pygame.K_DOWN:
                    slotmachine_state = change_slot_bet_amount(slotmachine_state, False)

            # Lucky wheel controls
            if event.type == pygame.KEYDOWN and scene == "luckywheel":
                if event.key == pygame.K_SPACE:
                    luckywheel_state = spin_luckywheel(luckywheel_state)

            # Blackjack controls
            if event.type == pygame.KEYDOWN and scene == "blackjack":
                blackjack_state = handle_blackjack_keypress(blackjack_state, event.key)

            # Higher/Lower controls
            if event.type == pygame.KEYDOWN and scene == "higherlower":
                higherlower_state = handle_higherlower_keypress(higherlower_state, event.key)

            # Settings slider event handling
            if scene == "settings":
                if volume_slider.handle_event(event, mouse_pos):
                    music_volume = volume_slider.value
                    pygame.mixer.music.set_volume(music_volume / 100.0)
                    _save_settings({"music_volume": music_volume})

            # Menu/scene mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if scene == "menu":
                    if start_btn.handle_click(mouse_pos):
                        scene = "loading"
                        loading_elapsed = 0.0
                    elif settings_btn.handle_click(mouse_pos):
                        scene = "settings"
                        volume_slider.value = music_volume  # Sync slider with current volume
                    elif leave_btn.handle_click(mouse_pos):
                        running = False
                elif scene == "settings":
                    if back_btn.handle_click(mouse_pos):
                        scene = "menu"
                elif scene == "roulette":
                    roulette_state = handle_roulette_click(roulette_state, mouse_pos)
                elif scene == "slotmachine":
                    btn = slotmachine_state.get("button_rect")
                    if isinstance(btn, pygame.Rect) and btn.collidepoint(mouse_pos):
                        slotmachine_state = spin_slotmachine(slotmachine_state)
                elif scene == "luckywheel":
                    btn = luckywheel_state.get("button_rect")
                    if isinstance(btn, pygame.Rect) and btn.collidepoint(mouse_pos):
                        luckywheel_state = spin_luckywheel(luckywheel_state)
                elif scene == "blackjack":
                    blackjack_state = handle_blackjack_click(blackjack_state, mouse_pos)
                elif scene == "higherlower":
                    higherlower_state = handle_higherlower_click(higherlower_state, mouse_pos)

        # Draw
        canvas.fill(BG)

        # Get current window size for scaling backgrounds
        win_w, win_h = window.get_size()

        if scene == "menu":
            if menu_bg is not None:
                # Stretch background to window size of the canvas
                stretched_bg = pygame.transform.smoothscale(menu_bg, (BASE_WIDTH, BASE_HEIGHT))
                canvas.blit(stretched_bg, (0, 0))
            else:
                canvas.fill(BG)
            rainbow_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
            draw_rainbow_text(canvas, "Main Menu", 200, font=FONT_TITLE, time_offset=rainbow_time)
            start_btn.draw(canvas, mouse_pos)
            settings_btn.draw(canvas, mouse_pos)
            leave_btn.draw(canvas, mouse_pos)
            draw_center_text(canvas, "Tip: ESC = exit (menu) / back (game)", 580, font=FONT_TIP, color=(200, 200, 200))

        elif scene == "settings":
            if menu_bg is not None:
                stretched_bg = pygame.transform.smoothscale(menu_bg, (BASE_WIDTH, BASE_HEIGHT))
                canvas.blit(stretched_bg, (0, 0))
            else:
                canvas.fill(BG)
            # Draw settings panel background
            pygame.draw.rect(canvas, (35, 40, 50), settings_panel_rect, border_radius=16)
            pygame.draw.rect(canvas, (60, 70, 90), settings_panel_rect, width=3, border_radius=16)
            
            # Title
            title_surf = FONT.render("Settings", True, WHITE)
            title_rect = title_surf.get_rect(centerx=settings_panel_rect.centerx, top=settings_panel_rect.top + 20)
            canvas.blit(title_surf, title_rect)
            
            # Volume label
            volume_label = FONT_SMALL.render("Music Volume", True, WHITE)
            volume_label_rect = volume_label.get_rect(centerx=settings_panel_rect.centerx, top=settings_panel_rect.top + 70)
            canvas.blit(volume_label, volume_label_rect)
            
            # Volume slider
            volume_slider.draw(canvas, mouse_pos)
            
            # Volume percentage
            volume_text = FONT_SMALL.render(f"{volume_slider.value}%", True, (180, 200, 255))
            volume_text_rect = volume_text.get_rect(centerx=settings_panel_rect.centerx, top=volume_slider.rect.bottom + 10)
            canvas.blit(volume_text, volume_text_rect)
            
            # Back button
            back_btn.draw(canvas, mouse_pos)

        elif scene == "loading":
            loading_elapsed += dt
            draw_game_screen(canvas, title_font=FONT, hint_font=FONT_GAME_HINT)
            if loading_elapsed >= LOADING_DURATION_SECONDS:
                scene = "game"
                player = Player((BASE_WIDTH // 2, BASE_HEIGHT // 2))

        elif scene == "roulette":
            roulette_state = draw_roulette_scene(canvas, roulette_state, font=FONT)
            tokens = roulette_state.get("tokens", tokens)  # Update tokens from roulette

        elif scene == "slotmachine":
            slotmachine_state = draw_slotmachine_scene(canvas, slotmachine_state, font=FONT)
            tokens = slotmachine_state.get("tokens", tokens)

        elif scene == "luckywheel":
            luckywheel_state = draw_luckywheel_scene(canvas, luckywheel_state, font=FONT)
            tokens = luckywheel_state.get("tokens", tokens)

        elif scene == "blackjack":
            blackjack_state = draw_blackjack_scene(canvas, blackjack_state, font=FONT)
            tokens = blackjack_state.get("tokens", tokens)

        elif scene == "higherlower":
            higherlower_state = draw_higherlower_scene(canvas, higherlower_state, font=FONT)
            tokens = higherlower_state.get("tokens", tokens)

        elif scene == "lobby2":
            # Second lobby with bg2 background
            if lobby2_bg is not None:
                stretched_bg = pygame.transform.smoothscale(lobby2_bg, (BASE_WIDTH, BASE_HEIGHT))
                canvas.blit(stretched_bg, (0, 0))
            else:
                canvas.fill((60, 40, 80))

            if player is None:
                player = Player((80, BASE_HEIGHT // 2))

            keys = pygame.key.get_pressed()
            player.update(dt, keys, canvas.get_rect(), obstacles=[])
            
            # Check if player is on the dancefloor (top-right corner)
            on_dancefloor = lobby2_table_topright.collidepoint(player.x, player.y)
            player.set_dancing(on_dancefloor)
            
            # Handle disco music and ball when entering/leaving dancefloor
            if on_dancefloor and not was_on_dancefloor:
                # Just entered dancefloor - start disco!
                disco_ball_lowering = True
                disco_ball_y = -100
                _enter_dancefloor_music()
            elif not on_dancefloor and was_on_dancefloor:
                # Just left dancefloor - stop disco
                disco_ball_lowering = False
                disco_ball_y = -100
                _leave_dancefloor_music()
            
            was_on_dancefloor = on_dancefloor
            
            # Animate disco ball lowering
            if disco_ball_lowering:
                if disco_ball_y < disco_ball_target_y:
                    disco_ball_y += 150 * dt  # Lower at 150 pixels per second
                else:
                    disco_ball_y = disco_ball_target_y
            
            # Update disco ray timer
            disco_ray_timer += dt
            
            # Draw disco light rays when on dancefloor
            if on_dancefloor:
                # Draw colorful light rays from disco ball position
                disco_colors = [
                    (255, 50, 50),    # Red
                    (50, 255, 50),    # Green
                    (50, 50, 255),    # Blue
                    (255, 255, 50),   # Yellow
                    (255, 50, 255),   # Magenta
                    (50, 255, 255),   # Cyan
                    (255, 150, 50),   # Orange
                    (150, 50, 255),   # Purple
                ]
                ball_center_x = BASE_WIDTH - TABLE_MARGIN - TABLE_WIDTH // 2
                ball_center_y = int(disco_ball_y) + 50  # Center of ball
                
                # Draw 12 rotating rays
                num_rays = 12
                ray_rotation = disco_ray_timer * 2  # Rotate 2 radians per second
                for i in range(num_rays):
                    angle = (2 * math.pi * i / num_rays) + ray_rotation
                    ray_length = 600
                    end_x = ball_center_x + int(math.cos(angle) * ray_length)
                    end_y = ball_center_y + int(math.sin(angle) * ray_length)
                    color = disco_colors[i % len(disco_colors)]
                    
                    # Draw semi-transparent ray using a surface
                    ray_surf = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
                    pygame.draw.line(ray_surf, (*color, 80), (ball_center_x, ball_center_y), (end_x, end_y), 8)
                    canvas.blit(ray_surf, (0, 0))
                
                # Draw disco ball
                if disco_ball_img is not None:
                    ball_x = ball_center_x - 50
                    ball_y = int(disco_ball_y)
                    canvas.blit(disco_ball_img, (ball_x, ball_y))
                    
                    # Draw string from top to disco ball
                    pygame.draw.line(canvas, (100, 100, 100), (ball_center_x, 0), (ball_center_x, ball_y), 2)
            
            player.draw(canvas)
            
            # Draw cocktail when holding
            if holding_cocktail and cocktail_img is not None:
                cocktail_x = int(player.x + 15 if player._facing_right else player.x - 15 - 40)
                cocktail_y = int(player.y - 10)
                canvas.blit(cocktail_img, (cocktail_x, cocktail_y))
            
            # Check if player goes to left edge -> back to lobby1
            if player.x < ZONE_WIDTH:
                player.set_dancing(False)  # Stop dancing when leaving
                _leave_dancefloor_music()
                scene = "game"
                player = Player((BASE_WIDTH - 80, BASE_HEIGHT // 2))

            # Draw token counter
            token_text = f"Tokens: {tokens}"
            token_surf = FONT_SMALL.render(token_text, True, (255, 215, 0))
            token_rect = token_surf.get_rect(midtop=(BASE_WIDTH // 2, 10))
            pygame.draw.rect(canvas, (30, 30, 30), token_rect.inflate(20, 10), border_radius=8)
            canvas.blit(token_surf, token_rect)
            
            # Show 'E' popup when near bottom-right table (Higher/Lower)
            if is_near_table(player, lobby2_table_bottomright):
                popup = pygame.Rect(0, 0, 26, 26)
                popup.center = (int(player.x), int(player.y - (player.radius + 18)))
                popup.clamp_ip(canvas.get_rect())
                pygame.draw.rect(canvas, (20, 20, 25), popup, border_radius=4)
                pygame.draw.rect(canvas, (255, 255, 255), popup, width=2, border_radius=4)
                e_surf = FONT_TIP.render("E", True, (255, 255, 255))
                e_rect = e_surf.get_rect(center=popup.center)
                canvas.blit(e_surf, e_rect)
            
            # Show 'E' popup when near top-left bar (Cocktail)
            if is_near_table(player, lobby2_table_topleft) and not holding_cocktail and not drunk_active:
                popup = pygame.Rect(0, 0, 26, 26)
                popup.center = (int(player.x), int(player.y - (player.radius + 18)))
                popup.clamp_ip(canvas.get_rect())
                pygame.draw.rect(canvas, (20, 20, 25), popup, border_radius=4)
                pygame.draw.rect(canvas, (255, 255, 255), popup, width=2, border_radius=4)
                e_surf = FONT_TIP.render("E", True, (255, 255, 255))
                e_rect = e_surf.get_rect(center=popup.center)
                canvas.blit(e_surf, e_rect)
            
            # Show dancefloor hint when on it
            if on_dancefloor:
                dance_hint = FONT_TIP.render("~ DANCEFLOOR ~", True, (255, 100, 255))
                dance_rect = dance_hint.get_rect(center=(lobby2_table_topright.centerx, lobby2_table_topright.bottom + 20))
                canvas.blit(dance_hint, dance_rect)
                
                # Disco color flash effect
                disco_flash_timer += dt
                if disco_flash_timer >= 0.15:  # Flash every 0.15 seconds
                    disco_flash_timer = 0.0
                    disco_flash_index = (disco_flash_index + 1) % len(disco_flash_colors)
                
                flash_color = disco_flash_colors[disco_flash_index]
                flash_overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
                flash_overlay.fill((*flash_color, 40))  # Semi-transparent color flash
                canvas.blit(flash_overlay, (0, 0))
            
            # Show arrow hint to go back
            hint_surf = FONT_TIP.render("< Back to Lobby 1", True, (200, 200, 200))
            canvas.blit(hint_surf, (10, BASE_HEIGHT // 2 - 10))

        else:  # scene == "game"
            if lobby_bg is not None:
                stretched_bg = pygame.transform.smoothscale(lobby_bg, (BASE_WIDTH, BASE_HEIGHT))
                canvas.blit(stretched_bg, (0, 0))
            else:
                canvas.fill((40, 60, 80))

            if player is None:
                player = Player((BASE_WIDTH // 2, BASE_HEIGHT // 2))

            keys = pygame.key.get_pressed()
            player.update(dt, keys, canvas.get_rect(), obstacles=[])
            player.draw(canvas)
            
            # Check if player goes to right edge -> lobby2
            if player.x > BASE_WIDTH - ZONE_WIDTH:
                scene = "lobby2"
                player = Player((80, BASE_HEIGHT // 2))

            # Tables are invisible interaction zones (no collision)

            # Draw token counter at top center
            token_text = f"Tokens: {tokens}"
            token_surf = FONT_SMALL.render(token_text, True, (255, 215, 0))
            token_rect = token_surf.get_rect(midtop=(BASE_WIDTH // 2, 10))
            pygame.draw.rect(canvas, (30, 30, 30), token_rect.inflate(20, 10), border_radius=8)
            canvas.blit(token_surf, token_rect)
            
            # Show arrow hint to go to lobby2
            hint_surf = FONT_TIP.render("Lobby 2 >", True, (200, 200, 200))
            canvas.blit(hint_surf, (BASE_WIDTH - 80, BASE_HEIGHT // 2 - 10))

            # Show 'E' popup when near any interactive table
            near_table = None
            if is_near_table(player, table_roulette):
                near_table = table_roulette
            elif is_near_table(player, table_slots):
                near_table = table_slots
            elif is_near_table(player, table_wheel):
                near_table = table_wheel
            elif is_near_table(player, table_blackjack):
                near_table = table_blackjack
            
            if near_table is not None:
                popup = pygame.Rect(0, 0, 26, 26)
                popup.center = (int(player.x), int(player.y - (player.radius + 18)))
                popup.clamp_ip(canvas.get_rect())
                pygame.draw.rect(canvas, (20, 20, 25), popup, border_radius=4)
                pygame.draw.rect(canvas, (255, 255, 255), popup, width=2, border_radius=4)
                e_surf = FONT_TIP.render("E", True, (255, 255, 255))
                e_rect = e_surf.get_rect(center=popup.center)
                canvas.blit(e_surf, e_rect)

        # Present surface (may be post-processed)
        present_canvas = canvas
        
        # Apply disco pulse effect when on dancefloor
        if scene == "lobby2" and was_on_dancefloor:
            disco_pulse_timer += dt
            # Pulse scale oscillates between 1.0 and 1.05 using sine wave
            pulse_scale = 1.0 + 0.05 * abs(math.sin(disco_pulse_timer * 12))  # 12 = pulse speed
            
            # Scale canvas from center
            pulse_width = int(BASE_WIDTH * pulse_scale)
            pulse_height = int(BASE_HEIGHT * pulse_scale)
            pulsed_canvas = pygame.transform.smoothscale(present_canvas, (pulse_width, pulse_height))
            
            # Create a new surface and blit the scaled canvas centered
            pulse_result = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
            offset_x = (pulse_width - BASE_WIDTH) // 2
            offset_y = (pulse_height - BASE_HEIGHT) // 2
            pulse_result.blit(pulsed_canvas, (-offset_x, -offset_y))
            present_canvas = pulse_result

        # Apply drunk effect if active (greenish tint + wave distortion)
        # Important: do NOT overwrite `canvas` across frames, otherwise the tint accumulates
        # and becomes opaque (this is especially noticeable on macOS).
        if drunk_active:
            drunk_canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT)).convert()
            wave_amplitude = 8  # How far pixels shift
            wave_frequency = 0.03  # How tight the waves are
            time_factor = drunk_timer * 5  # Speed of wave animation

            # Use efficient row-by-row blitting instead of pixel-by-pixel
            for y in range(BASE_HEIGHT):
                offset = int(wave_amplitude * math.sin(wave_frequency * y + time_factor))
                # Blit the entire row with offset
                drunk_canvas.blit(canvas, (offset, y), (0, y, BASE_WIDTH, 1))
                # Fill gaps on edges
                if offset > 0:
                    drunk_canvas.blit(canvas, (0, y), (BASE_WIDTH - offset, y, offset, 1))
                elif offset < 0:
                    drunk_canvas.blit(canvas, (BASE_WIDTH + offset, y), (0, y, -offset, 1))

            # Apply green tint overlay using per-pixel alpha (more consistent across platforms)
            green_overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
            green_overlay.fill((0, 100, 0, 70))
            drunk_canvas.blit(green_overlay, (0, 0))

            present_canvas = drunk_canvas

        # Now always stretch the (possibly post-processed) canvas to fill the window
        _present(present_canvas, window)
        pygame.display.flip()
        
        # Required for pygbag - yield control back to browser
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())

