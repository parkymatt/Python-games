import pygame
import sys
import time

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clicker Game with Shop")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
LIGHT_BLUE = (100, 180, 255)
BLUE = (70, 130, 255)
BG_COLOR = (30, 30, 30)
GRAY = (50, 50, 50)
GREEN = (0, 200, 100)
DARK_GREEN = (0, 150, 75)
RED = (200, 50, 50)

# Fonts
font = pygame.font.SysFont("segoeui", 28)
small_font = pygame.font.SysFont("segoeui", 22)
big_font = pygame.font.SysFont("segoeui", 48, bold=True)

# Game variables
clicks = 0
click_power = 1
auto_clicker_power = 0

# Timing for auto clicker
last_auto_click_time = time.time()

# Button setup
button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100)
button_color = BLUE
button_hover_color = LIGHT_BLUE

# Shop variables
shop_open = False
scroll_offset = 0
shop_rect = pygame.Rect(150, 100, 500, 400)

# Mouse click position for shop clicks
shop_mouse_click_pos = None

# Define upgrades as a list of dicts
upgrades = [
    {
        "name": "+1 Click Power",
        "cost": 50,
        "description": "Increase clicks per click by 1.",
        "bought": False,
    },
    {
        "name": "Auto Clicker",
        "cost": 200,
        "description": "Automatically gain 1 click every second.",
        "bought": False,
    },
    {
        "name": "Super Click Power",
        "cost": 500,
        "description": "Increase clicks per click by 5.",
        "bought": False,
    },
    {
        "name": "Mega Auto Clicker",
        "cost": 1000,
        "description": "Auto clicker gains +5 clicks per second.",
        "bought": False,
    },
]

def render_text_with_ellipsis(text, font, max_width, color):
    text_surface = font.render(text, True, color)
    if text_surface.get_width() <= max_width:
        return text_surface

    while text and text_surface.get_width() > max_width:
        text = text[:-1]
        text_surface = font.render(text + "…", True, color)
    return text_surface

def draw_button():
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = button_rect.collidepoint(mouse_pos)
    color = button_hover_color if is_hovered else button_color

    pygame.draw.rect(screen, color, button_rect, border_radius=20)
    text_surf = big_font.render("CLICK", True, WHITE)
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)

def draw_clicks():
    click_text = font.render(f"Clicks: {clicks}", True, WHITE)
    screen.blit(click_text, (WIDTH - click_text.get_width() - 20, 20))

def draw_click_power():
    power_text = font.render(f"Click Power: {click_power}", True, WHITE)
    screen.blit(power_text, (20, 20))

def draw_auto_click_power():
    auto_text = font.render(f"Auto Click Power: {auto_clicker_power}", True, WHITE)
    screen.blit(auto_text, (20, 50))

def draw_shop(mouse_click_pos):
    global clicks, click_power, auto_clicker_power, scroll_offset

    pygame.draw.rect(screen, GRAY, shop_rect, border_radius=15)
    title = big_font.render("Shop", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, shop_rect.y + 20))

    scroll_area = pygame.Rect(shop_rect.x + 20, shop_rect.y + 80, shop_rect.width - 40, shop_rect.height - 100)
    pygame.draw.rect(screen, (40, 40, 40), scroll_area, border_radius=10)

    max_text_width = scroll_area.width - 150

    upgrade_height = 90
    padding = 10

    total_height = len(upgrades) * (upgrade_height + padding)
    max_scroll = max(0, total_height - scroll_area.height)

    if scroll_offset < 0:
        scroll_offset = 0
    elif scroll_offset > max_scroll:
        scroll_offset = max_scroll

    mouse_pos = pygame.mouse.get_pos()

    # Set clipping to restrict drawing inside scroll area
    old_clip = screen.get_clip()
    screen.set_clip(scroll_area)

    for i, upg in enumerate(upgrades):
        y = scroll_area.y + i * (upgrade_height + padding) - scroll_offset
        button_rect = pygame.Rect(scroll_area.x, y, scroll_area.width, upgrade_height)

        if button_rect.bottom < scroll_area.y or button_rect.top > scroll_area.bottom:
            continue

        hovered = button_rect.collidepoint(mouse_pos)
        if upg["bought"]:
            color = DARK_GREEN
        elif hovered:
            color = GREEN
        else:
            color = (0, 170, 60)

        pygame.draw.rect(screen, color, button_rect, border_radius=12)

        name_text = render_text_with_ellipsis(upg["name"], font, max_text_width, WHITE)
        cost_text = font.render(f"Cost: {upg['cost']}", True, WHITE)
        desc_text = render_text_with_ellipsis(upg["description"], small_font, max_text_width, WHITE)

        screen.blit(name_text, (button_rect.x + 10, button_rect.y + 10))
        screen.blit(cost_text, (button_rect.right - cost_text.get_width() - 10, button_rect.y + 10))
        screen.blit(desc_text, (button_rect.x + 10, button_rect.y + 40))

        if mouse_click_pos and button_rect.collidepoint(mouse_click_pos) and not upg["bought"] and clicks >= upg["cost"]:
            clicks -= upg["cost"]
            upg["bought"] = True
            if upg["name"] == "+1 Click Power":
                click_power += 1
            elif upg["name"] == "Auto Clicker":
                auto_clicker_power += 1
            elif upg["name"] == "Super Click Power":
                click_power += 5
            elif upg["name"] == "Mega Auto Clicker":
                auto_clicker_power += 5

    # Restore previous clipping
    screen.set_clip(old_clip)

def handle_scroll(event):
    global scroll_offset
    if shop_open:
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if shop_rect.collidepoint(mouse_pos):
                scroll_offset -= event.y * 30

# Game loop
running = True
while running:
    screen.fill(BG_COLOR)
    mouse_pos = pygame.mouse.get_pos()
    shop_mouse_click_pos = None  # reset each frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                shop_open = not shop_open

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if shop_open:
                if shop_rect.collidepoint(event.pos):
                    shop_mouse_click_pos = event.pos
            else:
                if button_rect.collidepoint(event.pos):
                    clicks += click_power

        handle_scroll(event)

    current_time = time.time()
    if auto_clicker_power > 0 and current_time - last_auto_click_time >= 1:
        clicks += auto_clicker_power
        last_auto_click_time = current_time

    if shop_open:
        draw_shop(shop_mouse_click_pos)
    else:
        draw_button()

    draw_clicks()
    draw_click_power()
    draw_auto_click_power()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
