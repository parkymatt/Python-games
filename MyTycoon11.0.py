import threading
import time
import random

class TycoonGame:
    def __init__(self):
        self.prestige_level = 0
        self.achievements_unlocked = set()
        self.reset_game()

    def reset_game(self):
        self.cash = 0
        self.income = 10 + (10 * self.prestige_level)
        self.businesses = {
            "Car Wash": {"owned": 0, "income": 20, "cost": 200},
            "Factory": {"owned": 0, "income": 50, "cost": 500},
            "Tech Startup": {"owned": 0, "income": 150, "cost": 1500},
            "Real Estate": {"owned": 0, "income": 500, "cost": 5000},
            "Space Company": {"owned": 0, "income": 2000, "cost": 20000},
        }
        self.workers = {
            "Worker": {"hired": 0, "wage": 50, "income": 15, "cost": 100, "auto_buy": False},
            "Passive Worker": {"hired": 0, "wage": 40, "income": 25, "cost": 150, "auto_buy": False},
            "Manager": {"hired": 0, "wage": 100, "income": 0, "cost": 500, "auto_buy": True},
        }
        self.manager_preferences = {name: True for name in self.businesses}
        self.collect_count = 0
        self.loot_crates_price = 100

    def bankrupt(self):
        print("\n💥 You couldn't pay your taxes or wages and went BANKRUPT! 💥")
        print("Restarting the game...\n")
        time.sleep(3)
        self.reset_game()

    def random_event(self):
        if random.randint(1, 5) == 1:
            bonus = random.randint(100, 500)
            self.cash += bonus
            print(f"🎉 Lucky find! You received a surprise bonus of ${bonus}!")

    def check_achievements(self):
        achievements = [
            ("Factory Tycoon", self.businesses["Factory"]["owned"] >= 10),
            ("Startup Mogul", self.businesses["Tech Startup"]["owned"] >= 5),
            ("Real Estate Master", self.businesses["Real Estate"]["owned"] >= 3),
            ("Six Figures", self.cash >= 100000),
            ("Millionaire", self.cash >= 1000000),
            ("Workforce", self.workers["Worker"]["hired"] >= 10),
            ("Automated Empire", self.workers["Manager"]["hired"] >= 5),
            ("Collector", self.collect_count >= 50),
        ]
        for name, condition in achievements:
            if condition and name not in self.achievements_unlocked:
                print(f"🏆 Achievement Unlocked: {name}!")
                self.achievements_unlocked.add(name)

    def check_prestige(self):
        if self.cash >= 1000000:
            print("\n🌟 You've built a massive empire. Prestige?")
            confirm = input("Type 'yes' to prestige and restart with permanent income boost: ")
            if confirm.lower() == "yes":
                self.prestige_level += 1
                print(f"🚀 You prestiged! Permanent income bonus applied (Level {self.prestige_level})")
                self.reset_game()

    def collect_income(self):
        total_income = self.income
        for b in self.businesses.values():
            total_income += b["owned"] * b["income"]
        for w in self.workers.values():
            total_income += w["hired"] * w["income"]

        self.cash += total_income
        self.collect_count += 1

        print(f"\n💰 You collected ${total_income}. Total cash: ${self.cash}")

        self.random_event()
        self.check_achievements()
        self.check_prestige()

        if self.collect_count % 3 == 0:
            self.auto_buy_businesses()

        if self.collect_count % 5 == 0:
            tax = int(self.cash * 0.10)
            if self.cash >= tax:
                self.cash -= tax
                print(f"💸 Taxes paid: ${tax}. Cash after tax: ${self.cash}")
            else:
                self.bankrupt()

        if self.collect_count % 10 == 0:
            total_wages = sum(w["hired"] * w["wage"] for w in self.workers.values())
            if self.cash >= total_wages:
                self.cash -= total_wages
                print(f"🧾 Wages paid: ${total_wages}. Cash after wages: ${self.cash}")
            else:
                self.bankrupt()

    def auto_buy_businesses(self):
        # Disable managers from buying cheaper businesses if cash > 100,000
        disable_list = []
        if self.cash > 100000:
            disable_list = ["Car Wash", "Factory", "Tech Startup"]
        for business in disable_list:
            self.manager_preferences[business] = False

        # Calculate expected tax and wages for next payments (simulate next collect)
        next_collect = self.collect_count + 1
        expected_tax = int(self.cash * 0.10) if next_collect % 5 == 0 else 0
        total_wages = sum(w["hired"] * w["wage"] for w in self.workers.values()) if next_collect % 10 == 0 else 0
        cash_buffer = int(self.cash * 0.20)  # Keep 20% cash in reserve

        # Sort businesses by cost descending (higher priced first)
        sorted_businesses = sorted(
            [(name, b) for name, b in self.businesses.items() if self.manager_preferences.get(name, False)],
            key=lambda x: x[1]["cost"],
            reverse=True,
        )

        for manager_name, business in sorted_businesses:
            if self.workers["Manager"]["hired"] > 0:
                while True:
                    cost = business["cost"]
                    # Check if after buying, cash will cover tax, wages, and buffer
                    if self.cash - cost >= expected_tax + total_wages + cash_buffer:
                        self.cash -= cost
                        business["owned"] += 1
                        print(f"🤖 Manager bought 1 {manager_name} for ${cost}")
                    else:
                        break

    def buy_business(self):
        print("\nBusinesses to buy:")
        for idx, (name, info) in enumerate(self.businesses.items(), 1):
            print(f"{idx}. {name} - Cost: ${info['cost']} - Owned: {info['owned']}")
        choice = input("Enter the number of the business to buy or 'back' to return: ")
        if choice.lower() == 'back':
            return
        try:
            idx = int(choice) - 1
            business_name = list(self.businesses.keys())[idx]
            business = self.businesses[business_name]
            if self.cash >= business["cost"]:
                self.cash -= business["cost"]
                business["owned"] += 1
                print(f"✅ You bought 1 {business_name}")
            else:
                print("❌ Not enough cash to buy that business.")
        except (ValueError, IndexError):
            print("❌ Invalid choice.")

    def hire_workers(self):
        print("\nWorkers to hire:")
        for idx, (name, info) in enumerate(self.workers.items(), 1):
            print(f"{idx}. {name} - Cost: ${info['cost']} - Hired: {info['hired']} - Wage: ${info['wage']} - Auto-buy: {'Yes' if info['auto_buy'] else 'No'}")
        choice = input("Enter the number of the worker to hire or 'back' to return: ")
        if choice.lower() == 'back':
            return
        try:
            idx = int(choice) - 1
            worker_name = list(self.workers.keys())[idx]
            worker = self.workers[worker_name]
            if self.cash >= worker["cost"]:
                self.cash -= worker["cost"]
                worker["hired"] += 1
                print(f"✅ You hired 1 {worker_name}")
            else:
                print("❌ Not enough cash to hire that worker.")
        except (ValueError, IndexError):
            print("❌ Invalid choice.")

    def show_stats(self):
        print("\n" + "="*30)
        print("📊 Current Stats:")
        print(f"Cash: ${self.cash}")
        print(f"Prestige Level: {self.prestige_level}")
        print("Businesses Owned:")
        for name, b in self.businesses.items():
            print(f"  - {name}: {b['owned']}")
        print("Workers Hired:")
        for name, w in self.workers.items():
            print(f"  - {name}: {w['hired']}")
        print(f"Achievements Unlocked: {len(self.achievements_unlocked)}")
        if self.achievements_unlocked:
            print("  (" + ", ".join(self.achievements_unlocked) + ")")
        print("="*30 + "\n")

    def admin_panel(self):
        code = input("\nEnter admin code to access Admin Panel: ")
        if code != "2013":
            print("❌ Incorrect code! Returning to main menu.")
            return
        print("\n✅ Access granted to Admin Panel!")

        while True:
            print("\n--- Admin Panel ---")
            print("1. Add Money")
            print("2. Add Workers")
            print("3. Add Businesses")
            print("4. Edit Workers/Managers")
            print("5. Exit Admin Panel")
            choice = input("Select an option: ")

            if choice == "1":
                amount_str = input("Enter amount of money to add: ")
                try:
                    amount = int(amount_str)
                    if amount > 0:
                        self.cash += amount
                        print(f"✅ Added ${amount} to cash.")
                    else:
                        print("❌ Amount must be positive.")
                except ValueError:
                    print("❌ Invalid amount.")

            elif choice == "2":
                print("Workers:")
                for idx, name in enumerate(self.workers.keys(), 1):
                    print(f"{idx}. {name}")
                w_choice = input("Select worker type to add: ")
                try:
                    w_idx = int(w_choice) - 1
                    worker_name = list(self.workers.keys())[w_idx]
                    qty_str = input(f"How many {worker_name}s to add? ")
                    qty = int(qty_str)
                    if qty > 0:
                        self.workers[worker_name]["hired"] += qty
                        print(f"✅ Added {qty} {worker_name}(s).")
                    else:
                        print("❌ Quantity must be positive.")
                except (ValueError, IndexError):
                    print("❌ Invalid selection or quantity.")

            elif choice == "3":
                print("Businesses:")
                for idx, name in enumerate(self.businesses.keys(), 1):
                    print(f"{idx}. {name}")
                b_choice = input("Select business type to add: ")
                try:
                    b_idx = int(b_choice) - 1
                    business_name = list(self.businesses.keys())[b_idx]
                    qty_str = input(f"How many {business_name}s to add? ")
                    qty = int(qty_str)
                    if qty > 0:
                        self.businesses[business_name]["owned"] += qty
                        print(f"✅ Added {qty} {business_name}(s).")
                    else:
                        print("❌ Quantity must be positive.")
                except (ValueError, IndexError):
                    print("❌ Invalid selection or quantity.")

            elif choice == "4":
                print("\nWorkers/Managers List:")
                for idx, (w_name, w_data) in enumerate(self.workers.items(), 1):
                    print(f"{idx}. {w_name} - Hired: {w_data['hired']} - Wage: ${w_data['wage']} - Cost: ${w_data['cost']}")
                edit_choice = input("Select a worker/manager to edit or type 'back' to return: ")
                if edit_choice.lower() == "back":
                    continue
                try:
                    edit_idx = int(edit_choice) - 1
                    worker_name = list(self.workers.keys())[edit_idx]
                    worker = self.workers[worker_name]

                    print(f"\nEditing {worker_name}:")
                    new_hired = input(f"Enter new number hired (current {worker['hired']}): ")
                    new_wage = input(f"Enter new wage (current ${worker['wage']}): ")
                    new_cost = input(f"Enter new cost (current ${worker['cost']}): ")

                    if new_hired.strip() != "":
                        nh = int(new_hired)
                        if nh >= 0:
                            worker['hired'] = nh
                        else:
                            print("❌ Hired count must be zero or positive, ignoring change.")
                    if new_wage.strip() != "":
                        nw = int(new_wage)
                        if nw >= 0:
                            worker['wage'] = nw
                        else:
                            print("❌ Wage must be zero or positive, ignoring change.")
                    if new_cost.strip() != "":
                        nc = int(new_cost)
                        if nc >= 0:
                            worker['cost'] = nc
                        else:
                            print("❌ Cost must be zero or positive, ignoring change.")

                    print(f"✅ Updated {worker_name} successfully.")

                except (ValueError, IndexError):
                    print("❌ Invalid selection or input.")

            elif choice == "5":
                print("Exiting Admin Panel.")
                break

            else:
                print("❌ Invalid option. Please try again.")

    def shop(self):
        print("\n--- Shop ---")
        print(f"1. Buy Loot Crate - Cost: ${self.loot_crates_price}")
        print("2. Back to Main Menu")
        choice = input("Choose an option: ")

        if choice == "1":
            if self.cash >= self.loot_crates_price:
                self.cash -= self.loot_crates_price
                # Determine loot crate reward
                roll = random.random()
                if roll <= 0.7:  # 70% chance for low reward (50-200)
                    reward = random.randint(50, 200)
                else:  # 30% chance for high reward (201-1000)
                    reward = random.randint(201, 1000)
                self.cash += reward
                print(f"🎁 You bought a loot crate and received ${reward}!")
            else:
                print("❌ Not enough cash to buy a loot crate.")
        elif choice == "2":
            return
        else:
            print("❌ Invalid choice.")

def main():
    game = TycoonGame()

    try:
        while True:
            print("=== Tycoon Game Menu ===")
            print("1. Collect Income")
            print("2. Buy Business")
            print("3. Hire Workers")
            print("4. View Stats")
            print("5. Admin Panel")
            print("6. Shop")
            print("7. Exit")
            choice = input("Choose an action: ")

            if choice == "1":
                game.collect_income()
            elif choice == "2":
                game.buy_business()
            elif choice == "3":
                game.hire_workers()
            elif choice == "4":
                game.show_stats()
            elif choice == "5":
                game.admin_panel()
            elif choice == "6":
                game.shop()
            elif choice == "7":
                print("Thanks for playing! Goodbye.")
                break
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nExiting game.")

if __name__ == "__main__":
    main()
