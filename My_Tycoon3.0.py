import time

class TycoonGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.cash = 0
        self.income = 10  # Base income per collect
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
        self.collect_count = 0
        # Manager preferences: which businesses Managers are allowed to buy automatically
        self.manager_preferences = {name: True for name in self.businesses.keys()}

    def bankrupt(self):
        print("\n💥 You couldn't pay your taxes or wages and went BANKRUPT! 💥")
        print("Restarting the game...\n")
        time.sleep(3)
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

        # Managers try to buy businesses every 3 collects
        if self.collect_count % 3 == 0:
            self.auto_buy_businesses()

        # Pay taxes every 5th income collection
        if self.collect_count % 5 == 0:
            tax = int(self.cash * 0.10)  # 10% tax
            if self.cash >= tax:
                self.cash -= tax
                print(f"💸 Taxes paid: ${tax}. Cash after tax: ${self.cash}")
            else:
                self.bankrupt()

        # Pay wages every 10th income collection
        if self.collect_count % 10 == 0:
            total_wages = 0
            for w in self.workers.values():
                wages = w["hired"] * w["wage"]
                total_wages += wages

            if total_wages > 0:
                if self.cash >= total_wages:
                    self.cash -= total_wages
                    print(f"🧾 Wages paid: ${total_wages}. Cash after wages: ${self.cash}")
                else:
                    self.bankrupt()

    def auto_buy_businesses(self):
        managers = self.workers["Manager"]["hired"]
        if managers == 0:
            return  # No managers hired, skip

        for _ in range(managers):
            # Filter businesses by manager preferences AND affordability
            affordable = [(name, b) for name, b in self.businesses.items()
                          if self.cash >= b["cost"] and self.manager_preferences.get(name, False)]
            if not affordable:
                break
            affordable.sort(key=lambda x: x[1]["cost"])
            name, business = affordable[0]

            self.cash -= business["cost"]
            business["owned"] += 1
            business["cost"] = int(business["cost"] * 1.5)
            print(f"🤖 Manager bought a {name} automatically!")

    def show_stats(self):
        print("\n📊 Your Tycoon Empire:")
        print(f"   Cash: ${self.cash}")
        print(f"   Base income per collect: ${self.income}")
        print("\nBusinesses:")
        for name, info in self.businesses.items():
            print(f"  {name}: {info['owned']} owned | Earns ${info['income']} each | Next costs ${info['cost']}")
        print("\nWorkers:")
        for name, info in self.workers.items():
            print(f"  {name}: {info['hired']} hired | Earns ${info['income']} per collect | Wage ${info['wage']} every 10 collects | Hire cost ${info['cost']}")
        print("\nManager Business Preferences:")
        for name, allowed in self.manager_preferences.items():
            status = "✅ Allowed" if allowed else "❌ Not Allowed"
            print(f"  {name}: {status}")

    def buy_business(self):
        print("\n🏬 Businesses Available:")
        for i, (name, info) in enumerate(self.businesses.items(), start=1):
            print(f"{i}. Buy {name} (${info['cost']}) - Earns ${info['income']} each time")

        choice = input("Choose a business to buy (number): ")

        try:
            index = int(choice) - 1
            business_name = list(self.businesses.keys())[index]
            business = self.businesses[business_name]

            if self.cash >= business["cost"]:
                self.cash -= business["cost"]
                business["owned"] += 1
                business["cost"] = int(business["cost"] * 1.5)
                print(f"\n✅ You bought a {business_name}!")
            else:
                print("\n❌ Not enough cash to buy this.")
        except (ValueError, IndexError):
            print("❓ Invalid choice.")

    def hire_worker(self):
        print("\n👷 Workers Available to Hire:")
        for i, (name, info) in enumerate(self.workers.items(), start=1):
            print(f"{i}. Hire {name} (${info['cost']}) - Earns ${info['income']} per collect, Wage ${info['wage']} every 10 collects")

        choice = input("Choose a worker to hire (number): ")

        try:
            index = int(choice) - 1
            worker_name = list(self.workers.keys())[index]
            worker = self.workers[worker_name]

            if self.cash >= worker["cost"]:
                self.cash -= worker["cost"]
                worker["hired"] += 1
                print(f"\n✅ You hired a {worker_name}!")
            else:
                print("\n❌ Not enough cash to hire this worker.")
        except (ValueError, IndexError):
            print("❓ Invalid choice.")

    def manage_manager_preferences(self):
        while True:
            print("\n🛠 Manage Manager Business Preferences")
            for i, (name, allowed) in enumerate(self.manager_preferences.items(), start=1):
                status = "✅ Allowed" if allowed else "❌ Not Allowed"
                print(f"{i}. {name}: {status}")
            print(f"{len(self.manager_preferences) + 1}. Exit")

            choice = input("Toggle preference by number or Exit: ")

            try:
                index = int(choice) - 1
                if index == len(self.manager_preferences):
                    break
                business_name = list(self.manager_preferences.keys())[index]
                self.manager_preferences[business_name] = not self.manager_preferences[business_name]
                new_status = "✅ Allowed" if self.manager_preferences[business_name] else "❌ Not Allowed"
                print(f"Preference for {business_name} set to {new_status}")
            except (ValueError, IndexError):
                print("❓ Invalid choice.")

    def start(self):
        print("🏗️ Welcome to Tycoon Tycoon with Manager Preferences! 🤖👷\n")
        print("You start with $0 cash but earn $10 income every time you collect.")
        print("Taxes of 10% are paid every 5th income collection.")
        print("You must pay your workers' wages every 10th income collection.")
        print("Managers automatically buy businesses every 3 income collections if affordable and allowed.\n")

        while True:
            print("\nWhat would you like to do?")
            print("1. Collect Income 💵")
            print("2. Buy Business 🏪")
            print("3. Hire Worker 👷")
            print("4. View Stats 📊")
            print("5. Manage Manager Preferences ⚙️")
            print("6. Exit ❌")

            choice = input("Enter choice (1-6): ")

            if choice == "1":
                self.collect_income()
            elif choice == "2":
                self.buy_business()
            elif choice == "3":
                self.hire_worker()
            elif choice == "4":
                self.show_stats()
            elif choice == "5":
                self.manage_manager_preferences()
            elif choice == "6":
                print("\nThanks for playing! 👋")
                break
            else:
                print("❓ Invalid option, try again.")

            time.sleep(1)

if __name__ == "__main__":
    game = TycoonGame()
    game.start()
