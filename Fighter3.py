import random

# === Character class with stats, status effects, and combat methods ===

class Character:
    def __init__(self, name, max_hp, damage, crit_chance=5, dodge_chance=5, role="none", special=None):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.damage = damage
        self.crit_chance = crit_chance
        self.dodge_chance = dodge_chance
        self.role = role
        self.special = special
        self.level = 1
        self.xp = 0
        self.status_effects = {}  # e.g., {"burn": 3 turns left}

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        if random.randint(1, 100) <= self.dodge_chance:
            print(f"⚡ {self.name} dodged the attack!")
            return False
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0
        return True

    def attack(self, target):
        crit = random.randint(1, 100) <= self.crit_chance
        dmg = self.damage * 2 if crit else self.damage
        hit_success = target.take_damage(dmg)
        if hit_success:
            print(f"{self.name} hits {target.name} for {dmg} damage{' (CRIT!)' if crit else ''}!")
        return hit_success

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
        print(f"{self.name} heals for {amount} HP. ({self.hp}/{self.max_hp})")

    def add_status(self, effect, turns):
        self.status_effects[effect] = turns
        print(f"{self.name} is affected by {effect} for {turns} turns!")

    def process_status_effects(self):
        remove = []
        for effect in self.status_effects:
            if effect == "burn":
                burn_dmg = max(1, self.max_hp // 20)
                self.hp -= burn_dmg
                print(f"🔥 {self.name} takes {burn_dmg} burn damage! ({self.hp}/{self.max_hp})")
                if self.hp <= 0:
                    print(f"💀 {self.name} has succumbed to burn!")
            self.status_effects[effect] -= 1
            if self.status_effects[effect] <= 0:
                remove.append(effect)
        for effect in remove:
            del self.status_effects[effect]
            print(f"{self.name} is no longer affected by {effect}.")

# === Global variables ===
player = Character("Hero", 120, 12, crit_chance=15, dodge_chance=10)
squad = []
wave = 1
player_coins = 50

# === Recruitable squad types ===
recruitable_types = {
    "Warrior": {"max_hp": 60, "damage": 8, "crit_chance": 5, "dodge_chance": 5, "role": "tank"},
    "Archer": {"max_hp": 40, "damage": 10, "crit_chance": 20, "dodge_chance": 10, "role": "dps"},
    "Mage": {"max_hp": 35, "damage": 7, "crit_chance": 10, "dodge_chance": 5, "role": "aoe", "special": "fireball"},
    "Healer": {"max_hp": 30, "damage": 3, "crit_chance": 5, "dodge_chance": 15, "role": "support", "special": "heal"},
}

# === Enemy templates ===
enemy_types = [
    {"name": "Goblin", "max_hp": 25, "damage": 6},
    {"name": "Orc", "max_hp": 40, "damage": 9},
    {"name": "Skeleton Archer", "max_hp": 30, "damage": 8},
    {"name": "Dark Mage", "max_hp": 35, "damage": 7, "special": "drain"},
    {"name": "Troll", "max_hp": 60, "damage": 14},
]

# === Boss templates ===
boss_types = [
    {"name": "Dragon", "max_hp": 180, "damage": 22, "special": "firebreath"},
    {"name": "Demon Lord", "max_hp": 220, "damage": 20, "special": "curse"},
]

# === Utility Functions ===

def print_status():
    print("\n====== STATUS ======")
    print(f"Wave: {wave}")
    print(f"Coins: {player_coins}")
    print(f"Player: {player.name} HP: {player.hp}/{player.max_hp}")
    print("Squad Members:")
    if not squad:
        print("  None")
    else:
        for i, member in enumerate(squad, 1):
            print(f"  {i}. {member.name} (Lvl {member.level}) HP: {member.hp}/{member.max_hp} DMG: {member.damage}")

def input_choice(prompt, choices):
    choice = input(prompt).strip()
    while choice not in choices:
        print(f"Invalid choice. Choose from {choices}.")
        choice = input(prompt).strip()
    return choice

# === Recruiting and Upgrading ===

def recruit_member():
    global player_coins
    print("\n--- Recruit Squad Members ---")
    for i, (name, stats) in enumerate(recruitable_types.items(), 1):
        print(f"{i}. {name} (HP: {stats['max_hp']}, DMG: {stats['damage']}, Role: {stats['role']}) - Cost: 30 coins")
    print("5. Cancel")
    choice = input_choice("> ", ["1","2","3","4","5"])
    if choice == "5":
        return
    if player_coins < 30:
        print("Not enough coins to recruit!")
        return
    recruit_name = list(recruitable_types.keys())[int(choice)-1]
    stats = recruitable_types[recruit_name]
    new_member = Character(recruit_name, stats["max_hp"], stats["damage"],
                           crit_chance=stats.get("crit_chance", 5),
                           dodge_chance=stats.get("dodge_chance", 5),
                           role=stats.get("role", "none"),
                           special=stats.get("special", None))
    squad.append(new_member)
    player_coins -= 30
    print(f"Recruited new squad member: {recruit_name}!")

def upgrade_member():
    global player_coins
    if not squad:
        print("No squad members to upgrade.")
        return
    print("\n--- Upgrade Squad Members ---")
    for i, member in enumerate(squad, 1):
        print(f"{i}. {member.name} (Lvl {member.level}) DMG: {member.damage} HP: {member.max_hp} - Upgrade cost: 20 coins")
    print("0. Cancel")
    choices = [str(x) for x in range(len(squad)+1)]
    choice = input_choice("> ", choices)
    if choice == "0":
        return
    idx = int(choice)-1
    if player_coins < 20:
        print("Not enough coins to upgrade!")
        return
    member = squad[idx]
    member.damage += 3
    member.max_hp += 7
    member.hp = member.max_hp
    member.level += 1
    player_coins -= 20
    print(f"Upgraded {member.name} to level {member.level}!")

def heal_player():
    global player_coins, player
    if player_coins < 15:
        print("Not enough coins to heal!")
        return
    player.hp = player.max_hp
    player_coins -= 15
    print("Player fully healed!")

# === Enemy and Boss Creation ===

def create_enemies(current_wave):
    enemies = []
    if current_wave % 15 == 0:
        boss_template = random.choice(boss_types)
        hp = boss_template["max_hp"] + current_wave * 20
        dmg = boss_template["damage"] + current_wave * 3
        boss = Character(boss_template["name"], hp, dmg, special=boss_template.get("special"))
        enemies.append(boss)
        print(f"\n👑 BOSS WAVE! A {boss.name} appears with {boss.hp} HP and {boss.damage} DMG!")
    else:
        for _ in range(random.randint(1, 3)):
            enemy_template = random.choice(enemy_types)
            hp = enemy_template["max_hp"] + current_wave * 5
            dmg = enemy_template["damage"] + current_wave * 1
            enemy = Character(enemy_template["name"], hp, dmg, special=enemy_template.get("special"))
            enemies.append(enemy)
        print(f"\nWave {current_wave} enemies approach!")
    return enemies

# === Combat Mechanics ===

def squad_attack(squad, enemies):
    for member in squad:
        if not member.is_alive():
            continue
        if member.special == "fireball":
            # AoE damage
            dmg = member.damage
            print(f"{member.name} casts Fireball, hitting all enemies for {dmg} damage!")
            for enemy in enemies:
                enemy.take_damage(dmg)
        elif member.special == "heal":
            # Heal weakest ally
            if squad:
                weakest = min(squad, key=lambda x: x.hp if x.is_alive() else 9999)
                if weakest.is_alive():
                    heal_amount = 8 + member.level
                    weakest.heal(heal_amount)
                    print(f"{member.name} heals {weakest.name} for {heal_amount} HP!")
        else:
            # Normal attack random enemy
            living_enemies = [e for e in enemies if e.is_alive()]
            if not living_enemies:
                return
            target = random.choice(living_enemies)
            member.attack(target)

def player_attack(player, enemies):
    if not player.is_alive():
        return
    living_enemies = [e for e in enemies if e.is_alive()]
    if not living_enemies:
        return
    target = random.choice(living_enemies)
    player.attack(target)

def enemies_attack(enemies, player, squad):
    for enemy in enemies:
        if not enemy.is_alive():
            continue
        # Enemy special attacks
        if enemy.special == "firebreath":
            # AoE damage to squad + player
            print(f"🔥 {enemy.name} uses Firebreath!")
            targets = squad + [player]
            for t in targets:
                if t.is_alive():
                    t.take_damage(12 + enemy.level*2)
                    print(f"{t.name} takes firebreath damage!")
        elif enemy.special == "curse":
            # Curse random squad member reducing damage temporarily
            if squad:
                target = random.choice([m for m in squad if m.is_alive()])
                if "cursed" not in target.status_effects:
                    target.add_status("cursed", 3)
                    original_dmg = target.damage
                    target.damage = max(1, target.damage // 2)
                    print(f"💀 {enemy.name} curses {target.name}! Damage halved for 3 turns!")
        else:
            # Normal attack on random target prioritizing tank role
            targets = [m for m in squad if m.is_alive()]
            if player.is_alive():
                targets.append(player)
            if not targets:
                return
            tank_targets = [t for t in targets if getattr(t, "role", "") == "tank" and t.is_alive()]
            if tank_targets:
                target = random.choice(tank_targets)
            else:
                target = random.choice(targets)
            enemy.attack(target)

def process_statuses(characters):
    for c in characters:
        if c.is_alive():
            c.process_status_effects()
            # Remove curse after duration ends
            if "cursed" in c.status_effects and c.status_effects["cursed"] == 0:
                c.damage *= 2  # Restore damage

# === Main Battle Loop ===

def battle(wave_num):
    enemies = create_enemies(wave_num)
    turn = 1

    while any(e.is_alive() for e in enemies) and (player.is_alive() or any(m.is_alive() for m in squad)):
        print(f"\n--- TURN {turn} ---")
        print_status()

        # Process status effects first
        process_statuses([player] + squad + enemies)

        # Player & Squad attack
        squad_attack(squad, enemies)
        if not any(e.is_alive() for e in enemies) or (not player.is_alive() and not any(m.is_alive() for m in squad)):
            break
        player_attack(player, enemies)

        # Remove dead enemies
        enemies = [e for e in enemies if e.is_alive()]

        # Enemies attack
        enemies_attack(enemies, player, squad)

        # Remove dead squad members
        for member in squad[:]:
            if not member.is_alive():
                print(f"💀 {member.name} has fallen!")
                squad.remove(member)

        if not player.is_alive() and not squad:
            print("💀 You and your squad have been defeated!")
            return False

        turn += 1

    print(f"\n✅ Wave {wave_num} cleared!")
    reward = 20 + wave_num * 5
    global player_coins
    player_coins += reward
    print(f"You earned {reward} coins!")
    return True

# === Shop & Menu ===

def shop_menu():
    while True:
        print("\n=== SHOP MENU ===")
        print("1. Recruit Squad Member (30 coins)")
        print("2. Upgrade Squad Member (20 coins)")
        print("3. Heal Player (15 coins)")
        print("4. Show Status")
        print("5. Exit Shop")
        choice = input_choice("> ", ["1","2","3","4","5"])
        if choice == "1":
            recruit_member()
        elif choice == "2":
            upgrade_member()
        elif choice == "3":
            heal_player()
        elif choice == "4":
            print_status()
        elif choice == "5":
            break

# === Main Game Loop ===

def main():
    global wave
    print("=== WELCOME TO AUTO-BATTLE SQUAD RPG ===")
    print("Survive waves of enemies, recruit and upgrade your squad, and defeat bosses every 15 waves!\n")

    while True:
        print_status()
        success = battle(wave)
        if not success:
            print("Game Over!")
            break
        shop_menu()
        wave += 1

if __name__ == "__main__":
    main()
