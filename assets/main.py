import math
import pygame
from sys import exit
import random
import asyncio
import json
import os

# =====================================
# INITIALIZE
# =====================================
pygame.init()

# Enable native mobile/SDL text input support for login fields
pygame.key.start_text_input()

# =====================================
# SCREEN SETTINGS
# =====================================
GAME_WIDTH = 400
GAME_HEIGHT = 700

window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird Deluxe")

clock = pygame.time.Clock()

# =====================================
# DATABASE
# =====================================
DATABASE_FILE = "accounts.json"

if not os.path.exists(DATABASE_FILE):

    with open(DATABASE_FILE, "w") as file:
        json.dump({}, file)


def load_accounts():

    with open(DATABASE_FILE, "r") as file:
        return json.load(file)


def save_accounts(data):

    with open(DATABASE_FILE, "w") as file:
        json.dump(data, file, indent=4)


# =====================================
# COLORS
# =====================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 70, 70)
GREEN = (0, 255, 120)
YELLOW = (255, 230, 0)
BLUE = (100, 180, 255)
GRAY = (50, 50, 50)

# Enhanced UI colors
DARK_OVERLAY = (20, 20, 40)
CARD_BG = (30, 35, 55)
CARD_BORDER = (60, 70, 100)
INPUT_BG = (40, 45, 65)
INPUT_BORDER = (80, 90, 120)
INPUT_ACTIVE_BORDER = (100, 200, 255)
INPUT_TEXT = (220, 225, 235)
LABEL_COLOR = (150, 160, 185)
BTN_LOGIN = (46, 204, 113)
BTN_LOGIN_HOVER = (39, 174, 96)
BTN_REGISTER = (52, 152, 219)
BTN_REGISTER_HOVER = (41, 128, 185)
MSG_SUCCESS = (46, 204, 113)
MSG_ERROR = (231, 76, 60)
TITLE_GLOW = (255, 200, 50)
SUBTITLE_COLOR = (180, 190, 210)

# Difficulty button colors
BTN_EASY = (46, 204, 113)
BTN_EASY_HOVER = (39, 174, 96)
BTN_MEDIUM = (243, 156, 18)
BTN_MEDIUM_HOVER = (211, 132, 10)
BTN_HARD = (231, 76, 60)
BTN_HARD_HOVER = (192, 57, 43)
BTN_EXIT = (100, 110, 140)
BTN_EXIT_HOVER = (80, 88, 115)

# HUD colors
HUD_BADGE_BG = (0, 0, 0)
HUD_SCORE_OUTLINE = (0, 0, 0)
SCORE_GOLD = (255, 215, 0)

# =====================================
# FONTS
# =====================================
title_font = pygame.font.SysFont("Arial", 50, bold=True)
menu_font = pygame.font.SysFont("Arial", 28)
score_font = pygame.font.SysFont("Arial", 40, bold=True)

# Enhanced UI fonts
login_title_font = pygame.font.SysFont("Arial", 44, bold=True)
login_subtitle_font = pygame.font.SysFont("Arial", 16)
label_font = pygame.font.SysFont("Arial", 15, bold=True)
input_font = pygame.font.SysFont("Arial", 22)
button_font = pygame.font.SysFont("Arial", 20, bold=True)
msg_font = pygame.font.SysFont("Arial", 17, bold=True)
hud_score_font = pygame.font.SysFont("Arial", 48, bold=True)
hud_label_font = pygame.font.SysFont("Arial", 16, bold=True)
hud_value_font = pygame.font.SysFont("Arial", 18, bold=True)
gameover_title_font = pygame.font.SysFont("Arial", 52, bold=True)
gameover_label_font = pygame.font.SysFont("Arial", 15)
gameover_score_font = pygame.font.SysFont("Arial", 36, bold=True)
gameover_hint_font = pygame.font.SysFont("Arial", 14)
difficulty_label_font = pygame.font.SysFont("Arial", 13, bold=True)

# =====================================
# LOAD IMAGES
# =====================================
background_image = pygame.image.load(
    "flappybirdbg.png"
).convert()

background_image = pygame.transform.scale(
    background_image,
    (GAME_WIDTH, GAME_HEIGHT)
)

bird_width = 40
bird_height = 30

bird_image = pygame.image.load(
    "flappybird.png"
).convert_alpha()

bird_image = pygame.transform.scale(
    bird_image,
    (bird_width, bird_height)
)

pipe_width = 70
pipe_height = 500

top_pipe_image = pygame.image.load(
    "toppipe.png"
).convert_alpha()

top_pipe_image = pygame.transform.scale(
    top_pipe_image,
    (pipe_width, pipe_height)
)

bottom_pipe_image = pygame.image.load(
    "bottompipe.png"
).convert_alpha()

bottom_pipe_image = pygame.transform.scale(
    bottom_pipe_image,
    (pipe_width, pipe_height)
)

# =====================================
# GAME VARIABLES
# =====================================
gravity = 0.4
jump_strength = -7

bird_x = 70
bird_y = GAME_HEIGHT // 2

bird_velocity = 0

score = 0
high_score = 0

game_started = False
game_over = False

difficulty = "MEDIUM"

pipe_gap = 180
pipe_speed = -4

pipes = []

# =====================================
# LOGIN SYSTEM
# =====================================
logged_in = False

current_user = None

typing_username = True

username_input = ""
password_input = ""

message = ""
message_timer = 0

# Animation state
login_bird_bob = 0
login_bg_scroll = 0
menu_bird_bob = 0

# =====================================
# BUTTONS (login buttons repositioned for card layout)
# =====================================
login_button = pygame.Rect(85, 488, 110, 44)
register_button = pygame.Rect(205, 488, 110, 44)

easy_button = pygame.Rect(100, 350, 200, 50)
medium_button = pygame.Rect(100, 430, 200, 50)
hard_button = pygame.Rect(100, 510, 200, 50)

exit_button = pygame.Rect(100, 590, 200, 50)

# =====================================
# DIFFICULTY
# =====================================


def set_difficulty(level):

    global difficulty
    global pipe_gap
    global pipe_speed
    global gravity

    difficulty = level

    if level == "EASY":

        pipe_gap = 240
        pipe_speed = -3
        gravity = 0.35

    elif level == "MEDIUM":

        pipe_gap = 180
        pipe_speed = -4
        gravity = 0.4

    elif level == "HARD":

        pipe_gap = 140
        pipe_speed = -6
        gravity = 0.5


set_difficulty("MEDIUM")

# =====================================
# BIRD
# =====================================
bird = pygame.Rect(
    bird_x,
    bird_y,
    bird_width,
    bird_height
)

# =====================================
# PIPE TIMER
# =====================================
pipe_delay = 1500
last_pipe_time = pygame.time.get_ticks()

# =====================================
# LOGIN FUNCTION
# =====================================


def login():

    global current_user
    global high_score
    global message

    accounts = load_accounts()

    if username_input in accounts:

        if accounts[username_input]["password"] == password_input:

            current_user = username_input

            high_score = accounts[current_user]["high_score"]

            message = "LOGIN SUCCESS"

            return True

    message = "INVALID ACCOUNT"

    return False

# =====================================
# REGISTER FUNCTION
# =====================================


def register():

    global message
    global current_user
    global high_score

    accounts = load_accounts()

    if username_input in accounts:

        message = "USERNAME EXISTS"

        return False

    accounts[username_input] = {
        "password": password_input,
        "high_score": 0
    }

    save_accounts(accounts)

    # Auto-login after registration
    current_user = username_input
    high_score = 0

    message = "ACCOUNT CREATED"

    return True

# =====================================
# SAVE HIGH SCORE
# =====================================


def save_high_score():

    accounts = load_accounts()

    if current_user is None:
        return

    if high_score > accounts[current_user]["high_score"]:

        accounts[current_user]["high_score"] = high_score

        save_accounts(accounts)


def get_web_login_request():

    try:
        browser_platform = __import__("platform")
    except Exception:
        return None

    window = getattr(browser_platform, "window", None)
    if window is None:
        return None

    try:
        req = window.loginRequest
    except Exception:
        return None

    if not req:
        return None

    try:
        window.loginRequest = None
    except Exception:
        pass

    action = getattr(req, "action", None)
    username = getattr(req, "username", None)
    password = getattr(req, "password", None)

    if action and username is not None and password is not None:
        return {
            "action": action,
            "username": username,
            "password": password,
        }

    return None


def hide_web_login_overlay():

    try:
        browser_platform = __import__("platform")
    except Exception:
        return

    window = getattr(browser_platform, "window", None)
    if window is None:
        return

    try:
        hide_fn = window.hideLoginOverlay
    except Exception:
        return

    try:
        hide_fn()
    except Exception:
        return

# =====================================
# CREATE PIPES
# =====================================


def create_pipes():

    random_y = random.randint(-350, -120)

    top_pipe = pygame.Rect(
        GAME_WIDTH,
        random_y,
        pipe_width,
        pipe_height
    )

    bottom_pipe = pygame.Rect(
        GAME_WIDTH,
        random_y + pipe_height + pipe_gap,
        pipe_width,
        pipe_height
    )

    pipes.append({
        "rect": top_pipe,
        "top": True,
        "passed": False
    })

    pipes.append({
        "rect": bottom_pipe,
        "top": False,
        "passed": False
    })

# =====================================
# RESET GAME
# =====================================


def reset_game():

    global bird_y
    global bird_velocity
    global score
    global game_over

    bird_y = float(GAME_HEIGHT // 2)
    bird.y = int(bird_y)

    bird_velocity = 0

    score = 0

    pipes.clear()

    game_over = False

# =====================================
# DRAW CENTER TEXT
# =====================================


def draw_center_text(text, font, color, y):

    render = font.render(text, True, color)

    window.blit(
        render,
        (
            GAME_WIDTH // 2 - render.get_width() // 2,
            y
        )
    )

# =====================================
# SHARED UI HELPERS
# =====================================


def draw_rounded_rect(surface, color, rect, radius, alpha=255):
    """Draw a rounded rectangle with optional alpha."""
    if alpha < 255:
        shape = pygame.Surface(
            (rect[2], rect[3]), pygame.SRCALPHA
        )
        pygame.draw.rect(
            shape, (*color, alpha),
            (0, 0, rect[2], rect[3]),
            border_radius=radius
        )
        surface.blit(shape, (rect[0], rect[1]))
    else:
        pygame.draw.rect(
            surface, color, rect, border_radius=radius
        )


def draw_outlined_text(surface, text, font, color, outline_color, x, y, outline=2):
    """Draw text with an outline/shadow for readability."""
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx != 0 or dy != 0:
                shadow = font.render(text, True, outline_color)
                surface.blit(shadow, (x + dx, y + dy))
    render = font.render(text, True, color)
    surface.blit(render, (x, y))


def draw_outlined_center_text(surface, text, font, color, outline_color, y, outline=2):
    """Draw outlined text centered horizontally."""
    render = font.render(text, True, color)
    x = GAME_WIDTH // 2 - render.get_width() // 2
    draw_outlined_text(surface, text, font, color,
                       outline_color, x, y, outline)


def draw_styled_button(rect, text, color, hover_color, text_color=WHITE, is_active=False):
    """Draw a button with hover effect, shadow, and optional active indicator."""
    mouse_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mouse_pos)
    btn_color = hover_color if is_hover else color

    # Shadow
    draw_rounded_rect(
        window, (0, 0, 0),
        (rect.x + 2, rect.y + 3, rect.width, rect.height),
        10, alpha=70
    )

    # Button body
    draw_rounded_rect(
        window, btn_color,
        (rect.x, rect.y, rect.width, rect.height), 10
    )

    # Active difficulty border glow
    if is_active:
        pygame.draw.rect(
            window, WHITE,
            (rect.x - 2, rect.y - 2,
             rect.width + 4, rect.height + 4),
            width=2, border_radius=12
        )
        # Small indicator dot
        pygame.draw.circle(
            window, WHITE,
            (rect.x + 12, rect.centery), 4
        )

    # Hover highlight
    if is_hover:
        highlight = pygame.Surface(
            (rect.width, rect.height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            highlight, (255, 255, 255, 30),
            (0, 0, rect.width, rect.height),
            border_radius=10
        )
        window.blit(highlight, (rect.x, rect.y))

    # Text
    lbl = button_font.render(text, True, text_color)
    window.blit(
        lbl,
        (rect.centerx - lbl.get_width() // 2,
         rect.centery - lbl.get_height() // 2)
    )


# =====================================
# LOGIN SCREEN (ENHANCED)
# =====================================


def draw_login_screen():

    global login_bird_bob, login_bg_scroll

    import math

    # --- Scrolling background ---
    login_bg_scroll = (login_bg_scroll + 0.5) % GAME_WIDTH
    window.blit(background_image, (-login_bg_scroll, 0))
    window.blit(
        background_image,
        (GAME_WIDTH - login_bg_scroll, 0)
    )

    # --- Dark overlay ---
    overlay = pygame.Surface(
        (GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA
    )
    overlay.fill((15, 15, 35, 180))
    window.blit(overlay, (0, 0))

    # --- Bobbing bird mascot ---
    login_bird_bob += 0.06
    bob_offset = math.sin(login_bird_bob) * 8

    bird_login_img = pygame.transform.scale(
        bird_image, (64, 48)
    )
    bird_login_x = GAME_WIDTH // 2 - 32
    bird_login_y = 68 + bob_offset
    window.blit(bird_login_img, (bird_login_x, bird_login_y))

    # --- Title ---
    title_text = login_title_font.render(
        "FLAPPY BIRD", True, TITLE_GLOW
    )
    title_x = GAME_WIDTH // 2 - title_text.get_width() // 2
    title_y = 128

    # Title shadow
    shadow = login_title_font.render(
        "FLAPPY BIRD", True, (0, 0, 0)
    )
    window.blit(shadow, (title_x + 2, title_y + 2))
    window.blit(title_text, (title_x, title_y))

    # Subtitle
    subtitle = login_subtitle_font.render(
        "Sign in to save your high scores", True,
        SUBTITLE_COLOR
    )
    window.blit(
        subtitle,
        (GAME_WIDTH // 2 - subtitle.get_width() // 2, 178)
    )

    # --- Card panel ---
    card_x, card_y = 45, 210
    card_w, card_h = 310, 350

    # Card shadow
    draw_rounded_rect(
        window, (0, 0, 0), (card_x + 4, card_y + 4, card_w, card_h),
        16, alpha=80
    )
    # Card background
    draw_rounded_rect(
        window, CARD_BG, (card_x, card_y, card_w, card_h),
        16, alpha=230
    )
    # Card border
    pygame.draw.rect(
        window, CARD_BORDER,
        (card_x, card_y, card_w, card_h),
        width=1, border_radius=16
    )

    # --- Username field ---
    field_x = card_x + 20
    field_w = card_w - 40

    # Label
    user_label = label_font.render("USERNAME", True, LABEL_COLOR)
    window.blit(user_label, (field_x, card_y + 24))

    # Input box
    user_rect = (field_x, card_y + 46, field_w, 42)
    border_color = INPUT_ACTIVE_BORDER if typing_username else INPUT_BORDER
    draw_rounded_rect(window, INPUT_BG, user_rect, 8)
    pygame.draw.rect(
        window, border_color, user_rect,
        width=2, border_radius=8
    )

    # Active indicator glow
    if typing_username:
        glow_surf = pygame.Surface(
            (field_w + 6, 48), pygame.SRCALPHA
        )
        pygame.draw.rect(
            glow_surf, (*INPUT_ACTIVE_BORDER, 40),
            (0, 0, field_w + 6, 48), border_radius=10
        )
        window.blit(glow_surf, (field_x - 3, card_y + 43))

    # Username text with cursor
    display_user = username_input
    if typing_username and pygame.time.get_ticks() % 1000 < 500:
        display_user += "|"
    user_text = input_font.render(display_user, True, INPUT_TEXT)
    # Clip text to field
    clip_rect = pygame.Rect(
        field_x + 12, card_y + 52, field_w - 24, 30
    )
    window.set_clip(clip_rect)
    # Right-align if text overflows
    text_x = field_x + 12
    if user_text.get_width() > field_w - 24:
        text_x = field_x + 12 + (field_w - 24) - user_text.get_width()
    window.blit(user_text, (text_x, card_y + 54))
    window.set_clip(None)

    # Placeholder
    if not username_input and not typing_username:
        ph = input_font.render(
            "Enter username", True, (90, 95, 115)
        )
        window.blit(ph, (field_x + 12, card_y + 54))

    # --- Password field ---
    pass_label = label_font.render("PASSWORD", True, LABEL_COLOR)
    window.blit(pass_label, (field_x, card_y + 108))

    pass_rect = (field_x, card_y + 130, field_w, 42)
    border_color_p = INPUT_ACTIVE_BORDER if not typing_username else INPUT_BORDER
    draw_rounded_rect(window, INPUT_BG, pass_rect, 8)
    pygame.draw.rect(
        window, border_color_p, pass_rect,
        width=2, border_radius=8
    )

    if not typing_username:
        glow_surf2 = pygame.Surface(
            (field_w + 6, 48), pygame.SRCALPHA
        )
        pygame.draw.rect(
            glow_surf2, (*INPUT_ACTIVE_BORDER, 40),
            (0, 0, field_w + 6, 48), border_radius=10
        )
        window.blit(glow_surf2, (field_x - 3, card_y + 127))

    hidden_pw = "\u2022" * len(password_input)
    if not typing_username and pygame.time.get_ticks() % 1000 < 500:
        hidden_pw += "|"
    pass_text = input_font.render(hidden_pw, True, INPUT_TEXT)
    clip_rect2 = pygame.Rect(
        field_x + 12, card_y + 136, field_w - 24, 30
    )
    window.set_clip(clip_rect2)
    text_x2 = field_x + 12
    if pass_text.get_width() > field_w - 24:
        text_x2 = field_x + 12 + (field_w - 24) - pass_text.get_width()
    window.blit(pass_text, (text_x2, card_y + 138))
    window.set_clip(None)

    if not password_input and typing_username:
        ph2 = input_font.render(
            "Enter password", True, (90, 95, 115)
        )
        window.blit(ph2, (field_x + 12, card_y + 138))

    # --- Tab hint ---
    tab_hint = login_subtitle_font.render(
        "Press TAB to switch fields", True, (100, 110, 140)
    )
    window.blit(
        tab_hint,
        (GAME_WIDTH // 2 - tab_hint.get_width() // 2,
         card_y + 184)
    )

    mobile_hint = login_subtitle_font.render(
        "Tap a field to open mobile keyboard", True,
        (100, 110, 140)
    )
    window.blit(
        mobile_hint,
        (GAME_WIDTH // 2 - mobile_hint.get_width() // 2,
         card_y + 206)
    )

    # --- Buttons ---
    mouse_pos = pygame.mouse.get_pos()

    # Login button
    login_hover = login_button.collidepoint(mouse_pos)
    btn_login_color = BTN_LOGIN_HOVER if login_hover else BTN_LOGIN
    # Shadow
    draw_rounded_rect(
        window, (0, 0, 0),
        (login_button.x + 2, login_button.y + 3,
         login_button.width, login_button.height),
        10, alpha=60
    )
    draw_rounded_rect(
        window, btn_login_color,
        (login_button.x, login_button.y,
         login_button.width, login_button.height),
        10
    )
    login_lbl = button_font.render("LOGIN", True, WHITE)
    window.blit(
        login_lbl,
        (login_button.centerx - login_lbl.get_width() // 2,
         login_button.centery - login_lbl.get_height() // 2)
    )

    # Register button
    reg_hover = register_button.collidepoint(mouse_pos)
    btn_reg_color = BTN_REGISTER_HOVER if reg_hover else BTN_REGISTER
    draw_rounded_rect(
        window, (0, 0, 0),
        (register_button.x + 2, register_button.y + 3,
         register_button.width, register_button.height),
        10, alpha=60
    )
    draw_rounded_rect(
        window, btn_reg_color,
        (register_button.x, register_button.y,
         register_button.width, register_button.height),
        10
    )
    reg_lbl = button_font.render("REGISTER", True, WHITE)
    window.blit(
        reg_lbl,
        (register_button.centerx - reg_lbl.get_width() // 2,
         register_button.centery - reg_lbl.get_height() // 2)
    )

    # --- Message ---
    if message:
        is_success = message in ("LOGIN SUCCESS", "ACCOUNT CREATED")
        msg_color = MSG_SUCCESS if is_success else MSG_ERROR

        # Message pill background
        msg_render = msg_font.render(message, True, msg_color)
        msg_w = msg_render.get_width() + 30
        msg_h = 32
        msg_x = GAME_WIDTH // 2 - msg_w // 2
        msg_y = card_y + card_h - 38

        pill_color = (
            (30, 60, 35) if is_success else (60, 30, 30)
        )
        draw_rounded_rect(
            window, pill_color,
            (msg_x, msg_y, msg_w, msg_h), 8, alpha=200
        )
        window.blit(
            msg_render,
            (GAME_WIDTH // 2 - msg_render.get_width() // 2,
             msg_y + 5)
        )

    # --- Footer hints ---
    hint1 = login_subtitle_font.render(
        "ENTER = Login  |  F2 = Register  |  ESC = Quit",
        True, (100, 105, 130)
    )
    window.blit(
        hint1,
        (GAME_WIDTH // 2 - hint1.get_width() // 2,
         GAME_HEIGHT - 40)
    )

# =====================================
# DRAW MENU (ENHANCED)
# =====================================


def draw_menu():

    global menu_bird_bob

    # Restore button positions for menu layout
    easy_button.update(100, 300, 200, 50)
    medium_button.update(100, 370, 200, 50)
    hard_button.update(100, 440, 200, 50)
    exit_button.update(100, 520, 200, 50)

    window.blit(background_image, (0, 0))

    # --- Subtle dark gradient overlay at top for text readability ---
    top_overlay = pygame.Surface((GAME_WIDTH, 280), pygame.SRCALPHA)
    for y_line in range(280):
        alpha = max(0, 140 - y_line // 2)
        pygame.draw.line(
            top_overlay, (10, 10, 30, alpha),
            (0, y_line), (GAME_WIDTH, y_line)
        )
    window.blit(top_overlay, (0, 0))

    # --- Bobbing bird mascot ---
    menu_bird_bob += 0.05
    bob = math.sin(menu_bird_bob) * 6
    menu_bird_img = pygame.transform.scale(bird_image, (56, 42))
    window.blit(
        menu_bird_img,
        (GAME_WIDTH // 2 - 28, 52 + bob)
    )

    # --- Welcome badge ---
    welcome_text = f"Welcome, {current_user}!"
    w_render = hud_label_font.render(welcome_text, True, WHITE)
    badge_w = w_render.get_width() + 24
    badge_x = GAME_WIDTH // 2 - badge_w // 2
    draw_rounded_rect(
        window, (0, 0, 0),
        (badge_x, 102, badge_w, 26), 13, alpha=120
    )
    window.blit(
        w_render,
        (GAME_WIDTH // 2 - w_render.get_width() // 2, 106)
    )

    # --- Title with shadow ---
    draw_outlined_center_text(
        window, "FLAPPY BIRD",
        gameover_title_font, TITLE_GLOW, (80, 50, 0), 136, 3
    )

    # --- "Tap to Start" with pulsing alpha ---
    pulse = abs(math.sin(pygame.time.get_ticks() / 600)) * 80 + 175
    tap_surf = pygame.Surface((GAME_WIDTH, 40), pygame.SRCALPHA)
    tap_text = menu_font.render("Tap Screen to Start", True, WHITE)
    tap_surf.set_alpha(int(pulse))
    tap_surf.blit(
        tap_text,
        (GAME_WIDTH // 2 - tap_text.get_width() // 2, 0)
    )
    window.blit(tap_surf, (0, 210))

    # --- Keyboard hints ---
    keys_hint = gameover_hint_font.render(
        "SPACE = Start  |  1/2/3 = Difficulty  |  ESC = Exit",
        True, (180, 190, 210)
    )
    window.blit(
        keys_hint,
        (GAME_WIDTH // 2 - keys_hint.get_width() // 2, 248)
    )

    # --- Difficulty section ---
    diff_label = difficulty_label_font.render(
        "SELECT DIFFICULTY (1/2/3)", True, (200, 210, 230)
    )
    window.blit(
        diff_label,
        (GAME_WIDTH // 2 - diff_label.get_width() // 2, 265)
    )

    # Separator line
    line_w = 160
    line_x = GAME_WIDTH // 2 - line_w // 2
    pygame.draw.line(
        window, (200, 210, 230, 80),
        (line_x, 284), (line_x + line_w, 284), 1
    )

    # --- Difficulty buttons with active indicator ---
    draw_styled_button(
        easy_button, "EASY",
        BTN_EASY, BTN_EASY_HOVER, WHITE,
        is_active=(difficulty == "EASY")
    )
    draw_styled_button(
        medium_button, "MEDIUM",
        BTN_MEDIUM, BTN_MEDIUM_HOVER, WHITE,
        is_active=(difficulty == "MEDIUM")
    )
    draw_styled_button(
        hard_button, "HARD",
        BTN_HARD, BTN_HARD_HOVER, WHITE,
        is_active=(difficulty == "HARD")
    )

    # --- Current difficulty label under buttons ---
    curr_diff = difficulty_label_font.render(
        f"Current: {difficulty}", True, SUBTITLE_COLOR
    )
    window.blit(
        curr_diff,
        (GAME_WIDTH // 2 - curr_diff.get_width() // 2,
         hard_button.y + hard_button.height + 10)
    )

    # --- Exit button ---
    draw_styled_button(
        exit_button, "EXIT",
        BTN_EXIT, BTN_EXIT_HOVER, WHITE
    )

# =====================================
# DRAW GAME (ENHANCED)
# =====================================


def draw_game():

    window.blit(background_image, (0, 0))

    rotated_bird = pygame.transform.rotate(
        bird_image,
        max(-30, min(90, -bird_velocity * 5))
    )

    window.blit(rotated_bird, bird)

    for pipe in pipes:

        if pipe["top"]:
            window.blit(top_pipe_image, pipe["rect"])

        else:
            window.blit(bottom_pipe_image, pipe["rect"])

    # --- Enhanced HUD ---

    # Score - large centered outlined text at top
    score_str = str(score)
    draw_outlined_center_text(
        window, score_str,
        hud_score_font, WHITE, HUD_SCORE_OUTLINE, 16, 3
    )

    # Best score badge - top left pill
    best_str = f"Best: {high_score}"
    best_render = hud_label_font.render(best_str, True, SCORE_GOLD)
    badge_w = best_render.get_width() + 18
    draw_rounded_rect(
        window, HUD_BADGE_BG,
        (8, 72, badge_w, 24), 12, alpha=130
    )
    window.blit(best_render, (17, 75))

    # Username badge - top right pill
    user_render = hud_label_font.render(current_user, True, WHITE)
    u_badge_w = user_render.get_width() + 18
    u_badge_x = GAME_WIDTH - u_badge_w - 8
    draw_rounded_rect(
        window, HUD_BADGE_BG,
        (u_badge_x, 12, u_badge_w, 24), 12, alpha=130
    )
    window.blit(user_render, (u_badge_x + 9, 15))

    # Difficulty badge - top right below user
    diff_render = difficulty_label_font.render(
        difficulty, True, SUBTITLE_COLOR)
    d_badge_w = diff_render.get_width() + 16
    d_badge_x = GAME_WIDTH - d_badge_w - 8
    draw_rounded_rect(
        window, HUD_BADGE_BG,
        (d_badge_x, 40, d_badge_w, 22), 11, alpha=100
    )
    window.blit(diff_render, (d_badge_x + 8, 43))

    # --- Game Over overlay ---
    if game_over:

        overlay = pygame.Surface(
            (GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((10, 10, 25, 190))
        window.blit(overlay, (0, 0))

        # --- Game Over card ---
        card_w, card_h = 320, 440
        card_x = GAME_WIDTH // 2 - card_w // 2
        card_y = 80

        # Card shadow
        draw_rounded_rect(
            window, (0, 0, 0),
            (card_x + 4, card_y + 5, card_w, card_h),
            18, alpha=100
        )
        # Card bg
        draw_rounded_rect(
            window, CARD_BG,
            (card_x, card_y, card_w, card_h),
            18, alpha=240
        )
        # Card border
        pygame.draw.rect(
            window, CARD_BORDER,
            (card_x, card_y, card_w, card_h),
            width=1, border_radius=18
        )

        # "GAME OVER" title
        draw_outlined_center_text(
            window, "GAME OVER",
            gameover_title_font, RED, (80, 0, 0), card_y + 20, 2
        )

        # Divider
        div_w = 200
        div_x = GAME_WIDTH // 2 - div_w // 2
        pygame.draw.line(
            window, CARD_BORDER,
            (div_x, card_y + 85), (div_x + div_w, card_y + 85), 1
        )

        # Score section
        sc_label = gameover_label_font.render("YOUR SCORE", True, LABEL_COLOR)
        window.blit(
            sc_label,
            (GAME_WIDTH // 2 - sc_label.get_width() // 2, card_y + 100)
        )
        sc_value = gameover_score_font.render(str(score), True, WHITE)
        window.blit(
            sc_value,
            (GAME_WIDTH // 2 - sc_value.get_width() // 2, card_y + 118)
        )

        # High score section
        hs_label = gameover_label_font.render("HIGH SCORE", True, LABEL_COLOR)
        window.blit(
            hs_label,
            (GAME_WIDTH // 2 - hs_label.get_width() // 2, card_y + 164)
        )
        hs_value = gameover_score_font.render(
            str(high_score), True, SCORE_GOLD)
        window.blit(
            hs_value,
            (GAME_WIDTH // 2 - hs_value.get_width() // 2, card_y + 182)
        )

        # New high score indicator
        if score >= high_score and score > 0:
            new_hs = msg_font.render("NEW BEST!", True, MSG_SUCCESS)
            nhw = new_hs.get_width() + 20
            draw_rounded_rect(
                window, (30, 60, 35),
                (GAME_WIDTH // 2 - nhw // 2, card_y + 222,
                 nhw, 26), 8, alpha=200
            )
            window.blit(
                new_hs,
                (GAME_WIDTH // 2 - new_hs.get_width() // 2, card_y + 225)
            )

        # Divider
        pygame.draw.line(
            window, CARD_BORDER,
            (div_x, card_y + 258), (div_x + div_w, card_y + 258), 1
        )

        # Difficulty label
        diff_sec_label = difficulty_label_font.render(
            "SELECT DIFFICULTY & RESTART", True, SUBTITLE_COLOR
        )
        window.blit(
            diff_sec_label,
            (GAME_WIDTH // 2 - diff_sec_label.get_width() // 2,
             card_y + 268)
        )

        # Repositioned buttons inside the card
        go_easy = pygame.Rect(card_x + 15, card_y + 292, 88, 38)
        go_med = pygame.Rect(card_x + 116, card_y + 292, 88, 38)
        go_hard = pygame.Rect(card_x + 217, card_y + 292, 88, 38)

        draw_styled_button(
            go_easy, "EASY",
            BTN_EASY, BTN_EASY_HOVER, WHITE,
            is_active=(difficulty == "EASY")
        )
        draw_styled_button(
            go_med, "MEDIUM",
            BTN_MEDIUM, BTN_MEDIUM_HOVER, WHITE,
            is_active=(difficulty == "MEDIUM")
        )
        draw_styled_button(
            go_hard, "HARD",
            BTN_HARD, BTN_HARD_HOVER, WHITE,
            is_active=(difficulty == "HARD")
        )

        # Update global button rects so click detection works
        easy_button.update(go_easy)
        medium_button.update(go_med)
        hard_button.update(go_hard)

        # Restart hint (pulsing)
        pulse = abs(math.sin(pygame.time.get_ticks() / 500)) * 80 + 150
        hint_surf = pygame.Surface((card_w, 24), pygame.SRCALPHA)
        hint = gameover_hint_font.render(
            "SPACE = Restart | 1/2/3 = Difficulty | ESC = Exit",
            True, SUBTITLE_COLOR
        )
        hint_surf.set_alpha(int(pulse))
        hint_surf.blit(
            hint, (card_w // 2 - hint.get_width() // 2, 0)
        )
        window.blit(hint_surf, (card_x, card_y + 340))

        # Exit button inside card
        go_exit = pygame.Rect(
            GAME_WIDTH // 2 - 60, card_y + 370, 120, 38
        )
        draw_styled_button(
            go_exit, "EXIT",
            BTN_EXIT, BTN_EXIT_HOVER, WHITE
        )
        exit_button.update(go_exit)

        # Current difficulty
        curr = difficulty_label_font.render(
            f"Difficulty: {difficulty}", True, LABEL_COLOR
        )
        window.blit(
            curr,
            (GAME_WIDTH // 2 - curr.get_width() // 2,
             card_y + card_h - 25)
        )

# =====================================
# UPDATE GAME
# =====================================


def update_game():

    global bird_y
    global bird_velocity
    global game_over
    global score
    global high_score

    bird_velocity += gravity

    bird_y += bird_velocity
    bird.y = int(bird_y)

    if bird.y < 0:
        bird.y = 0
        bird_y = 0

    if bird.y > GAME_HEIGHT:
        game_over = True

    for pipe in pipes:

        pipe["rect"].x += pipe_speed

        if (
            pipe["top"]
            and not pipe["passed"]
            and pipe["rect"].x + pipe_width < bird.x
        ):

            score += 1
            pipe["passed"] = True

        if bird.colliderect(pipe["rect"]):
            game_over = True

    pipes[:] = [
        pipe for pipe in pipes
        if pipe["rect"].x > -pipe_width
    ]

    if score > high_score:

        high_score = score

        save_high_score()


def update_text_input_rect():

    if logged_in:
        return

    field_rect = pygame.Rect(
        65, 256, 270, 42) if typing_username else pygame.Rect(65, 340, 270, 42)

    try:
        pygame.key.set_text_input_rect(field_rect)
    except Exception:
        pass


# =====================================
# MAIN LOOP
# =====================================


async def main():

    global logged_in
    global username_input
    global password_input
    global typing_username
    global bird_velocity
    global game_started
    global last_pipe_time

    while True:

        if not logged_in:
            pygame.key.start_text_input()
            update_text_input_rect()
        else:
            pygame.key.stop_text_input()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

            # LOGIN SYSTEM
            if not logged_in:

                if event.type == pygame.TEXTINPUT:
                    if typing_username:
                        username_input += event.text
                    else:
                        password_input += event.text

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_TAB:
                        typing_username = not typing_username

                    elif event.key == pygame.K_BACKSPACE:

                        if typing_username:
                            username_input = username_input[:-1]

                        else:
                            password_input = password_input[:-1]

                    elif event.key == pygame.K_RETURN:

                        if login():
                            logged_in = True

                    elif event.key == pygame.K_F2:
                        # F2 to register
                        if register():
                            logged_in = True

                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

                    else:
                        # Mobile/web fallback when TEXTINPUT is not delivered
                        if hasattr(event, 'unicode') and event.unicode and event.unicode.isprintable():
                            if typing_username:
                                username_input += event.unicode
                            else:
                                password_input += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN or (hasattr(pygame, 'FINGERDOWN') and event.type == pygame.FINGERDOWN):

                    if hasattr(pygame, 'FINGERDOWN') and event.type == pygame.FINGERDOWN:
                        mouse = (int(event.x * GAME_WIDTH), int(event.y * GAME_HEIGHT))
                    else:
                        mouse = pygame.mouse.get_pos()

                    # Click or touch to focus input fields
                    username_field_rect = pygame.Rect(65, 256, 270, 42)
                    password_field_rect = pygame.Rect(65, 340, 270, 42)

                    if username_field_rect.collidepoint(mouse):
                        typing_username = True
                    elif password_field_rect.collidepoint(mouse):
                        typing_username = False
                    elif login_button.collidepoint(mouse):

                        if login():
                            logged_in = True

                    elif register_button.collidepoint(mouse):

                        if register():
                            logged_in = True

            # GAME SYSTEM
            else:

                if event.type == pygame.KEYDOWN:

                    # ESC to exit (menu or game over only)
                    if event.key == pygame.K_ESCAPE:
                        if not game_started or game_over:
                            pygame.quit()
                            exit()

                    # 1/2/3 to select difficulty (menu or game over)
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        set_difficulty("EASY")
                        if game_over:
                            reset_game()
                        elif not game_started:
                            game_started = True
                            bird_velocity = jump_strength

                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        set_difficulty("MEDIUM")
                        if game_over:
                            reset_game()
                        elif not game_started:
                            game_started = True
                            bird_velocity = jump_strength

                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        set_difficulty("HARD")
                        if game_over:
                            reset_game()
                        elif not game_started:
                            game_started = True
                            bird_velocity = jump_strength

                    # SPACE / UP / RETURN to flap / start / restart
                    elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_RETURN):
                        if not game_started:
                            game_started = True
                        elif game_over:
                            reset_game()
                        bird_velocity = jump_strength

                if event.type == pygame.MOUSEBUTTONDOWN:

                    mouse = pygame.mouse.get_pos()

                    if (not game_started or game_over) and exit_button.collidepoint(mouse):

                        pygame.quit()
                        exit()

                    # Only check difficulty buttons on menu or game over
                    if not game_started or game_over:

                        if easy_button.collidepoint(mouse):

                            set_difficulty("EASY")

                            if game_over:
                                reset_game()
                            elif not game_started:
                                game_started = True
                                bird_velocity = jump_strength

                        elif medium_button.collidepoint(mouse):

                            set_difficulty("MEDIUM")

                            if game_over:
                                reset_game()
                            elif not game_started:
                                game_started = True
                                bird_velocity = jump_strength

                        elif hard_button.collidepoint(mouse):

                            set_difficulty("HARD")

                            if game_over:
                                reset_game()
                            elif not game_started:
                                game_started = True
                                bird_velocity = jump_strength

                        else:

                            if not game_started:
                                game_started = True

                            elif game_over:
                                reset_game()

                            bird_velocity = jump_strength

                    else:
                        # During active gameplay, any click = flap
                        bird_velocity = jump_strength

        if not logged_in:
            login_req = get_web_login_request()
            if login_req:
                username_input = login_req["username"]
                password_input = login_req["password"]

                if login_req["action"] == "login":
                    if login():
                        logged_in = True
                        hide_web_login_overlay()

                elif login_req["action"] == "register":
                    if register():
                        logged_in = True
                        hide_web_login_overlay()

            draw_login_screen()

        # MENU
        elif not game_started:

            draw_menu()

        # GAME
        else:

            now = pygame.time.get_ticks()

            if (
                now - last_pipe_time >= pipe_delay
                and not game_over
            ):

                create_pipes()

                last_pipe_time = now

            if not game_over:
                update_game()

            draw_game()

        pygame.display.update()

        clock.tick(60)

        await asyncio.sleep(0)

# =====================================
# START GAME
# =====================================
asyncio.run(main())
