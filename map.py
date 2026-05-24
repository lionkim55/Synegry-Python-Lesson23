from utils import randbool, randcell, rand_neighbor

CELL_EMPTY = 0
CELL_TREE = 1
CELL_RIVER = 2
CELL_HOSPITAL = 3
CELL_SHOP = 4
CELL_FIRE = 5
CELL_BURNT = 6

ICONS = {
    CELL_EMPTY: "🟩",
    CELL_TREE: "🌲",
    CELL_RIVER: "🌊",
    CELL_HOSPITAL: "🏥",
    CELL_SHOP: "🏦",
    CELL_FIRE: "🔥",
    CELL_BURNT: "🟫",
}

TREE_BONUS = 100
TREE_LOSS = 50
UPGRADE_COST = 500
LIFE_COST = 300
FIRE_LIFETIME = 10
STORM_DAMAGE_DELAY = 3

class Map:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cells = [[CELL_EMPTY for _ in range(w)] for _ in range(h)]
        self.fire_age = {}

        self.generate_forest()
        self.generate_river(12)
        self.generate_river(10)
        self.generate_shop()
        self.generate_hospital()

    def check_bounds(self, x, y):
        return 0 <= x < self.h and 0 <= y < self.w

    def print_map(self, helicopter, clouds):
        border = "⬛"
        print((border + " ") * (self.w + 2))

        for x in range(self.h):
            row = []

            for y in range(self.w):
                cloud = clouds.cells[x][y]

                if cloud == 2:
                    row.append("🟥")
                elif cloud == 1:
                    row.append("⚪")
                elif helicopter.x == x and helicopter.y == y:
                    row.append("🚁")
                else:
                    row.append(ICONS[self.cells[x][y]])

            print(border, " ".join(row), border)

        print((border + " ") * (self.w + 2))

    def find_empty_cell(self):
        for _ in range(200):
            x, y = randcell(self.w, self.h)
            if self.cells[x][y] in (CELL_EMPTY, CELL_BURNT):
                return x, y
        return None

    def generate_forest(self):
        for x in range(self.h):
            for y in range(self.w):
                if randbool(3, 10):
                    self.cells[x][y] = CELL_TREE

    def generate_tree(self):
        place = self.find_empty_cell()
        if place is None:
            return "Для нового дерева нет места."

        x, y = place
        self.cells[x][y] = CELL_TREE
        return "Выросло новое дерево."

    def generate_river(self, length):
        x, y = randcell(self.w, self.h)
        self.cells[x][y] = CELL_RIVER

        for _ in range(length):
            new_x, new_y = rand_neighbor(x, y)

            if self.check_bounds(new_x, new_y):
                x, y = new_x, new_y
                self.cells[x][y] = CELL_RIVER

    def generate_shop(self):
        place = self.find_empty_cell()
        if place is not None:
            x, y = place
            self.cells[x][y] = CELL_SHOP

    def generate_hospital(self):
        place = self.find_empty_cell()
        if place is not None:
            x, y = place
            self.cells[x][y] = CELL_HOSPITAL

    def add_fire(self):
        for _ in range(200):
            x, y = randcell(self.w, self.h)
            if self.cells[x][y] == CELL_TREE:
                self.cells[x][y] = CELL_FIRE
                self.fire_age[f"{x},{y}"] = 0
                return "Загорелось дерево."
        return "На карте нет деревьев для пожара."

    def spread_fire(self, x, y):
        new_x, new_y = rand_neighbor(x, y)

        if self.check_bounds(new_x, new_y) and self.cells[new_x][new_y] == CELL_TREE:
            self.cells[new_x][new_y] = CELL_FIRE
            self.fire_age[f"{new_x},{new_y}"] = 0
            return True

        return False

    def update_fires(self, helicopter):
        messages = []
        new_fire_age = {}

        for key, age in list(self.fire_age.items()):
            x, y = map(int, key.split(","))

            if self.cells[x][y] != CELL_FIRE:
                continue

            age += 1

            if age >= FIRE_LIFETIME:
                self.cells[x][y] = CELL_BURNT
                helicopter.score -= TREE_LOSS
                messages.append("Дерево сгорело. Минус очки.")

                if self.spread_fire(x, y):
                    messages.append("Пожар распространился на соседнее дерево.")
            else:
                new_fire_age[key] = age

        self.fire_age.update(new_fire_age)

        self.fire_age = {
            key: age for key, age in self.fire_age.items()
            if self.cells[int(key.split(',')[0])][int(key.split(',')[1])] == CELL_FIRE
        }

        return messages

    def process_helicopter(self, helicopter, clouds, tick):
        messages = []
        cell = self.cells[helicopter.x][helicopter.y]
        cloud = clouds.cells[helicopter.x][helicopter.y]

        if cell == CELL_RIVER and helicopter.water < helicopter.max_water:
            helicopter.water = helicopter.max_water
            messages.append("Вертолет набрал воду из реки.")

        if cell == CELL_FIRE:
            if helicopter.water > 0:
                helicopter.water -= 1
                helicopter.score += TREE_BONUS
                self.cells[helicopter.x][helicopter.y] = CELL_TREE
                self.fire_age.pop(f"{helicopter.x},{helicopter.y}", None)
                messages.append("Пожар потушен. Плюс очки.")
            else:
                messages.append("Здесь пожар. Нужна вода.")

        if cloud == 2 and tick % STORM_DAMAGE_DELAY == 0:
            helicopter.lives -= 1
            messages.append("Вертолет находится в грозе. Минус 1 жизнь.")

        return messages

    def use_action(self, helicopter):
        cell = self.cells[helicopter.x][helicopter.y]

        if cell == CELL_SHOP:
            if helicopter.score >= UPGRADE_COST:
                helicopter.score -= UPGRADE_COST
                helicopter.max_water += 1
                return f"Бак улучшен. Теперь вместимость: {helicopter.max_water}."
            return f"Не хватает очков. Нужно {UPGRADE_COST}."

        if cell == CELL_HOSPITAL:
            if helicopter.score >= LIFE_COST:
                helicopter.score -= LIFE_COST
                helicopter.lives += 2
                return "В госпитале восстановлено 2 жизни."
            return f"Не хватает очков. Нужно {LIFE_COST}."

        return "Здесь нечего использовать."

    def export_data(self):
        return {
            "w": self.w,
            "h": self.h,
            "cells": self.cells,
            "fire_age": self.fire_age,
        }

    def import_data(self, data):
        self.w = data.get("w", self.w)
        self.h = data.get("h", self.h)
        self.cells = data.get("cells", self.cells)
        self.fire_age = data.get("fire_age", {})
