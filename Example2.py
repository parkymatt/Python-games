
# Full BitLife-Style Life Simulator
import random

class Person:
    def __init__(self, name, age=0, relation=None):
        self.name = name
        self.age = age
        self.relation = relation
        self.alive = True

class Player(Person):
    def __init__(self, name):
        super().__init__(name, age=0)
        self.money = 0
        self.happiness = random.randint(40, 80)
        self.health = random.randint(40, 80)
        self.intelligence = random.randint(40, 80)
        self.looks = random.randint(40, 80)
        self.education = "None"
        self.career = "None"
        self.relationship = None
        self.spouse = None
        self.children = []
        self.parents = [Person(random.choice(["Alex", "Sam", "Taylor", "Jordan", "Morgan"]), age=30, relation="Mother"),
                        Person(random.choice(["Chris", "Pat", "Jamie", "Robin", "Casey"]), age=32, relation="Father")]
        self.siblings = [Person(random.choice(["Lee", "Drew", "Sky", "Riley", "Quinn"]), age=random.randint(0, 18), relation="Sibling") for _ in range(random.randint(0,2))]
        self.alive = True

    def status(self):
        print(f"\nName: {self.name} | Age: {self.age} | Money: ${self.money} | Happiness: {self.happiness} | Health: {self.health} | Intelligence: {self.intelligence} | Looks: {self.looks}")
        print(f"Education: {self.education} | Career: {self.career}")
        print(f"Relationship: {self.relationship} | Spouse: {self.spouse}")
        print(f"Children: {[child.name for child in self.children]}")
        print(f"Parents: {[parent.name for parent in self.parents]}")
        print(f"Siblings: {[sib.name for sib in self.siblings]}")

    def age_up(self):
        self.age += 1
        self.health -= random.randint(0, 3)
        self.happiness -= random.randint(0, 2)
        self.random_event()
        if self.health <= 0 or self.happiness <= 0:
            self.alive = False
            print("You died! Game Over.")

    def study(self):
        if self.age < 6:
            print("You're too young for school!")
            return
        if self.education == "None":
            self.education = "Elementary School"
            print("You started elementary school.")
        elif self.education == "Elementary School" and self.age >= 12:
            self.education = "High School"
            print("You started high school.")
        elif self.education == "High School" and self.age >= 18:
            self.education = "College"
            print("You started college.")
        elif self.education == "College" and self.age >= 22:
            self.education = "Graduate"
            print("You graduated college!")
        else:
            print("No new education opportunities this year.")
        self.intelligence += random.randint(1, 5)
        self.happiness += 1

    def get_job(self):
        if self.age < 18 or self.education not in ["High School", "College", "Graduate"]:
            print("You need to finish high school and be 18+ to get a job!")
            return
        jobs = ["Retail", "Artist", "Engineer", "Teacher", "Doctor", "CEO"]
        self.career = random.choice(jobs)
        self.money += random.randint(1000, 5000)
        print(f"You got a job as a {self.career}!")

    def work(self):
        if self.career == "None":
            print("You need a job first!")
            return
        earned = random.randint(1000, 3000)
        self.money += earned
        self.happiness -= 2
        self.health -= 1
        print(f"You worked as a {self.career} and earned ${earned}.")

    def date(self):
        if self.age < 16:
            print("You're too young to date!")
            return
        if self.relationship:
            print(f"You are already dating {self.relationship}.")
            return
        partners = ["Alex", "Sam", "Taylor", "Jordan", "Morgan"]
        self.relationship = random.choice(partners)
        self.happiness += 10
        print(f"You started dating {self.relationship}!")

    def marry(self):
        if not self.relationship:
            print("You need to be in a relationship to marry!")
            return
        if self.spouse:
            print("You are already married!")
            return
        self.spouse = self.relationship
        self.relationship = None
        self.happiness += 20
        print(f"You married {self.spouse}!")

    def have_child(self):
        if not self.spouse:
            print("You need to be married to have children!")
            return
        child_name = random.choice(["Jamie", "Robin", "Casey", "Sky", "Riley", "Quinn"])
        child = Person(child_name, age=0, relation="Child")
        self.children.append(child)
        self.happiness += 15
        print(f"You had a child named {child_name}!")

    def random_event(self):
        events = [
            ("You got sick!", lambda p: setattr(p, 'health', max(p.health - 20, 0))),
            ("You won a lottery!", lambda p: setattr(p, 'money', p.money + 5000)),
            ("You made a new friend!", lambda p: setattr(p, 'happiness', p.happiness + 10)),
            ("You lost your wallet!", lambda p: setattr(p, 'money', max(p.money - 300, 0))),
            ("You got promoted!", lambda p: setattr(p, 'money', p.money + 2000)),
            ("You got scammed!", lambda p: setattr(p, 'money', max(p.money - 1000, 0))),
            ("You went on vacation!", lambda p: setattr(p, 'happiness', p.happiness + 15)),
            ("Nothing happened this year.", lambda p: None),
        ]
        event, effect = random.choice(events)
        print(f"Random Event: {event}")
        effect(self)



def main():
    name = input("Enter your name: ")
    player = Player(name)
    print("Welcome to BitLife!")
    while player.alive:
        player.status()
        print("Choose an action:")
        print("1) Age Up 2) Study 3) Get Job 4) Work 5) Date 6) Marry 7) Have Child 8) Quit")
        choice = input("Your choice: ")
        if choice == "1":
            player.age_up()
        elif choice == "2":
            player.study()
        elif choice == "3":
            player.get_job()
        elif choice == "4":
            player.work()
        elif choice == "5":
            player.date()
        elif choice == "6":
            player.marry()
        elif choice == "7":
            player.have_child()
        elif choice == "8":
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
