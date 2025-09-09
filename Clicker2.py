import pygame
import sys
import time

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clicker Tycoon")

# Fonts & Colors
FONT = pygame.font.SysFont("Arial", 30)
BIG_FONT = pygame.font.SysFont("Arial", 50)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (100, 100, 255)
BLACK = (0, 0, 0)

# Game state
money = 0
money_per_click = 1
money_per_sec = 0
last_income_time = time.time()

# Button areas
click_button = pygame.Rect(300, 200, 200, 200)
shop_button = pygame.Rect(325, 500, 150, 50)

# Sound
try:
    click_sound = pygame.mixer.Sound("click.wav")
except:
    click_sound = None

clock = pygame.time.Clock()

def open_shop():
    global money, money_per_click, money_per_sec

    # Create a new shop window
    shop_screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Shop")

    # Buttons inside shop
    upgrade_click_button = pygame.Rect(50, 60, 300, 50)
    upgrade_passive_button = pygame.Rect(50, 150, 300, 50)

    running_shop = True
    while running_shop:
        shop_screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_shop = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = pygame.mouse.get_pos()

                if upgrade_click_button.collidepoint(mouse):
                    if money >= 50:
                        money -= 50
                        money_per_click += 1

                if upgrade_passive_button.collidepoint(mouse):
                    if money >= 100:
                        money -= 100
                        money_per_sec += 1

        # Draw buttons
        pygame.draw.rect(shop_screen, GREEN, upgrade_click_button)
        pygame.draw.rect(shop_screen, GREEN, upgrade_passive_button)
        shop_screen.blit(FONT.render("Upgrade Click ($50)", True, BLACK), (upgrade_click_button.x + 30, upgrade_click_button.y + 10))
        shop_screen.blit(FONT.render("Upgrade Passive ($100)", True, BLACK), (upgrade_passive_button.x + 10, upgrade_passive_button.y + 10))

        pygame.display.flip()
        clock.tick(60)

    # After shop closes, restore original screen
    pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Clicker Tycoon")

# Main loop
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.mouse.get_pos()

            if click_button.collidepoint(mouse):
                money += money_per_click
                if click_sound:
                    click_sound.play()

            if shop_button.collidepoint(mouse):
                open_shop()

    # Passive income every second
    current_time = time.time()
    if current_time - last_income_time >= 1:
        money += money_per_sec
        last_income_time = current_time

    # Draw main click button
    pygame.draw.rect(screen, RED, click_button)
    screen.blit(BIG_FONT.render("CLICK", True, WHITE), (click_button.x + 40, click_button.y + 70))

    # Shop button
    pygame.draw.rect(screen, BLUE, shop_button)
    screen.blit(FONT.render("Shop", True, WHITE), (shop_button.x + 40, shop_button.y + 10))

    # Display stats
    screen.blit(FONT.render(f"Money: ${money}", True, BLACK), (20, 20))
    screen.blit(FONT.render(f"Money per Click: ${money_per_click}", True, BLACK), (20, 60))
    screen.blit(FONT.render(f"Money per Second: ${money_per_sec}", True, BLACK), (20, 100))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
