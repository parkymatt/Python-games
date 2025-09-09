import pygame
import sys
import math
import random

pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter Game")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

map_names = [
    "Drifting (No Rocks)",
    "Giant Rock",
    "Random Rocks",
    "Maze Field",
    "Meteor Belt",
    "Spiral Path",
    "Broken Asteroids",
    "Alien Hive",
    "Core Collapse"
]

def load_map(map_id):
    rocks = []
    if map_id == 0:  # Drifting (No Rocks)
        pass
    elif map_id == 1:  # Giant Rock
        rocks.append({'pos': pygame.Vector2(WIDTH//2, HEIGHT//2), 'radius': 180})
    elif map_id == 2:  # Random Rocks
        for _ in range(15):
            rocks.append({'pos': pygame.Vector2(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)), 'radius': random.randint(40, 80)})
    elif map_id == 3:  # Maze Field
        for x in range(200, WIDTH, 300):
            for y in range(200, HEIGHT, 300):
                if random.random() > 0.5:
                    rocks.append({'pos': pygame.Vector2(x, y), 'radius': 60})
    elif map_id == 4:  # Meteor Belt
        for i in range(25):
            angle = i * 0.4
            x = WIDTH//2 + int(math.cos(angle) * i * 30)
            y = HEIGHT//2 + int(math.sin(angle) * i * 30)
            rocks.append({'pos': pygame.Vector2(x, y), 'radius': 50})
    elif map_id == 5:  # Spiral Path
        for _ in range(15):
            rocks.append({'pos': pygame.Vector2(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)), 'radius': 75})
    elif map_id == 6:  # Broken Asteroids
        for x in range(300, WIDTH, 500):
            rocks.append({'pos': pygame.Vector2(x, HEIGHT//2), 'radius': 100})
    elif map_id == 7:  # Alien Hive
        for _ in range(12):
            rocks.append({'pos': pygame.Vector2(WIDTH//2 + random.randint(-400, 400), HEIGHT//2 + random.randint(-300, 300)), 'radius': 120})
    elif map_id == 8:  # Core Collapse
        for _ in range(20):
            rocks.append({'pos': pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT)), 'radius': random.randint(30, 80)})
    return rocks

def map_selector_loop():
    selected = 0
    scroll_offset = 0
    visible = 6
    while True:
        screen.fill((15, 15, 15))
        title = big_font.render("Select a Map", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - 200, 50))
        for i in range(scroll_offset, min(len(map_names), scroll_offset + visible)):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            text = font.render(map_names[i], True, color)
            screen.blit(text, (WIDTH//2 - 200, 150 + (i - scroll_offset) * 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN and selected < len(map_names)-1:
                    selected += 1
                    if selected >= scroll_offset + visible: scroll_offset += 1
                elif event.key == pygame.K_UP and selected > 0:
                    selected -= 1
                    if selected < scroll_offset: scroll_offset -= 1
                elif event.key == pygame.K_RETURN:
                    return selected

def draw_rocks(rocks):
    for r in rocks:
        pygame.draw.circle(screen, (100, 100, 100), (int(r['pos'].x), int(r['pos'].y)), r['radius'])

def collides_with_rocks(pos, rocks, radius=20):
    for r in rocks:
        if pos.distance_to(r['pos']) < r['radius'] + radius:
            return True
    return False

def move_enemy(enemy, target, rocks, speed=2):
    direction = target - enemy['pos']
    if direction.length() > 0:
        direction = direction.normalize()
        new_pos = enemy['pos'] + direction * speed
        if not collides_with_rocks(new_pos, rocks, radius=30):
            enemy['pos'] = new_pos
        else:
            # Try alternate directions if blocked
            for angle_offset in [-30, 30, -60, 60, 90, -90]:
                angle = math.atan2(direction.y, direction.x) + math.radians(angle_offset)
                alt_direction = pygame.Vector2(math.cos(angle), math.sin(angle))
                new_pos = enemy['pos'] + alt_direction * speed
                if not collides_with_rocks(new_pos, rocks, radius=30):
                    enemy['pos'] = new_pos
                    break

def game_loop(map_index):
    player_img = pygame.Surface((40, 60), pygame.SRCALPHA)
    pygame.draw.polygon(player_img, (0, 200, 255), [(20, 0), (0, 60), (40, 60)])
    player_pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
    player_speed = 5
    max_health = 5
    player_health = max_health
    bullets = []
    cooldown = 400
    last_shot = 0
    score = 0

    enemies = []
    enemy_spawn_timer = 0

    rocks = load_map(map_index)

    game_paused = False
    show_upgrade_shop = False

    # Upgrade system variables
    upgrades = {
        "max_health": max_health,
        "player_speed": player_speed,
        "cooldown": cooldown,
    }
    upgrade_costs = {
        "max_health": 500,
        "player_speed": 700,
        "cooldown": 800,  # reduces cooldown
    }

    def draw_upgrade_shop():
        shop_rect = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 200, 600, 400)
        pygame.draw.rect(screen, (30, 30, 30), shop_rect)
        pygame.draw.rect(screen, (200, 200, 200), shop_rect, 3)
        title = big_font.render("Upgrade Shop (Press TAB to Close)", True, (255, 255, 255))
        screen.blit(title, (shop_rect.x + 30, shop_rect.y + 20))

        # Draw upgrades and costs
        y_off = 100
        for i, (key, cost) in enumerate(upgrade_costs.items()):
            val = upgrades[key]
            if key == "cooldown":
                display_val = f"{val//10} frames"
            elif key == "player_speed":
                display_val = f"{val}"
            else:
                display_val = f"{val}"
            text = font.render(f"{key.replace('_',' ').title()} : {display_val} - Cost: {cost} (Press {i+1})", True, (255, 255, 255))
            screen.blit(text, (shop_rect.x + 30, shop_rect.y + y_off))
            y_off += 50

    running = True
    while running:
        dt = clock.tick(60)
        screen.fill((5, 5, 15))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    show_upgrade_shop = not show_upgrade_shop
                    game_paused = show_upgrade_shop
                # Upgrade buy keys
                if show_upgrade_shop:
                    if event.key == pygame.K_1 and score >= upgrade_costs["max_health"]:
                        upgrades["max_health"] += 1
                        score -= upgrade_costs["max_health"]
                        upgrade_costs["max_health"] = int(upgrade_costs["max_health"] * 1.5)
                    elif event.key == pygame.K_2 and score >= upgrade_costs["player_speed"]:
                        upgrades["player_speed"] += 1
                        score -= upgrade_costs["player_speed"]
                        upgrade_costs["player_speed"] = int(upgrade_costs["player_speed"] * 1.5)
                    elif event.key == pygame.K_3 and score >= upgrade_costs["cooldown"]:
                        # cooldown decreases by 25 frames, minimum 100 frames
                        if upgrades["cooldown"] > 100:
                            upgrades["cooldown"] -= 25
                            score -= upgrade_costs["cooldown"]
                            upgrade_costs["cooldown"] = int(upgrade_costs["cooldown"] * 1.5)

        if game_paused:
            draw_upgrade_shop()
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()

        # Movement with WASD
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0:
            move = move.normalize() * upgrades["player_speed"]
            new_pos = player_pos + move
            if not collides_with_rocks(new_pos, rocks):
                player_pos = new_pos

        # Shooting
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - player_pos
        if direction.length() > 0:
            direction = direction.normalize()
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        rotated = pygame.transform.rotate(player_img, angle)
        draw_pos = rotated.get_rect(center=player_pos)

        if pygame.mouse.get_pressed()[0]:
            now = pygame.time.get_ticks()
            if now - last_shot >= upgrades["cooldown"]:
                bullets.append({'pos': player_pos + direction * 30, 'dir': direction})
                last_shot = now

        # Update bullets
        for b in bullets[:]:
            b['pos'] += b['dir'] * 10
            if not (0 <= b['pos'].x <= WIDTH and 0 <= b['pos'].y <= HEIGHT):
                bullets.remove(b)

        # Spawn enemies every 2 seconds
        enemy_spawn_timer += dt
        if enemy_spawn_timer >= 2000:
            enemy_spawn_timer = 0
            spawn_x = random.choice([0, WIDTH])
            spawn_y = random.randint(0, HEIGHT)
            enemies.append({'pos': pygame.Vector2(spawn_x, spawn_y), 'health': 3})

        # Move enemies and check collisions
        for e in enemies[:]:
            move_enemy(e, player_pos, rocks)
            # Check collision with player
            if e['pos'].distance_to(player_pos) < 40:
                player_health -= 1
                enemies.remove(e)
                if player_health <= 0:
                    running = False
            # Check if hit by bullet
            for b in bullets[:]:
                if b['pos'].distance_to(e['pos']) < 30:
                    e['health'] -= 1
                    bullets.remove(b)
                    if e['health'] <= 0:
                        enemies.remove(e)
                        score += 100
                    break

        # Draw rocks
        draw_rocks(rocks)

        # Draw player
        screen.blit(rotated, draw_pos)

        # Draw bullets
        for b in bullets:
            pygame.draw.circle(screen, (255, 255, 0), (int(b['pos'].x), int(b['pos'].y)), 5)

        # Draw enemies
        for e in enemies:
            pygame.draw.circle(screen, (255, 50, 50), (int(e['pos'].x), int(e['pos'].y)), 30)

        # Draw HUD
        hud = font.render(f"Health: {player_health}/{upgrades['max_health']}  Score: {score}  (Press TAB for Upgrade Shop)", True, (255, 255, 255))
        screen.blit(hud, (20, 20))

        pygame.display.flip()

    # Game Over
    game_over_screen(score)

def game_over_screen(score):
    while True:
        screen.fill((0, 0, 0))
        text1 = big_font.render("Game Over", True, (255, 0, 0))
        text2 = font.render(f"Final Score: {score}", True, (255, 255, 255))
        text3 = font.render("Press ESC to Quit", True, (255, 255, 255))

        screen.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - 100))
        screen.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2))
        screen.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

def main():
    selected_map = map_selector_loop()
    game_loop(selected_map)

if __name__ == "__main__":
    main()
