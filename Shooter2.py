import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Shooter Game with Shop and Mouse Aim")

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Player
player_size = 50
player_speed = 7
player_health = 100
player_rect = pygame.Rect(WIDTH//2, HEIGHT//2, player_size, player_size)

# Bullet
bullet_speed = 15
bullets = []

# Enemy
enemy_size = 50
enemy_speed = 3
enemies = [pygame.Rect(random.randint(0, WIDTH-50), random.randint(0, HEIGHT-50), enemy_size, enemy_size) for _ in range(5)]

# Coins
coin_size = 30
coins = [pygame.Rect(random.randint(0, WIDTH-coin_size), random.randint(0, HEIGHT-coin_size), coin_size, coin_size) for _ in range(5)]
score = 0

# Font
font = pygame.font.SysFont(None, 50)

# Shop variables
shop_open = False
shop_items = [
    {"name": "Increase Speed", "cost": 50, "effect": "speed"},
    {"name": "Heal 50 HP", "cost": 30, "effect": "heal"},
    {"name": "Extra Bullet Slot", "cost": 70, "effect": "bullet"}
]
bullet_limit = 10

# Helper function to shoot bullet toward cursor
def shoot_bullet():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player_rect.centerx
    dy = mouse_y - player_rect.centery
    angle = math.atan2(dy, dx)
    velocity_x = math.cos(angle) * bullet_speed
    velocity_y = math.sin(angle) * bullet_speed
    bullets.append({"rect": pygame.Rect(player_rect.centerx-5, player_rect.centery-5, 10, 10),
                    "vel": (velocity_x, velocity_y)})

# Main game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if shop_open:
                if event.key == pygame.K_1:
                    item = shop_items[0]
                    if score >= item["cost"]:
                        score -= item["cost"]
                        player_speed += 2
                if event.key == pygame.K_2:
                    item = shop_items[1]
                    if score >= item["cost"]:
                        score -= item["cost"]
                        player_health += 50
                        if player_health > 100:
                            player_health = 100
                if event.key == pygame.K_3:
                    item = shop_items[2]
                    if score >= item["cost"]:
                        score -= item["cost"]
                        bullet_limit += 5
            if event.key == pygame.K_p:
                shop_open = not shop_open
        if event.type == pygame.MOUSEBUTTONDOWN and not shop_open:
            if event.button == 1:  # Left click
                if len(bullets) < bullet_limit:
                    shoot_bullet()

    if not shop_open:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player_rect.top > 0:
            player_rect.y -= player_speed
        if keys[pygame.K_s] and player_rect.bottom < HEIGHT:
            player_rect.y += player_speed
        if keys[pygame.K_a] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_d] and player_rect.right < WIDTH:
            player_rect.x += player_speed

        # Move bullets
        for b in bullets[:]:
            b["rect"].x += b["vel"][0]
            b["rect"].y += b["vel"][1]
            if b["rect"].bottom < 0 or b["rect"].top > HEIGHT or b["rect"].right < 0 or b["rect"].left > WIDTH:
                bullets.remove(b)

        # Move enemies toward player
        for enemy in enemies:
            if enemy.x < player_rect.x:
                enemy.x += enemy_speed
            elif enemy.x > player_rect.x:
                enemy.x -= enemy_speed
            if enemy.y < player_rect.y:
                enemy.y += enemy_speed
            elif enemy.y > player_rect.y:
                enemy.y -= enemy_speed

        # Bullet collision with enemies
        for b in bullets[:]:
            for enemy in enemies[:]:
                if b["rect"].colliderect(enemy):
                    bullets.remove(b)
                    enemies.remove(enemy)
                    enemies.append(pygame.Rect(random.randint(0, WIDTH-50), random.randint(0, HEIGHT-50), enemy_size, enemy_size))
                    break

        # Enemy collision with player
        for enemy in enemies:
            if enemy.colliderect(player_rect):
                player_health -= 1

        # Coin collection
        for coin in coins[:]:
            if coin.colliderect(player_rect):
                score += 10
                coins.remove(coin)
                coins.append(pygame.Rect(random.randint(0, WIDTH-coin_size), random.randint(0, HEIGHT-coin_size), coin_size, coin_size))

        # Draw enemies
        for enemy in enemies:
            pygame.draw.rect(screen, RED, enemy)

        # Draw coins
        for coin in coins:
            pygame.draw.circle(screen, GOLD, coin.center, coin_size//2)

        # Draw bullets
        for b in bullets:
            pygame.draw.rect(screen, YELLOW, b["rect"])

        # Draw player rotated toward mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - player_rect.centerx, mouse_y - player_rect.centery
        angle = math.degrees(math.atan2(-rel_y, rel_x))
        player_surf = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
        pygame.draw.polygon(player_surf, BLUE, [(0,0),(player_size,player_size//2),(0,player_size)])
        rotated_player = pygame.transform.rotate(player_surf, angle)
        rot_rect = rotated_player.get_rect(center=player_rect.center)
        screen.blit(rotated_player, rot_rect.topleft)

        # Draw UI
        health_text = font.render(f"Health: {player_health}", True, WHITE)
        score_text = font.render(f"Score: {score}", True, WHITE)
        shop_hint = font.render("Press P to open Shop", True, GREEN)
        screen.blit(health_text, (10, 10))
        screen.blit(score_text, (10, 60))
        screen.blit(shop_hint, (WIDTH-400, 10))

    else:
        # Draw Shop
        shop_bg = pygame.Surface((WIDTH, HEIGHT))
        shop_bg.set_alpha(200)
        shop_bg.fill(BLACK)
        screen.blit(shop_bg, (0, 0))
        shop_title = font.render("SHOP - Press 1/2/3 to Buy, P to Close", True, WHITE)
        screen.blit(shop_title, (WIDTH//2 - shop_title.get_width()//2, 50))
        for idx, item in enumerate(shop_items):
            item_text = font.render(f"{idx+1}. {item['name']} - Cost: {item['cost']}", True, WHITE)
            screen.blit(item_text, (WIDTH//2 - 200, 150 + idx*60))

    pygame.display.flip()

    # Check for game over
    if player_health <= 0:
        running = False

# Game Over screen
screen.fill(BLACK)
game_over_text = font.render("GAME OVER", True, WHITE)
final_score_text = font.render(f"Final Score: {score}", True, WHITE)
screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 + 10))
pygame.display.flip()
pygame.time.wait(5000)

pygame.quit()
sys.exit()
