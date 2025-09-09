import pygame
import sys
import time

pygame.init()

# Set up screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clicker Tycoon")

# Fonts and colors
FONT = pygame.font.SysFont("Arial", 30)
BIG_FONT = pygame.font.SysFont("Arial", 50)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLACK = (0, 0, 0)

# Game state
money = 0
money_per_click = 1
money_per_sec = 0
last_income_time = time.time()

# Button areas
click_button = pygame.Rect(300, 200, 200, 200)
upgrade_click_button = pygame.Rect(50, 450, 300, 50)
upgrade_passive_button = pygame.Rect(450, 450, 300, 50)

# Try to load sound
try:
    click_sound = pygame.mixer.Sound("click.wav")
except:
    click_sound = None

clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    screen.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.mouse.get_pos()

            # Click main button
            if click_button.collidepoint(mouse):
                money += money_per_click
                if click_sound:
                    click_sound.play()

            # Upgrade Click
            if upgrade_click_button.collidepoint(mouse):
                if money >= 50:
                    money -= 50
                    money_per_click += 1

            # Upgrade Passive
            if upgrade_passive_button.collidepoint(mouse):
                if money >= 100:
                    money -= 100
                    money_per_sec += 1

    # Passive income
    current_time = time.time()
    if current_time - last_income_time >= 1:
        money += money_per_sec
        last_income_time = current_time

    # Draw click button
    pygame.draw.rect(screen, RED, click_button)
    screen.blit(BIG_FONT.render("CLICK", True, WHITE), (click_button.x + 40, click_button.y + 70))

    # Upgrade buttons
    pygame.draw.rect(screen, GREEN, upgrade_click_button)
    pygame.draw.rect(screen, GREEN, upgrade_passive_button)
    screen.blit(FONT.render("Upgrade Click ($50)", True, BLACK), (upgrade_click_button.x + 20, upgrade_click_button.y + 10))
    screen.blit(FONT.render("Upgrade Passive ($100)", True, BLACK), (upgrade_passive_button.x + 20, upgrade_passive_button.y + 10))

    # Display stats
    screen.blit(FONT.render(f"Money: ${money}", True, BLACK), (20, 20))
    screen.blit(FONT.render(f"Money per Click: ${money_per_click}", True, BLACK), (20, 60))
    screen.blit(FONT.render(f"Money per Second: ${money_per_sec}", True, BLACK), (20, 100))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()