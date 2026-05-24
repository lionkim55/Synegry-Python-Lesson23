from utils import randcell, clear_screen


class Helicopter:
    def __init__(self, w, h):
        self.x, self.y = randcell(w, h)
        self.w = w
        self.h = h
        self.water = 0
        self.max_water = 1
        self.score = 0
        self.lives = 20

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if 0 <= new_x < self.h and 0 <= new_y < self.w:
            self.x = new_x
            self.y = new_y
            return "Вертолет переместился."

        return "Нельзя выйти за границы карты."

    def print_stats(self, tick):
        print(f"🪣 Вода: {self.water}/{self.max_water} | 🏆 Очки: {self.score} | 💛 Жизни: {self.lives} | Ход: {tick}")

    def game_over(self):
        clear_screen()
        print("=" * 45)
        print("ИГРА ОКОНЧЕНА")
        print(f"Ваш итоговый счет: {self.score}")
        print("=" * 45)

    def export_data(self):
        return {
            "x": self.x,
            "y": self.y,
            "w": self.w,
            "h": self.h,
            "water": self.water,
            "max_water": self.max_water,
            "score": self.score,
            "lives": self.lives,
        }

    def import_data(self, data):
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)
        self.w = data.get("w", self.w)
        self.h = data.get("h", self.h)
        self.water = data.get("water", 0)
        self.max_water = data.get("max_water", 1)
        self.score = data.get("score", 0)
        self.lives = data.get("lives", 20)
