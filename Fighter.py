import random
import time
import os
import sys

# Terminal colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text, delay=0.03):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

# Fighter classes with base stats
CLASSES = {
    "Warrior": {"max_hp": 120, "base_atk": 14, "defense": 6, "speed": 5},
    "Mage": {"max_hp": 90, "base_atk": 18, "defense": 3, "speed": 7},
    "Rogue": {"max_hp": 100, "base_atk": 12, "defense": 4, "speed": 10},
    "Tank": {"max_hp": 150, "base_atk": 10, "defense": 10, "speed": 3},
}

def choose_class():
    slow_print("Choose a class:")
    for i, cls in enumerate(CLASSES.keys(), 1):
        slow_print(f" {i}) {cls}")
    while True:
        choice = input(f"Class [1-{len(CLASSES)}]: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(CLASSES):
                class_name = list(CLASSES.keys())[choice - 1]
                slow_print(f"You chose {class_name}!")
                return class_name
        slow_print("Invalid choice.")

class Weapon:
    def __init__(self, name, atk_bonus, price):
        self.name = name
        self.atk_bonus = atk_bonus
        self.price = price
    def __str__(self):
        return f"{self.name} (+{self.atk_bonus} ATK) - ${self.price}"

class Fighter:
    def __init__(self, name, class_name="Warrior", level=1, is_ai=False):
        stats = CLASSES[class_name]
        self.class_name = class_name
        self.name = name
        self.level = level
        self.max_hp = stats["max_hp"]
        self.hp = self.max_hp
        self.base_atk = stats["base_atk"]
        self.defense = stats["defense"]
        self.speed = stats["speed"]
        self.is_ai = is_ai
        self.weapon = None
        self.inventory = {}  # e.g., {"Potion": 1}
        self.statuses = {}  # e.g., {"stunned": 1}
        self.cooldowns = {"heavy": 0, "special": 0}
        self.meter = 0
        self.alive = True

    @property
    def atk(self):
        weapon_bonus = self.weapon.atk_bonus if self.weapon else 0
        return self.base_atk + weapon_bonus

    def is_alive(self):
        return self.alive and self.hp > 0

    def __str__(self):
        weapon = self.weapon.name if self.weapon else "None"
        status = "Alive" if self.is_alive() else "Defeated"
        return (f"{self.name} ({self.class_name}) Lv{self.level} HP:{self.hp}/{self.max_hp} "
                f"ATK:{self.atk} DEF:{self.defense} SPD:{self.speed} Weapon:{weapon} Status:{status}")

    def tick_cooldowns(self):
        for cd in self.cooldowns:
            if self.cooldowns[cd] > 0:
                self.cooldowns[cd] -= 1

    def tick_statuses(self):
        to_remove = []
        for status in self.statuses:
            self.statuses[status] -= 1
            if self.statuses[status] <= 0:
                to_remove.append(status)
        for status in to_remove:
            del self.statuses[status]

    def can_act(self):
        return "stunned" not in self.statuses and self.is_alive()

    def take_damage(self, dmg):
        dmg_after_def = max(0, dmg - self.defense)
        # Blocking halves damage
        if "blocking" in self.statuses:
            dmg_after_def = dmg_after_def // 2
        # Dodging gives 50% chance to avoid damage
        if "dodging" in self.statuses:
            if random.random() < 0.5:
                slow_print(f"{self.name} dodged the attack!")
                dmg_after_def = 0
        self.hp -= dmg_after_def
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return dmg_after_def

    def heal(self, amount):
        if not self.is_alive():
            return False
        self.hp = min(self.max_hp, self.hp + amount)
        return True

def print_health_bar(fighter, bar_length=30):
    hp_ratio = fighter.hp / fighter.max_hp if fighter.max_hp else 0
    fill_length = int(bar_length * hp_ratio)
    bar = "[" + "#" * fill_length + "-" * (bar_length - fill_length) + "]"
    hp_text = f"{fighter.hp}/{fighter.max_hp}"
    print(f"{fighter.name:15} {bar} {hp_text}")

def team_alive(team):
    return any(f.is_alive() for f in team)

def ai_choose_action(fighter):
    if fighter.meter >= 10 and fighter.cooldowns["special"] == 0:
        return "special"
    if fighter.cooldowns["heavy"] == 0:
        return random.choice(["attack", "heavy"])
    return "attack"

def perform_action(attacker, target, action):
    if not attacker.is_alive():
        return
    if action == "attack":
        dmg = attacker.atk
        damage_done = target.take_damage(dmg)
        slow_print(f"{attacker.name} attacks {target.name} for {damage_done} damage!")
        attacker.meter = min(10, attacker.meter + 1)
    elif action == "heavy":
        dmg = int(attacker.atk * 1.7)
        damage_done = target.take_damage(dmg)
        slow_print(f"{attacker.name} uses Heavy Attack on {target.name} for {damage_done} damage!")
        attacker.cooldowns["heavy"] = 3
        attacker.meter = min(10, attacker.meter + 2)
    elif action == "special":
        dmg = int(attacker.atk * 3)
        damage_done = target.take_damage(dmg)
        slow_print(f"{attacker.name} unleashes Special Attack on {target.name} for {damage_done} damage!")
        attacker.cooldowns["special"] = 5
        attacker.meter = 0
    elif action == "heal":
        if attacker.inventory.get("Potion", 0) > 0:
            healed = attacker.heal(30)
            if healed:
                attacker.inventory["Potion"] -= 1
                slow_print(f"{attacker.name} uses a Potion and heals 30 HP!")
            else:
                slow_print(f"{attacker.name} is already at full HP.")
        else:
            slow_print(f"{attacker.name} has no Potions to heal.")
    elif action == "block":
        slow_print(f"{attacker.name} is blocking this turn (reduces damage taken).")
        attacker.statuses["blocking"] = 1
    elif action == "dodge":
        slow_print(f"{attacker.name} attempts to dodge the next attack.")
        attacker.statuses["dodging"] = 1
    elif action == "stunned":
        slow_print(f"{attacker.name} is stunned and skips the turn!")
    else:
        slow_print(f"{attacker.name} does nothing.")

def battle(player_team, enemy_team):
    round_num = 1
    while team_alive(player_team) and team_alive(enemy_team):
        clear()
        slow_print(f"{CYAN}--- Round {round_num} ---{RESET}")
        slow_print("Player Team:")
        for f in player_team:
            print_health_bar(f)
        slow_print("\nEnemy Team:")
        for f in enemy_team:
            print_health_bar(f)
        slow_print("")

        # Determine turn order based on speed, both teams combined
        combatants = [f for f in player_team + enemy_team if f.is_alive()]
        combatants.sort(key=lambda x: x.speed, reverse=True)

        for f in combatants:
            if not f.is_alive():
                continue
            f.tick_cooldowns()
            f.tick_statuses()
            if not f.can_act():
                perform_action(f, None, "stunned")
                continue
            if f in player_team:
                # Player chooses action
                slow_print(f"Your turn: {f.name} ({f.class_name}) Meter: {f.meter} HeavyCD:{f.cooldowns['heavy']} SpCD:{f.cooldowns['special']}")
                slow_print("Actions: 1) Attack  2) Heavy Attack  3) Special Attack  4) Heal (Potion)  5) Block  6) Dodge")
                action_choice = input("Choose action (1-6): ").strip()
                actions_map = {"1":"attack","2":"heavy","3":"special","4":"heal","5":"block","6":"dodge"}
                if action_choice not in actions_map:
                    slow_print("Invalid action, skipping turn.")
                    continue
                action = actions_map[action_choice]
                # Select target if needed
                target = None
                if action in ("attack","heavy","special"):
                    alive_enemies = [e for e in enemy_team if e.is_alive()]
                    if not alive_enemies:
                        continue
                    slow_print("Choose a target:")
                    for i, enemy in enumerate(alive_enemies,1):
                        slow_print(f"{i}) {enemy.name} ({enemy.class_name}) HP:{enemy.hp}/{enemy.max_hp}")
                    while True:
                        t_choice = input(f"Target (1-{len(alive_enemies)}): ").strip()
                        if t_choice.isdigit():
                            t_choice = int(t_choice)
                            if 1 <= t_choice <= len(alive_enemies):
                                target = alive_enemies[t_choice-1]
                                break
                        slow_print("Invalid target.")
                perform_action(f, target, action)
            else:
                # AI turn
                alive_opponents = [p for p in player_team if p.is_alive()]
                if not alive_opponents:
                    break
                target = random.choice(alive_opponents)
                action = ai_choose_action(f)
                perform_action(f, target, action)

            if not team_alive(enemy_team) or not team_alive(player_team):
                break

        round_num += 1

    if team_alive(player_team):
        slow_print(f"{GREEN}Victory! You won the battle!{RESET}")
        reward = random.randint(20, 50) * len(enemy_team)
        slow_print(f"You earn ${reward}.")
        game_state['money'] += reward
        return True
    else:
        slow_print(f"{RED}Your team was defeated... Game Over.{RESET}")
        return False

def show_team(team):
    slow_print("Your team status:")
    for f in team:
        weapon = f.weapon.name if f.weapon else "None"
        slow_print(f"  {f.name} ({f.class_name}) Lv{f.level} HP:{f.hp}/{f.max_hp} ATK:{f.atk} DEF:{f.defense} SPD:{f.speed} Weapon: {weapon}")

def hire_teammate():
    cost = 50 + (10 * len(game_state['player_team']))
    slow_print(f"Hiring a new teammate costs ${cost}. You have ${game_state['money']}.")
    if game_state['money'] < cost:
        slow_print("Not enough money to hire a teammate.")
        return
    name = input("Enter new teammate's name: ").strip()
    if not name:
        slow_print("Hiring cancelled.")
        return
    class_name = choose_class()
    new_fighter = Fighter(name, class_name=class_name, level=1, is_ai=True)
    game_state['player_team'].append(new_fighter)
    game_state['money'] -= cost
    slow_print(f"{name} the {class_name} has joined your team!")

def equip_weapon(fighter, weapons):
    slow_print(f"Available weapons to equip for {fighter.name}:")
    for i, w in enumerate(weapons, 1):
        slow_print(f"{i}) {w}")
    slow_print(f"{len(weapons)+1}) Cancel")
    while True:
        choice = input(f"Choose weapon (1-{len(weapons)+1}): ").strip()
        if choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(weapons):
                fighter.weapon = weapons[choice-1]
                slow_print(f"{fighter.name} equipped {fighter.weapon.name}!")
                return weapons[choice-1].price
            elif choice == len(weapons)+1:
                slow_print("Cancelled weapon equip.")
                return 0
        slow_print("Invalid choice.")

def shop():
    potions_price = 15
    weapons = game_state['weapon_store']
    while True:
        slow_print(f"\nWelcome to the Shop! You have ${game_state['money']}")
        slow_print("1) Buy Potion ($15 each)")
        slow_print("2) Buy Weapon for your fighters")
        slow_print("3) Exit Shop")
        choice = input("Choice: ").strip()
        if choice == "1":
            amt = input("How many potions to buy? ").strip()
            if amt.isdigit() and int(amt) > 0:
                cost = int(amt) * potions_price
                if cost > game_state['money']:
                    slow_print("Not enough money.")
                else:
                    game_state['money'] -= cost
                    for f in game_state['player_team']:
                        f.inventory["Potion"] = f.inventory.get("Potion", 0) + int(amt)
                    slow_print(f"Bought {amt} potions for your entire team!")
            else:
                slow_print("Invalid amount.")
        elif choice == "2":
            slow_print("Choose fighter to equip weapon:")
            for i, f in enumerate(game_state['player_team'], 1):
                slow_print(f"{i}) {f.name} ({f.class_name})")
            while True:
                f_choice = input(f"Choose fighter (1-{len(game_state['player_team'])}): ").strip()
                if f_choice.isdigit():
                    f_choice = int(f_choice)
                    if 1 <= f_choice <= len(game_state['player_team']):
                        fighter = game_state['player_team'][f_choice-1]
                        spent = equip_weapon(fighter, weapons)
                        if spent > 0:
                            if game_state['money'] >= spent:
                                game_state['money'] -= spent
                            else:
                                slow_print("Not enough money to buy weapon.")
                                fighter.weapon = None
                        break
                slow_print("Invalid choice.")
        elif choice == "3":
            slow_print("Leaving shop.")
            break
        else:
            slow_print("Invalid choice.")

def admin_panel():
    code = input("Enter admin code: ").strip()
    if code != "2013":
        slow_print("Incorrect admin code!")
        return
    while True:
        slow_print(f"{MAGENTA}--- Admin Panel ---{RESET}")
        slow_print("Options:")
        slow_print("1) View all fighters")
        slow_print("2) Edit a fighter")
        slow_print("3) Manage money")
        slow_print("4) Manage potions")
        slow_print("5) Spawn new fighter")
        slow_print("6) Exit Admin Panel")
        choice = input("Choose: ").strip()

        if choice == "1":
            slow_print("=== Player Team ===")
            for f in game_state['player_team']:
                status = "Alive" if f.is_alive() else "Defeated"
                weapon = f.weapon.name if f.weapon else "None"
                slow_print(f"{f.name} ({f.class_name}) Lv{f.level} HP:{f.hp}/{f.max_hp} ATK:{f.atk} DEF:{f.defense} SPD:{f.speed} Weapon:{weapon} Status:{status}")

        elif choice == "2":
            slow_print("Choose fighter to edit:")
            for i, f in enumerate(game_state['player_team'], 1):
                slow_print(f" {i}) {f.name} ({f.class_name})")
            idx = input("Number: ").strip()
            if not idx.isdigit() or not (1 <= int(idx) <= len(game_state['player_team'])):
                slow_print("Invalid choice.")
                continue
            fighter = game_state['player_team'][int(idx)-1]
            slow_print(f"Editing {fighter.name}:")
            slow_print("1) Heal to full HP")
            slow_print("2) Revive fighter")
            slow_print("3) Change HP manually")
            slow_print("4) Change ATK")
            slow_print("5) Change DEF")
            slow_print("6) Change SPD")
            slow_print("7) Equip/change weapon")
            sub_choice = input("Choose option: ").strip()
            if sub_choice == "1":
                fighter.hp = fighter.max_hp
                fighter.alive = True
                slow_print(f"{fighter.name} healed to full HP.")
            elif sub_choice == "2":
                if not fighter.is_alive():
                    fighter.alive = True
                    fighter.hp = fighter.max_hp // 2
                    slow_print(f"{fighter.name} revived at half HP.")
                else:
                    slow_print(f"{fighter.name} is already alive.")
            elif sub_choice == "3":
                val = input("Set HP to: ").strip()
                if val.isdigit():
                    val = int(val)
                    fighter.hp = max(0, min(val, fighter.max_hp))
                    if fighter.hp == 0:
                        fighter.alive = False
                    else:
                        fighter.alive = True
                    slow_print(f"{fighter.name}'s HP set to {fighter.hp}.")
                else:
                    slow_print("Invalid input.")
            elif sub_choice == "4":
                val = input("Set ATK to: ").strip()
                if val.isdigit():
                    fighter.base_atk = int(val)
                    slow_print(f"{fighter.name}'s ATK set to {fighter.base_atk}.")
                else:
                    slow_print("Invalid input.")
            elif sub_choice == "5":
                val = input("Set DEF to: ").strip()
                if val.isdigit():
                    fighter.defense = int(val)
                    slow_print(f"{fighter.name}'s DEF set to {fighter.defense}.")
                else:
                    slow_print("Invalid input.")
            elif sub_choice == "6":
                val = input("Set SPD to: ").strip()
                if val.isdigit():
                    fighter.speed = int(val)
                    slow_print(f"{fighter.name}'s SPD set to {fighter.speed}.")
                else:
                    slow_print("Invalid input.")
            elif sub_choice == "7":
                slow_print("Available weapons:")
                weapons = game_state['weapon_store']
                for i, w in enumerate(weapons,1):
                    slow_print(f" {i}) {w}")
                slow_print(f" {len(weapons)+1}) Remove weapon")
                w_choice = input("Choose weapon: ").strip()
                if w_choice.isdigit():
                    w_choice = int(w_choice)
                    if 1 <= w_choice <= len(weapons):
                        fighter.weapon = weapons[w_choice-1]
                        slow_print(f"{fighter.name} equipped {fighter.weapon.name}.")
                    elif w_choice == len(weapons)+1:
                        fighter.weapon = None
                        slow_print(f"{fighter.name}'s weapon removed.")
                    else:
                        slow_print("Invalid choice.")
                else:
                    slow_print("Invalid input.")

        elif choice == "3":
            slow_print(f"Current money: ${game_state['money']}")
            slow_print("1) Add money")
            slow_print("2) Subtract money")
            sub_choice = input("Choose: ").strip()
            if sub_choice == "1":
                amt = input("Enter amount to add: ").strip()
                if amt.isdigit():
                    game_state['money'] += int(amt)
                    slow_print(f"Added ${amt}. New balance: ${game_state['money']}")
                else:
                    slow_print("Invalid amount.")
            elif sub_choice == "2":
                amt = input("Enter amount to subtract: ").strip()
                if amt.isdigit():
                    val = int(amt)
                    if val > game_state['money']:
                        slow_print("Cannot subtract more than you have.")
                    else:
                        game_state['money'] -= val
                        slow_print(f"Subtracted ${amt}. New balance: ${game_state['money']}")
                else:
                    slow_print("Invalid amount.")
            else:
                slow_print("Invalid choice.")

        elif choice == "4":
            slow_print("Manage Potions for your fighters:")
            for i, f in enumerate(game_state['player_team'],1):
                potions = f.inventory.get("Potion",0)
                slow_print(f" {i}) {f.name} - Potions: {potions}")
            f_choice = input("Choose fighter to add/remove potions: ").strip()
            if f_choice.isdigit() and 1 <= int(f_choice) <= len(game_state['player_team']):
                fighter = game_state['player_team'][int(f_choice)-1]
                slow_print(f"1) Add potions\n2) Remove potions")
                action = input("Choose action: ").strip()
                amt = input("Amount: ").strip()
                if amt.isdigit():
                    amt = int(amt)
                    if action == "1":
                        fighter.inventory["Potion"] = fighter.inventory.get("Potion",0) + amt
                        slow_print(f"Added {amt} potions to {fighter.name}.")
                    elif action == "2":
                        current = fighter.inventory.get("Potion",0)
                        if amt > current:
                            slow_print(f"{fighter.name} only has {current} potions.")
                        else:
                            fighter.inventory["Potion"] = current - amt
                            slow_print(f"Removed {amt} potions from {fighter.name}.")
                    else:
                        slow_print("Invalid action.")
                else:
                    slow_print("Invalid amount.")
            else:
                slow_print("Invalid fighter choice.")

        elif choice == "5":
            slow_print("Spawn new fighter")
            name = input("Enter fighter name: ").strip()
            if not name:
                slow_print("Cancelled.")
                continue
            class_name = choose_class()
            new_fighter = Fighter(name, class_name=class_name, level=1, is_ai=True)
            game_state['player_team'].append(new_fighter)
            slow_print(f"{name} the {class_name} spawned and added to your team!")

        elif choice == "6":
            slow_print("Exiting Admin Panel.")
            break
        else:
            slow_print("Invalid choice.")

def generate_enemy(level=1):
    class_name = random.choice(list(CLASSES.keys()))
    name = random.choice(["Goblin", "Orc", "Bandit", "Thief", "Warlock", "Brute"])
    enemy = Fighter(f"{name} Lv{level}", class_name=class_name, level=level, is_ai=True)
    # scale stats with level
    enemy.max_hp += (level-1) * 10
    enemy.hp = enemy.max_hp
    enemy.base_atk += (level-1) * 3
    enemy.defense += (level-1) * 2
    enemy.speed += (level-1)
    return enemy

def main_menu():
    while True:
        slow_print(f"\n{CYAN}--- Main Menu ---{RESET}")
        slow_print("1) View Team")
        slow_print("2) Hire Teammate")
        slow_print("3) Visit Shop")
        slow_print("4) Battle")
        slow_print("5) Admin Panel")
        slow_print("6) Exit Game")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            show_team(game_state['player_team'])
        elif choice == "2":
            hire_teammate()
        elif choice == "3":
            shop()
        elif choice == "4":
            level = game_state.get("current_level", 1)
            slow_print(f"Starting battle at level {level}!")
            enemies = [generate_enemy(level) for _ in range(level)]
            result = battle(game_state['player_team'], enemies)
            if result:
                game_state["current_level"] = level + 1
        elif choice == "5":
            admin_panel()
        elif choice == "6":
            slow_print("Thanks for playing!")
            sys.exit()
        else:
            slow_print("Invalid choice.")

# Initial game state
game_state = {
    "player_team": [],
    "money": 100,
    "current_level": 1,
    "weapon_store": [
        Weapon("Sword", 5, 40),
        Weapon("Axe", 7, 60),
        Weapon("Staff", 6, 50),
        Weapon("Dagger", 4, 30),
        Weapon("Hammer", 8, 70),
    ]
}

def setup():
    clear()
    slow_print("Welcome to the Text Fighting Game!")
    slow_print(f"You start with ${game_state['money']} and one fighter.")
    name = input("Enter your fighter's name: ").strip()
    if not name:
        name = "Hero"
    class_name = choose_class()
    starter = Fighter(name, class_name=class_name)
    game_state['player_team'].append(starter)
    slow_print(f"Good luck, {name} the {class_name}!")
    slow_print("Press Enter to continue...")
    input()

if __name__ == "__main__":
    setup()
    while True:
        main_menu()
