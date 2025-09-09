import time

class TycoonGame:
    def __init__(self):
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
            "Worker": {"hired": 0, "wage": 50, "income": 15, "cost": 100},
        }
        self.collect_count = 0  # Count of income collections

    def collect_income(self):
        total_income = self.income
        for info in self.businesses.values():
            total_income += info["owned"] * info["income"]
        for w in self.workers.values():
            total_income += w["hired"] * w["income"]
        
        self.cash += total_income
        self.collect_count += 1

        print(f"\n💰 You collected ${total_income}. Total cash: ${self.cash}")

        # Pay taxes every 5th income collection
        if self.collect_count % 5 == 0:
            tax = int(self.cash * 0.10)  # 10% tax
            self.cash -= tax
            print(f"💸 Taxes paid: ${tax}. Cash after tax: ${self.cash}")

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
                    print(f"⚠️ Not enough cash to pay wages of ${total_wages}! You owe your workers!")

    def show_stats(self):
        print("\n📊 Your Tycoon Empire:")
        print(f"   Cash: ${self.cash}")
        print(f"   Base income per collect: ${self.income}")
        print("\nBusinesses:")
        for name, info in self.businesses.items():
            print(f"  {name}: {info['owned']} owned | Earns ${info['income']} each | Next costs ${info['cost']}")
        print("\nWorkers:")
        for name, info in self.workers.items():
            print(f"  {name}: {info['hired']} hired | Earns ${info['income']} each collect | Wage ${info['wage']} every 10 collects | Hire cost ${info['cost']}")

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

    def start(self):
        print("🏗️ Welcome to Tycoon Tycoon with Workers and Wages!\n")
        print("You start with $0 cash but earn $10 income every time you collect.")
        print("Taxes of 10% are paid every 5th income collection.")
        print("You must pay your workers' wages every 10th income collection.\n")
        while True:
            print("\nWhat would you like to do?")
            print("1. Collect Income 💵")
            print("2. Buy Business 🏪")
            print("3. Hire Worker 👷")
            print("4. View Stats 📊")
            print("5. Exit ❌")

            choice = input("Enter choice (1-5): ")

            if choice == "1":
                self.collect_income()
            elif choice == "2":
                self.buy_business()
            elif choice == "3":
                self.hire_worker()
            elif choice == "4":
                self.show_stats()
            elif choice == "5":
                print("\nThanks for playing! 👋")
                break
            else:
                print("❓ Invalid option, try again.")

            time.sleep(1)

if __name__ == "__main__":
    game = TycoonGame()
    game.start()
