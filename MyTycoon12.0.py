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
            "Luxury Hotel": {"owned": 0, "income": 8000, "cost": 75000},
            "Automobile Plant": {"owned": 0, "income": 15000, "cost": 150000},
            "Bank": {"owned": 0, "income": 35000, "cost": 300000},
            "Media Conglomerate": {"owned": 0, "income": 90000, "cost": 750000},
            "Tech Giant": {"owned": 0, "income": 200000, "cost": 2000000},
        }
        self.workers = {
            "Worker": {"hired": 0, "wage": 50, "income": 15, "cost": 100, "auto_buy": False},
            "Passive Worker": {"hired": 0, "wage": 40, "income": 25, "cost": 150, "auto_buy": False},
            "Manager": {"hired": 0, "wage": 100, "income": 0, "cost": 500, "auto_buy": True},
        }
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

        self.cash += total_income
        self.collect_count += 1

        print(f"\n💰 You collected ${total_income}. Total cash: ${self.cash}")

        self.random_event()
        self.check_achievements()
        self.check_prestige()

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

        if self.workers["Manager"]["hired"] > 0:
            self.smart_manager_buying()

    def smart_manager_buying(self):
        # Managers buy businesses smartly based on cash and priority
        managers_count = self.workers["Manager"]["hired"]
        # Define business priorities: higher cost = higher priority
        sorted_businesses = sorted(
            self.businesses.items(),
            key=lambda item: item[1]["cost"],
            reverse=True
        )

        # Simple logic to not buy lower-cost businesses if cash is high
        for name, biz in sorted_businesses:
            # If cash > 100k, skip the first three cheapest businesses
            cheapest_names = list(self.businesses.keys())[:3]
            if self.cash > 100000 and name in cheapest_names:
                continue

            # Managers buy businesses only if they can afford it multiple times
            max_affordable = self.cash // biz["cost"]
            buy_amount = min(max_affordable, managers_count)

            if buy_amount > 0:
                cost = buy_amount * biz["cost"]
                self.cash -= cost
                biz["owned"] += buy_amount
                print(f"🤖 Manager bought {buy_amount} {name}(s) for ${cost}")

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
            print(f"{idx}. {name} - Cost: ${info['cost']} - Hired: {info['hired']} - Wage: ${info['wage']}")
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

    def shop(self):
        loot_crate_cost = 100
        print(f"\nWelcome to the Shop! Loot crates cost ${loot_crate_cost} each.")
        print("Opening a loot crate gives you money between $50 and $1000.")
        print("Lower amounts ($100-$200) are more common; amounts above that have a 30% chance.")
        choice = input("Type 'buy' to purchase a loot crate or 'back' to return: ")
        if choice.lower() == "buy":
            if self.cash < loot_crate_cost:
                print("❌ Not enough cash to buy a loot crate.")
                return
            self.cash -= loot_crate_cost
            roll = random.randint(1, 100)
            if roll <= 70:  # 70% chance for lower range
                money_gained = random.randint(50, 200)
            else:  # 30% chance for higher range
                money_gained = random.randint(201, 1000)
            self.cash += money_gained
            print(f"🎉 You opened a loot crate and got ${money_gained}!")
        elif choice.lower() == "back":
            return
        else:
            print("❌ Invalid choice in shop.")

def main():
    game = TycoonGame()

    try:
        while True:
            print("=== Tycoon Game Menu ===")
            print("1. Collect Income")
            print("2. Buy Business")
            print("3. Hire Workers")
            print("4. View Stats")
            print("5. Shop")
            print("6. Exit")
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
                game.shop()
            elif choice == "6":
                print("Thanks for playing! Goodbye.")
                break
            else:
                print("Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nExiting game.")

if __name__ == "__main__":
    main()
