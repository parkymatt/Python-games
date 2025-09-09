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
        self.collect_count = 0  # Track how many times income was collected

    def collect_income(self):
        total_income = self.income
        for info in self.businesses.values():
            total_income += info["owned"] * info["income"]
        self.cash += total_income
        self.collect_count += 1

        print(f"\n💰 You collected ${total_income}. Total cash: ${self.cash}")

        # Tax every 5th time income is collected
        if self.collect_count % 5 == 0:
            tax = int(self.cash * 0.10)  # 10% tax
            self.cash -= tax
            print(f"💸 Taxes paid: ${tax}. Cash after tax: ${self.cash}")

    def show_stats(self):
        print("\n📊 Your Tycoon Empire:")
        print(f"   Cash: ${self.cash}")
        print(f"   Base income per collect: ${self.income}")
        for name, info in self.businesses.items():
            print(f"   {name}: {info['owned']} owned | Earns ${info['income']} each | Next costs ${info['cost']}")

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

    def start(self):
        print("🏗️ Welcome to Tycoon Tycoon with Taxes!\n")
        print("You start with $0 cash but earn $10 income every time you collect.")
        print("Taxes of 10% are paid every 5th income collection.\n")
        while True:
            print("\nWhat would you like to do?")
            print("1. Collect Income 💵")
            print("2. Buy Business 🏪")
            print("3. View Stats 📊")
            print("4. Exit ❌")

            choice = input("Enter choice (1-4): ")

            if choice == "1":
                self.collect_income()
            elif choice == "2":
                self.buy_business()
            elif choice == "3":
                self.show_stats()
            elif choice == "4":
                print("\nThanks for playing! 👋")
                break
            else:
                print("❓ Invalid option, try again.")

            time.sleep(1)

if __name__ == "__main__":
    game = TycoonGame()
    game.start()
