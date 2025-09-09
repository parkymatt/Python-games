
import pygame
import sys

pygame.init()

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tycoon Game")

# Fonts
FONT = pygame.font.SysFont("arial", 30)
BIG_FONT = pygame.font.SysFont("arial", 50)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

class Business:
    def __init__(self, name, income, cost):
        self.name = name
        self.income = income
        self.cost = cost
        self.owned = 0

class Worker:
    def __init__(self, name, wage, income, cost):
        self.name = name
        self.wage = wage
        self.income = income
        self.cost = cost
        self.hired = 0

class TycoonGame:
    def __init__(self):
        self.cash = 10  # Starting cash
        self.collect_count = 0

        self.businesses = [
            Business("Real Estate", 500, 5000),
            Business("Space Company", 2000, 20000),
            Business("Luxury Hotel", 4500, 45000),
            Business("Car Manufacturer", 7000, 70000),
            Business("Bank", 9000, 90000),
            Business("Airline", 12000, 120000),
            Business("Tech Giant", 20000, 200000),
            Business("Space Tourism", 40000, 400000),
            Business("AI Corporation", 80000, 800000),
            Business("Energy Company", 160000, 1600000),
            Business("Global Media", 320000, 3200000),
            Business("Luxury Real Estate", 640000, 6400000),
            Business("Worldwide Conglomerate", 1280000, 12800000),
            Business("International Space Port", 2560000, 25600000),
            Business("Mars Colonization", 5120000, 51200000),
            Business("Interstellar Trade", 10240000, 102400000),
            Business("Universal AI Network", 20480000, 204800000),
            Business("Galactic Federation", 40960000, 409600000),
            Business("Multiverse Inc.", 81920000, 819200000),
            Business("Quantum Holdings", 163840000, 1638400000)
        ]

        self.workers = [
            Worker("Worker", 50, 15, 100),
            Worker("Passive Worker", 40, 25, 150),
            Worker("Manager", 100, 0, 500),
        ]

    def total_income(self):
        income = 10
        for b in self.businesses:
            income += b.income * b.owned
        for w in self.workers:
            income += w.income * w.hired
        return income

    def total_wages(self):
        return sum(w.wage * w.hired for w in self.workers)

    def collect_income(self):
        income = self.total_income()
        self.cash += income
        self.collect_count += 1

        if self.collect_count % 5 == 0:
            tax = int(self.cash * 0.10)
            self.cash = max(0, self.cash - tax)

        if self.collect_count % 10 == 0:
            wages = self.total_wages()
            self.cash = max(0, self.cash - wages)

    def buy_business(self, index):
        b = self.businesses[index]
        if self.cash >= b.cost:
            self.cash -= b.cost
            b.owned += 1
            return True
        return False

    def hire_worker(self, index):
        w = self.workers[index]
        if self.cash >= w.cost:
            self.cash -= w.cost
            w.hired += 1
            return True
        return False

if __name__ == "__main__":
    app = TycoonApp()
    app.run()