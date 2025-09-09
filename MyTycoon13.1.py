
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
        self.cash = 10
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
        ]

        self.workers = [
            Worker("Worker", 50, 15, 100),
            Worker("Passive Worker", 40, 25, 150),
            Worker("Manager", 100, 0, 500),
        ]

    def total_income(self):
        income = 10  # Base income
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
            self.cash -= int(self.cash * 0.1)
        if self.collect_count % 10 == 0:
            self.cash -= self.total_wages()
        if self.cash < 0:
            self.reset_game()

    def reset_game(self):
        self.cash = 10
        self.collect_count = 0
        for b in self.businesses:
            b.owned = 0
        for w in self.workers:
            w.hired = 0

    def buy_business(self, index):
        b = self.businesses[index]
        if self.cash >= b.cost:
            self.cash -= b.cost
            b.owned += 1

    def hire_worker(self, index):
        w = self.workers[index]
        if self.cash >= w.cost:
            self.cash -= w.cost
            w.hired += 1

class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        txt = FONT.render(self.text, True, BLACK)
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

class TycoonApp:
    def __init__(self):
        self.game = TycoonGame()
        self.screen = "main"
        self.scroll_offset = 0
        self.buttons = [
            Button(100, 200, 300, 60, "Collect Income", self.game.collect_income),
            Button(100, 280, 300, 60, "Buy Businesses", self.switch_to_businesses),
            Button(100, 360, 300, 60, "Hire Workers", self.switch_to_workers),
            Button(100, 440, 300, 60, "Exit", sys.exit),
        ]

    def switch_to_businesses(self):
        self.screen = "businesses"
        self.scroll_offset = 0

    def switch_to_workers(self):
        self.screen = "workers"
        self.scroll_offset = 0

    def draw_main(self):
        screen.fill(WHITE)
        txt = BIG_FONT.render("Tycoon Game", True, BLACK)
        screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 50))
        for btn in self.buttons:
            btn.draw()
        cash_text = FONT.render(f"Cash: ${self.game.cash:,}", True, BLACK)
        screen.blit(cash_text, (SCREEN_WIDTH - 300, 20))

    def draw_scrollable_list(self, items, is_worker=False):
        screen.fill(WHITE)
        back_button = Button(SCREEN_WIDTH - 150, 20, 120, 50, "Back", self.go_back)
        back_button.draw()

        for i, item in enumerate(items):
            y = 150 + i * 70 - self.scroll_offset
            if 100 <= y <= SCREEN_HEIGHT - 60:
                pygame.draw.rect(screen, GRAY, (100, y, 800, 60))
                if is_worker:
                    txt = FONT.render(f"{item.name} | Cost: ${item.cost} | Hired: {item.hired}", True, BLACK)
                else:
                    txt = FONT.render(f"{item.name} | Cost: ${item.cost} | Owned: {item.owned}", True, BLACK)
                screen.blit(txt, (110, y + 15))

    def go_back(self):
        self.screen = "main"

    def handle_scroll(self, event, item_count):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = max(self.scroll_offset - 30, 0)
            elif event.button == 5:
                max_scroll = max(0, item_count * 70 - (SCREEN_HEIGHT - 200))
                self.scroll_offset = min(self.scroll_offset + 30, max_scroll)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.screen == "main":
                    for btn in self.buttons:
                        btn.handle_event(event)

                elif self.screen == "businesses":
                    self.handle_scroll(event, len(self.game.businesses))
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        for i, b in enumerate(self.game.businesses):
                            y = 150 + i * 70 - self.scroll_offset
                            if pygame.Rect(100, y, 800, 60).collidepoint(mx, my):
                                self.game.buy_business(i)
                        if pygame.Rect(SCREEN_WIDTH - 150, 20, 120, 50).collidepoint(mx, my):
                            self.screen = "main"

                elif self.screen == "workers":
                    self.handle_scroll(event, len(self.game.workers))
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        for i, w in enumerate(self.game.workers):
                            y = 150 + i * 70 - self.scroll_offset
                            if pygame.Rect(100, y, 800, 60).collidepoint(mx, my):
                                self.game.hire_worker(i)
                        if pygame.Rect(SCREEN_WIDTH - 150, 20, 120, 50).collidepoint(mx, my):
                            self.screen = "main"

            if self.screen == "main":
                self.draw_main()
            elif self.screen == "businesses":
                self.draw_scrollable_list(self.game.businesses)
            elif self.screen == "workers":
                self.draw_scrollable_list(self.game.workers, is_worker=True)

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    app = TycoonApp()
    app.run()
