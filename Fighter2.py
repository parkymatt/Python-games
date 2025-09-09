import pygame
import sys
import random

pygame.init()

# Screen settings
WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turn-Based Fighting Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (0, 180, 0)
RED = (180, 0, 0)
BLUE = (0, 0, 180)
YELLOW = (255, 255, 0)

FONT = pygame.font.SysFont("arial", 20)
BIG_FONT = pygame.font.SysFont("arial", 30)

# --- Game data ---

CLASSES = {
    "Warrior": {"max_hp": 120, "atk": 15, "defense": 10, "speed": 8, "hp_inc": 20, "atk_inc": 3, "def_inc": 2, "spd_inc": 1},
    "Archer": {"max_hp": 90, "atk": 20, "defense": 5, "speed": 12, "hp_inc": 15, "atk_inc": 4, "def_inc": 1, "spd_inc": 2},
    "Mage": {"max_hp": 80, "atk": 25, "defense": 3, "speed": 10, "hp_inc": 10, "atk_inc": 5, "def_inc": 1, "spd_inc": 1},
}

WEAPONS = [
    {"name": "Iron Sword", "atk": 5, "price": 30},
    {"name": "Long Bow", "atk": 7, "price": 40},
    {"name": "Magic Staff", "atk": 10, "price": 60},
]

# --- Classes ---

class Fighter:
    def __init__(self, name, class_name, is_ai=False):
        self.name = name
        self.class_name = class_name
        self.is_ai = is_ai
        base = CLASSES[class_name]
        self.max_hp = base["max_hp"]
        self.hp = self.max_hp
        self.base_atk = base["atk"]
        self.defense = base["defense"]
        self.speed = base["speed"]
        self.level = 1
        self.weapon = None
        self.cooldowns = {"heavy": 0, "special": 0}

    def is_alive(self):
        return self.hp > 0

    def attack_value(self):
        wpn_atk = self.weapon["atk"] if self.weapon else 0
        return self.base_atk + wpn_atk

    def take_damage(self, amount):
        damage = max(0, amount - self.defense)
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        return damage

    def reset_cooldowns(self):
        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] -= 1

class Button:
    def __init__(self, rect, text, color=GRAY, hover_color=BLUE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.hover_color if self.hovered else self.color, self.rect, border_radius=6)
        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

# --- Game State ---

class GameState:
    def __init__(self):
        self.player_team = []
        self.enemy_team = []
        self.money = 100
        self.level = 1
        self.phase = "menu"
        self.selected_fighter = None
        self.selected_action = None
        self.turn_order = []
        self.current_turn_index = 0
        self.messages = []
        self.admin_mode = False
        self.admin_input = ""

    def add_message(self, text):
        self.messages.append(text)
        if len(self.messages) > 6:
            self.messages.pop(0)

game_state = GameState()

# Attack animation variables
attack_anim_timer = 0
attack_anim_duration = 30
attack_anim_active = False
attacker_name = ""
defender_name = ""
damage_done = 0

# --- UI Buttons ---

buttons = []

def create_menu_buttons():
    buttons.clear()
    buttons.append(Button((50, 100, 220, 45), "View Team"))
    buttons.append(Button((50, 170, 220, 45), "Hire Teammate ($50)"))
    buttons.append(Button((50, 240, 220, 45), "Shop"))
    buttons.append(Button((50, 310, 220, 45), "Battle"))
    buttons.append(Button((50, 380, 220, 45), "Admin Panel"))
    buttons.append(Button((50, 450, 220, 45), "Exit Game"))

def create_team_buttons():
    buttons.clear()
    y = 100
    for f in game_state.player_team:
        buttons.append(Button((50, y, 320, 45), f"{f.name} - Lv {f.level} HP:{f.hp}/{f.max_hp}"))
        y += 60
    buttons.append(Button((50, y, 220, 45), "Back"))

def create_shop_buttons():
    buttons.clear()
    y = 100
    for wpn in WEAPONS:
        buttons.append(Button((50, y, 350, 45), f"Buy {wpn['name']} (${wpn['price']}) ATK+{wpn['atk']}"))
        y += 60
    buttons.append(Button((50, y, 220, 45), "Back"))

def create_upgrade_buttons():
    buttons.clear()
    y = 100
    for f in game_state.player_team:
        cost = f.level * 75
        buttons.append(Button((50, y, 400, 45), f"Upgrade {f.name} to Lv {f.level+1} (Cost: ${cost})"))
        y += 60
    buttons.append(Button((50, y, 220, 45), "Back"))

def create_battle_buttons():
    buttons.clear()
    f = game_state.selected_fighter
    if not f:
        return
    buttons.append(Button((50, HEIGHT - 140, 160, 50), f"Light Attack"))
    heavy_text = f"Heavy Attack (CD:{f.cooldowns['heavy']})" if f.cooldowns['heavy'] > 0 else "Heavy Attack"
    buttons.append(Button((230, HEIGHT - 140, 160, 50), heavy_text))
    special_text = f"Special Attack (CD:{f.cooldowns['special']})" if f.cooldowns['special'] > 0 else "Special Attack"
    buttons.append(Button((410, HEIGHT - 140, 160, 50), special_text))
    buttons.append(Button((590, HEIGHT - 140, 160, 50), "Pass"))
    buttons.append(Button((WIDTH - 120, 20, 110, 40), "Main Menu"))

def create_admin_buttons():
    buttons.clear()
    buttons.append(Button((50, 100, 220, 45), "Add $100"))
    y = 170
    for f in game_state.player_team:
        buttons.append(Button((50, y, 320, 45), f"Heal {f.name} Fully"))
        y += 60
    buttons.append(Button((50, y, 220, 45), "Back"))

# --- Drawing functions ---

def draw_text_lines(surface, lines, start_x, start_y, line_height=26, color=BLACK):
    y = start_y
    for line in lines:
        text_surf = FONT.render(line, True, color)
        surface.blit(text_surf, (start_x, y))
        y += line_height

def draw_menu():
    SCREEN.fill(WHITE)
    create_menu_buttons()
    for btn in buttons:
        btn.draw(SCREEN)
    draw_text_lines(SCREEN, [f"Money: ${game_state.money}", f"Level: {game_state.level}"], 50, 40)

def draw_team():
    SCREEN.fill(WHITE)
    create_team_buttons()
    for btn in buttons:
        btn.draw(SCREEN)

def draw_shop():
    SCREEN.fill(WHITE)
    create_shop_buttons()
    for btn in buttons:
        btn.draw(SCREEN)
    draw_text_lines(SCREEN, [f"Money: ${game_state.money}"], 50, 50)

def draw_upgrade():
    SCREEN.fill(WHITE)
    create_upgrade_buttons()
    for btn in buttons:
        btn.draw(SCREEN)
    draw_text_lines(SCREEN, [f"Money: ${game_state.money}"], 50, 50)

def draw_battle():
    global attack_anim_timer, attack_anim_active

    SCREEN.fill(WHITE)
    # Draw player team
    x = 50
    y = HEIGHT - 250
    for f in game_state.player_team:
        color = GREEN if f.is_alive() else RED
        hp_ratio = f.hp / f.max_hp if f.max_hp > 0 else 0
        hp_bar_length = int(150 * hp_ratio)
        # HP bar background
        pygame.draw.rect(SCREEN, GRAY, (x, y - 25, 150, 20), border_radius=6)
        # HP bar fill (flashes red if in attack anim)
        bar_color = RED
        if attack_anim_active and defender_name == f.name:
            if attack_anim_timer % 10 < 5:
                bar_color = YELLOW
        pygame.draw.rect(SCREEN, bar_color, (x, y - 25, hp_bar_length, 20), border_radius=6)

        # Name and level
        name_text = FONT.render(f"{f.name} (Lv {f.level})", True, BLACK)
        SCREEN.blit(name_text, (x, y - 60))

        # Weapon info
        weapon_text = FONT.render(f"Weapon: {f.weapon['name'] if f.weapon else 'None'}", True, BLACK)
        SCREEN.blit(weapon_text, (x, y - 5))

        # Cooldowns
        cd_text = FONT.render(f"Heavy CD: {f.cooldowns['heavy']}  SpCD: {f.cooldowns['special']}", True, BLACK)
        SCREEN.blit(cd_text, (x, y + 20))

        x += 180

    # Draw enemy team
    x = 50
    y = 100
    for e in game_state.enemy_team:
        color = RED if e.is_alive() else GRAY
        hp_ratio = e.hp / e.max_hp if e.max_hp > 0 else 0
        hp_bar_length = int(150 * hp_ratio)

        pygame.draw.rect(SCREEN, GRAY, (x, y - 25, 150, 20), border_radius=6)
        bar_color = GREEN
        if attack_anim_active and defender_name == e.name:
            if attack_anim_timer % 10 < 5:
                bar_color = YELLOW
        pygame.draw.rect(SCREEN, bar_color, (x, y - 25, hp_bar_length, 20), border_radius=6)

        name_text = FONT.render(f"{e.name} (Lv {e.level})", True, BLACK)
        SCREEN.blit(name_text, (x, y - 60))

        weapon_text = FONT.render(f"Weapon: {e.weapon['name'] if e.weapon else 'None'}", True, BLACK)
        SCREEN.blit(weapon_text, (x, y - 5))

        cd_text = FONT.render(f"Heavy CD: {e.cooldowns['heavy']}  SpCD: {e.cooldowns['special']}", True, BLACK)
        SCREEN.blit(cd_text, (x, y + 20))

        x += 180

    # Show turn text
    if game_state.selected_fighter:
        turn_text = BIG_FONT.render(f"Turn: {game_state.selected_fighter.name}", True, BLUE)
        SCREEN.blit(turn_text, (WIDTH // 2 - turn_text.get_width() // 2, 20))

    # Draw battle buttons
    create_battle_buttons()
    for btn in buttons:
        btn.draw(SCREEN)

    # Draw messages
    draw_text_lines(SCREEN, game_state.messages, 50, HEIGHT // 2 + 40, color=BLACK)

    # Draw attack animation damage text
    if attack_anim_active:
        dmg_text = BIG_FONT.render(f"{attacker_name} hit {defender_name} for {damage_done} damage!", True, RED)
        SCREEN.blit(dmg_text, (WIDTH // 2 - dmg_text.get_width() // 2, HEIGHT // 2 - 50))

def draw_admin_login():
    SCREEN.fill(WHITE)
    prompt = BIG_FONT.render("Enter Admin Code:", True, BLACK)
    SCREEN.blit(prompt, (50, 150))
    input_text = BIG_FONT.render(game_state.admin_input, True, BLACK)
    SCREEN.blit(input_text, (50, 220))

def draw_admin_panel():
    SCREEN.fill(WHITE)
    create_admin_buttons()
    for btn in buttons:
        btn.draw(SCREEN)
    draw_text_lines(SCREEN, [f"Money: ${game_state.money}"], 50, 50)

# --- Game logic ---

def start_battle():
    game_state.phase = "battle"
    game_state.enemy_team.clear()
    # Create enemies scaled to level
    for i in range(3):
        cls = random.choice(list(CLASSES.keys()))
        enemy = Fighter(f"Enemy{i+1}", cls, is_ai=True)
        # Scale enemy stats by level
        base = CLASSES[cls]
        enemy.max_hp = base["max_hp"] + (game_state.level - 1) * base["hp_inc"]
        enemy.hp = enemy.max_hp
        enemy.base_atk = base["atk"] + (game_state.level - 1) * base["atk_inc"]
        enemy.defense = base["defense"] + (game_state.level - 1) * base["def_inc"]
        enemy.speed = base["speed"] + (game_state.level - 1) * base["spd_inc"]
        enemy.level = game_state.level
        game_state.enemy_team.append(enemy)
    # Setup turn order
    game_state.turn_order = sorted(game_state.player_team + game_state.enemy_team, key=lambda f: f.speed, reverse=True)
    game_state.current_turn_index = 0
    game_state.selected_fighter = game_state.turn_order[game_state.current_turn_index]
    game_state.messages.clear()
    game_state.add_message("Battle started!")

def next_turn():
    game_state.current_turn_index = (game_state.current_turn_index + 1) % len(game_state.turn_order)
    # Skip dead fighters
    while not game_state.turn_order[game_state.current_turn_index].is_alive():
        game_state.current_turn_index = (game_state.current_turn_index + 1) % len(game_state.turn_order)
    game_state.selected_fighter = game_state.turn_order[game_state.current_turn_index]
    game_state.selected_fighter.reset_cooldowns()

def ai_choose_action(fighter):
    # AI prefers special if available, else heavy if available, else light
    if fighter.cooldowns["special"] == 0:
        return "special"
    elif fighter.cooldowns["heavy"] == 0:
        return "heavy"
    else:
        return "light"

def ai_choose_target(target_list):
    alive_targets = [t for t in target_list if t.is_alive()]
    if alive_targets:
        return random.choice(alive_targets)
    return None

def apply_attack(attacker, defender, attack_type):
    global attack_anim_active, attack_anim_timer, attacker_name, defender_name, damage_done
    base_dmg = attacker.attack_value()
    if attack_type == "light":
        dmg = base_dmg
        attacker.cooldowns["heavy"] = max(0, attacker.cooldowns["heavy"] - 1)
        attacker.cooldowns["special"] = max(0, attacker.cooldowns["special"] - 1)
    elif attack_type == "heavy" and attacker.cooldowns["heavy"] == 0:
        dmg = int(base_dmg * 1.5)
        attacker.cooldowns["heavy"] = 3  # cooldown 3 turns
    elif attack_type == "special" and attacker.cooldowns["special"] == 0:
        dmg = int(base_dmg * 2)
        attacker.cooldowns["special"] = 5  # cooldown 5 turns
    else:
        dmg = base_dmg  # fallback to light if cooldown active

    damage = defender.take_damage(dmg)
    attacker_name = attacker.name
    defender_name = defender.name
    damage_done = damage
    start_attack_animation(attacker, defender, damage)
    game_state.add_message(f"{attacker.name} used {attack_type} attack on {defender.name} for {damage} damage!")

def check_battle_over():
    if all(not f.is_alive() for f in game_state.enemy_team):
        game_state.add_message("You won the battle!")
        game_state.money += game_state.level * 100
        game_state.level += 1
        game_state.phase = "menu"
        game_state.selected_fighter = None
        game_state.selected_action = None
        return True
    elif all(not f.is_alive() for f in game_state.player_team):
        game_state.add_message("Your team has been defeated! Game over.")
        game_state.phase = "menu"
        game_state.selected_fighter = None
        game_state.selected_action = None
        return True
    return False

def hire_teammate():
    if game_state.money < 50:
        game_state.add_message("Not enough money to hire!")
        return
    cls = random.choice(list(CLASSES.keys()))
    name = f"Ally{len(game_state.player_team)+1}"
    new_fighter = Fighter(name, cls)
    game_state.player_team.append(new_fighter)
    game_state.money -= 50
    game_state.add_message(f"Hired new teammate {name} ({cls})!")

def buy_weapon(index):
    if index >= len(WEAPONS):
        return
    wpn = WEAPONS[index]
    if game_state.money < wpn["price"]:
        game_state.add_message("Not enough money to buy weapon!")
        return
    if not game_state.selected_fighter:
        game_state.add_message("Select a fighter first!")
        return
    game_state.selected_fighter.weapon = wpn
    game_state.money -= wpn["price"]
    game_state.add_message(f"{game_state.selected_fighter.name} equipped {wpn['name']}!")

def upgrade_fighter(index):
    if index >= len(game_state.player_team):
        return
    f = game_state.player_team[index]
    cost = f.level * 75
    if game_state.money < cost:
        game_state.add_message("Not enough money to upgrade!")
        return
    base = CLASSES[f.class_name]
    f.max_hp += base["hp_inc"]
    f.hp = f.max_hp
    f.base_atk += base["atk_inc"]
    f.defense += base["def_inc"]
    f.speed += base["spd_inc"]
    f.level += 1
    game_state.money -= cost
    game_state.add_message(f"{f.name} upgraded to level {f.level}!")

# --- Event handlers ---

def handle_menu_click(pos):
    for btn in buttons:
        if btn.is_hovered(pos):
            if btn.text == "View Team":
                game_state.phase = "team"
                create_team_buttons()
            elif btn.text == "Hire Teammate ($50)":
                hire_teammate()
            elif btn.text == "Shop":
                if not game_state.player_team:
                    game_state.add_message("Hire teammates first!")
                    return
                game_state.phase = "shop"
                create_shop_buttons()
            elif btn.text == "Battle":
                if not game_state.player_team:
                    game_state.add_message("Hire teammates first!")
                    return
                start_battle()
            elif btn.text == "Admin Panel":
                game_state.phase = "admin_login"
                game_state.admin_input = ""
            elif btn.text == "Exit Game":
                pygame.quit()
                sys.exit()

def handle_team_click(pos):
    for btn in buttons:
        if btn.is_hovered(pos):
            if btn.text == "Back":
                game_state.phase = "menu"
                create_menu_buttons()
                return
            else:
                # Select fighter to equip weapons
                for idx, f in enumerate(game_state.player_team):
                    if btn.text.startswith(f.name):
                        game_state.selected_fighter = f
                        game_state.phase = "upgrade"
                        create_upgrade_buttons()
                        return

def handle_shop_click(pos):
    for idx, btn in enumerate(buttons):
        if btn.is_hovered(pos):
            if btn.text == "Back":
                game_state.phase = "menu"
                create_menu_buttons()
                game_state.selected_fighter = None
                return
            else:
                buy_weapon(idx)
                return

def handle_upgrade_click(pos):
    for idx, btn in enumerate(buttons):
        if btn.is_hovered(pos):
            if btn.text == "Back":
                game_state.phase = "team"
                create_team_buttons()
                game_state.selected_fighter = None
                return
            else:
                for i, f in enumerate(game_state.player_team):
                    if btn.text.startswith(f"Upgrade {f.name}"):
                        upgrade_fighter(i)
                        return

def handle_battle_click(pos):
    global attack_anim_active
    if attack_anim_active:
        # Ignore clicks during animation
        return
    for idx, btn in enumerate(buttons):
        if btn.is_hovered(pos):
            if btn.text == "Main Menu":
                game_state.phase = "menu"
                create_menu_buttons()
                game_state.selected_fighter = None
                return
            if game_state.selected_fighter.is_ai:
                return  # AI acts automatically

            target_team = game_state.enemy_team if game_state.selected_fighter in game_state.player_team else game_state.player_team
            alive_targets = [f for f in target_team if f.is_alive()]
            if not alive_targets:
                return

            target = alive_targets[0]  # For simplicity, attack first alive enemy

            action = None
            if btn.text.startswith("Light"):
                action = "light"
            elif btn.text.startswith("Heavy") and game_state.selected_fighter.cooldowns["heavy"] == 0:
                action = "heavy"
            elif btn.text.startswith("Special") and game_state.selected_fighter.cooldowns["special"] == 0:
                action = "special"
            elif btn.text == "Pass":
                game_state.add_message(f"{game_state.selected_fighter.name} passed the turn.")
                next_turn()
                if check_battle_over():
                    return
                if game_state.selected_fighter.is_ai:
                    ai_take_turn()
                return

            if action:
                apply_attack(game_state.selected_fighter, target, action)
                if check_battle_over():
                    return
                # Wait for animation, then next turn
                pygame.time.set_timer(pygame.USEREVENT + 1, 700)

def handle_admin_login_click(event):
    if event.key == pygame.K_BACKSPACE:
        game_state.admin_input = game_state.admin_input[:-1]
    elif event.key == pygame.K_RETURN:
        if game_state.admin_input == "2013":
            game_state.phase = "admin_panel"
            create_admin_buttons()
            game_state.admin_input = ""
        else:
            game_state.admin_input = ""
            game_state.phase = "menu"
            create_menu_buttons()
            game_state.add_message("Incorrect admin code.")
    else:
        if len(game_state.admin_input) < 10:
            game_state.admin_input += event.unicode

def handle_admin_panel_click(pos):
    for btn in buttons:
        if btn.is_hovered(pos):
            if btn.text == "Add $100":
                game_state.money += 100
                game_state.add_message("Added $100.")
                return
            elif btn.text == "Back":
                game_state.phase = "menu"
                create_menu_buttons()
                return
            else:
                for f in game_state.player_team:
                    if btn.text == f"Heal {f.name} Fully":
                        f.hp = f.max_hp
                        game_state.add_message(f"Healed {f.name}!")
                        return

def ai_take_turn():
    fighter = game_state.selected_fighter
    if not fighter.is_alive():
        next_turn()
        return
    action = ai_choose_action(fighter)
    target_team = game_state.enemy_team if fighter in game_state.player_team else game_state.player_team
    target = ai_choose_target(target_team)
    if target:
        apply_attack(fighter, target, action)
    if check_battle_over():
        return
    # Wait for animation then next turn
    pygame.time.set_timer(pygame.USEREVENT + 1, 700)

# --- Main game loop ---

def main():
    create_menu_buttons()
    global attack_anim_active, attack_anim_timer
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state.phase == "menu":
                    handle_menu_click(mouse_pos)
                elif game_state.phase == "team":
                    handle_team_click(mouse_pos)
                elif game_state.phase == "shop":
                    handle_shop_click(mouse_pos)
                elif game_state.phase == "upgrade":
                    handle_upgrade_click(mouse_pos)
                elif game_state.phase == "battle":
                    handle_battle_click(mouse_pos)
                elif game_state.phase == "admin_panel":
                    handle_admin_panel_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if game_state.phase == "admin_login":
                    handle_admin_login_click(event)
            elif event.type == pygame.USEREVENT + 1:  # Animation end event
                attack_anim_active = False
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                next_turn()
                if game_state.selected_fighter.is_ai and game_state.phase == "battle":
                    ai_take_turn()

        # Update button hover state
        for btn in buttons:
            btn.hovered = btn.is_hovered(mouse_pos)

        # Draw current phase
        if game_state.phase == "menu":
            draw_menu()
        elif game_state.phase == "team":
            draw_team()
        elif game_state.phase == "shop":
            draw_shop()
        elif game_state.phase == "upgrade":
            draw_upgrade()
        elif game_state.phase == "battle":
            draw_battle()
        elif game_state.phase == "admin_login":
            draw_admin_login()
        elif game_state.phase == "admin_panel":
            draw_admin_panel()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Start with a default fighter
    starter = Fighter("Larry", "Warrior")
    game_state.player_team.append(starter)
    main()
