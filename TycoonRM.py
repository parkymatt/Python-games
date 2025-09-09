import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tycoon Game with Workers")
font = pygame.font.SysFont(None, 32)
large_font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
BACKGROUND = (100, 150, 200)

# States
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_SHOP = 'shop'

TAB_BUSINESS = 'business'
TAB_WORKER = 'worker'

state = STATE_MENU
tab = TAB_BUSINESS

# Money and entities
money = 100
workers = 0
worker_cost = 50
managers = 0
manager_cost = 500

auto_timer = 0
auto_interval = 1500  # ms

# Businesses list
businesses = []
titles = [
    'Tech Startup','Coffee Shop','Bookstore','Bakery','Fitness Gym','Art Gallery',
    'Clothing Boutique','Music Store','Electronics Shop','Toy Store','Pet Store',
    'Flower Shop','Car Dealership','Movie Theater','Restaurant','Ice Cream Parlor',
    'Hotel','Night Club','Book Publisher','Advertising Agency'
]
for i, name in enumerate(titles, 1):
    businesses.append({'name': name, 'cost': 1000 * i, 'income': 10 * i, 'owned': 0, 'rect': None})

# Buttons
btn_start = pygame.Rect(860, 480, 200, 60)
btn_open_shop = pygame.Rect(20, 80, 250, 60)
btn_tab_business = pygame.Rect(20, 80, 250, 60)
btn_tab_worker = pygame.Rect(300, 80, 250, 60)
btn_close_shop = pygame.Rect(20, 20, 180, 50)
btn_collect_income = pygame.Rect(20, 160, 250, 60)

scroll = 0
max_scroll = 0

# Helpers
def draw_text_center(rect, text, color, font_obj=font):
    surf = font_obj.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=rect.center))

def button(rect, text, active=True):
    pygame.draw.rect(screen, GREEN if active else GRAY, rect, border_radius=6)
    draw_text_center(rect, text, BLACK)

# Screens
def screen_menu():
    screen.fill(BACKGROUND)
    txt = large_font.render('Tycoon Game with Workers', True, BLUE)
    screen.blit(txt, txt.get_rect(center=(WIDTH // 2, 300)))
    button(btn_start, 'Start Game')
    pygame.display.flip()

def screen_play():
    screen.fill(BACKGROUND)
    button(btn_open_shop, 'Open Shop')
    button(btn_collect_income, 'Collect Income')
    mon = font.render(f'Money: ${money}', True, BLACK)
    screen.blit(mon, (20, 20))
    pygame.display.flip()

def screen_shop():
    global scroll, max_scroll
    screen.fill(BACKGROUND)
    # Tabs
    is_business = (tab == TAB_BUSINESS)
    is_worker = (tab == TAB_WORKER)
    button(btn_tab_business, 'Businesses', is_business)
    button(btn_tab_worker, 'Workers', is_worker)
    button(btn_close_shop, 'Close Shop')

    y0 = 160 + scroll
    spacing = 50 if tab == TAB_BUSINESS else 90

    if tab == TAB_BUSINESS:
        items = businesses
    else:
        items = [
            {'name': 'Worker', 'cost': worker_cost, 'info': '+5 income/click', 'owned': workers, 'rect': None},
            {'name': 'Manager', 'cost': manager_cost, 'info': 'Auto-buy biz', 'owned': managers, 'rect': None}
        ]

    total_height = len(items) * spacing
    max_scroll = min(0, HEIGHT - 200 - total_height)

    for i, item in enumerate(items):
        y = y0 + i * spacing
        if -spacing < y < HEIGHT:
            screen.blit(font.render(item['name'], True, BLACK), (50, y))
            screen.blit(font.render(f"Cost: ${item['cost']}", True, BLACK), (300, y))
            screen.blit(font.render(item['info'], True, BLACK), (550, y))
            screen.blit(font.render(f"Owned: {item['owned']}", True, BLACK), (800, y))
            r = pygame.Rect(950, y, 120, 40)
            item['rect'] = r
            button(r, 'Buy', money >= item['cost'])

    pygame.display.flip()

def auto_buy(dt):
    global auto_timer, money
    auto_timer += dt
    if auto_timer >= auto_interval and managers > 0:
        auto_timer = 0
        for b in reversed(businesses):
            if money >= b['cost']:
                money -= b['cost']
                b['owned'] += 1
                b['cost'] = int(b['cost'] * 1.15)
                break

# Main loop
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == STATE_MENU and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_start.collidepoint(event.pos):
                state = STATE_PLAYING

        elif state == STATE_PLAYING and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_open_shop.collidepoint(event.pos):
                state = STATE_SHOP
                tab = TAB_BUSINESS
                scroll = 0
            elif btn_collect_income.collidepoint(event.pos):
                total_income = sum(b['income'] * b['owned'] for b in businesses) + workers * 5
                money += total_income

        elif state == STATE_SHOP and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_close_shop.collidepoint(event.pos):
                state = STATE_PLAYING
            elif btn_tab_business.collidepoint(event.pos):
                tab = TAB_BUSINESS
                scroll = 0
            elif btn_tab_worker.collidepoint(event.pos):
                tab = TAB_WORKER
                scroll = 0
            else:
                y0 = 160 + scroll
                spacing = 50 if tab == TAB_BUSINESS else 90
                if tab == TAB_BUSINESS:
                    for b in businesses:
                        if b.get('rect') and b['rect'].collidepoint(event.pos) and money >= b['cost']:
                            money -= b['cost']
                            b['owned'] += 1
                            b['cost'] = int(b['cost'] * 1.15)
                else:
                    worker_rect = pygame.Rect(950, y0, 120, 40)
                    manager_rect = pygame.Rect(950, y0 + spacing, 120, 40)
                    if worker_rect.collidepoint(event.pos) and money >= worker_cost:
                        money -= worker_cost
                        workers += 1
                    elif manager_rect.collidepoint(event.pos) and money >= manager_cost:
                        money -= manager_cost
                        managers += 1

        elif state == STATE_SHOP and event.type == pygame.MOUSEWHEEL:
            scroll += event.y * 30
            scroll = min(0, scroll)
            scroll = max(max_scroll, scroll)

    if state == STATE_PLAYING:
        auto_buy(dt)

    if state == STATE_MENU:
        screen_menu()
    elif state == STATE_PLAYING:
        screen_play()
    elif state == STATE_SHOP:
        screen_shop()

pygame.quit()
sys.exit()
