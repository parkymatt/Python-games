import threading
import time
import random

class TycoonGame:
    def __init__(self):
        self.prestige_level = 0
        self.achievements_unlocked = set()
        self.reset_game()
        self.super_manager_stop_event = threading.Event()
        self.super_manager_thread = threading.Thread(target=self.super_manager_auto_collect_loop, daemon=True)
        self.super_manager_thread.start()

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
            "Super Manager": {"hired": 0, "wage": 1500, "income": 0, "cost": 10000, "auto_buy": True},
        }
        self.manager_preferences = {name: True for name in self.businesses}
        self.collect_count = 0

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

        # Add extra income from Super Managers
        super_manager_count = self.workers["Super Manager"]["hired"]
        super_manager_income_per = 500  # Adjust as needed
        extra_income = super_manager_count * super_manager_income_per
        total_income += extra_income

        self.cash += total_income
        self.collect_count += 1

        print(f"\n💰 You collected ${total_income} (including ${extra_income} from Super Managers). Total cash: ${self.cash}")

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

        # Super Managers do auto-buy and auto-hire actions
        self.super_manager_actions()

    def auto_buy_businesses(self):
        for manager_name, managed in self.manager_preferences.items():
            if managed and self.workers["Manager"]["hired"] > 0:
                business = self.businesses[manager_name]
                while self.cash >= business["cost"]:
                    self.cash -= business["cost"]
                    business["owned"] += 1
                    print(f"🤖 Manager bought 1 {manager_name} for ${business['cost']}")

    def super_manager_actions(self):
        count = self.workers["Super Manager"]["hired"]
        if count == 0:
            return

        print(f"\n🤖 Super Managers ({count}) are working for you...")

        # Auto-buy businesses count times
        for _ in range(count):
            for manager_name, managed in self.manager_preferences.items():
                if managed:
                    business = self.businesses[manager_name]
                    if self.cash >= business["cost"]:
                        self.cash -= business["cost"]
                        business["owned"] += 1
                        print(f"🤖 Super Manager bought 1 {manager_name} for ${business['cost']}")

        # Auto-hire one of each worker count times if affordable
        worker_names = ["Worker", "Passive Worker", "Manager"]
        for _ in range(count):
            for w_name in worker_names:
                worker = self.workers[w_name]
                if self.cash >= worker["cost"]:
                    self.cash -= worker["cost"]
                    worker["hired"] += 1
                    print(f"🤖 Super Manager hired 1 {w_name}")

    def super_manager_auto_collect_loop(self):
        while not self.super_manager_stop_event.is_set():
            if self.workers["Super Manager"]["hired"] > 0:
                self.collect_income()
                print("\n[Super Manager auto-collect triggered]\n")
            # Check every 5 seconds regardless of Super Manager count
            time.sleep(5)

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

    def toggle_manager_preference(self):
        print("\nManager Preferences (which businesses managers auto-buy):")
        for idx, name in enumerate(self.manager_preferences.keys(), 1):
            status = "Yes" if self.manager_preferences[name] else "No"
            print(f"{idx}. {name} - Auto-buy: {status}")
        choice = input("Enter the number to toggle preference or 'back' to return: ")
        if choice.lower() == "back":
            return
        try:
            idx = int(choice) - 1
            business_name = list(self.manager_preferences.keys())[idx]
            self.manager_preferences[business_name] = not self.manager_preferences[business_name]
            status = "enabled" if self.manager_preferences[business_name] else "disabled"
            print(f"✅ Auto-buy for {business_name} {status}.")
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
            print("4. Exit Admin Panel")
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
                print("Exiting Admin Panel.")
                break

            else:
                print("❌ Invalid option. Please try again.")

def main():
    game = TycoonGame()

    try:
        while True:
            print("=== Tycoon Game Menu ===")
            print("1. Collect Income")
            print("2. Buy Business")
            print("3. Hire Workers")
            print("4. Toggle Manager Auto-Buy Preferences")
            print("5. View Stats")
            print("6. Admin Panel")
            print("7. Exit")
            choice = input("Choose an action: ")

            if choice == "1":
                game.collect_income()
            elif choice == "2":
                game.buy_business()
            elif choice == "3":
                game.hire_workers()
            elif choice == "4":
                game.toggle_manager_preference()
            elif choice == "5":
                game.show_stats()
            elif choice == "6":
                game.admin_panel()
            elif choice == "7":
                print("Thanks for playing! Goodbye.")
                break
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nExiting game.")
    finally:
        game.super_manager_stop_event.set()
        game.super_manager_thread.join()

if __name__ == "__main__":
    main()
