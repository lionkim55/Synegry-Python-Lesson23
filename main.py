import json
from pathlib import Path
from clouds import Clouds
from helicopter import Helicopter
from map import Map
from utils import ask_int, clear_screen, read_key

SAVE_FILE = Path("level.json")

TREE_UPDATE = 22
FIRE_UPDATE = 18
CLOUD_UPDATE = 20
TICK_DELAY = 0.5

MOVES = {
    "w": (-1, 0),
    "a": (0, -1),
    "s": (1, 0),
    "d": (0, 1),
}


def print_rules():
    print("Управление:")
    print("W/A/S/D — движение | E — купить/лечиться | F — сохранить | G — загрузить | Q — выйти")
    print("Обозначения:")
    print("🚁 вертолет | 🌲 дерево | 🌊 вода | 🔥 пожар | 🟫 сгоревшее дерево")
    print("🏥 госпиталь | 🏦 магазин | ⚪ облако | 🟥 гроза")
   
def create_new_game():
    print("Создание новой игры")
    w = ask_int("Введите ширину карты", 20, 8, 35)
    h = ask_int("Введите высоту карты", 10, 6, 20)

    field = Map(w, h)
    clouds = Clouds(w, h)
    helicopter = Helicopter(w, h)
    tick = 1
    return field, clouds, helicopter, tick


def save_game(field, clouds, helicopter, tick):
    data = {
        "field": field.export_data(),
        "clouds": clouds.export_data(),
        "helicopter": helicopter.export_data(),
        "tick": tick,
    }

    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return "Игра сохранена в файл level.json."

def load_game():
    if not SAVE_FILE.exists():
        return None, "Файл сохранения level.json не найден."

    with open(SAVE_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    w = data["field"]["w"]
    h = data["field"]["h"]

    field = Map(w, h)
    clouds = Clouds(w, h)
    helicopter = Helicopter(w, h)

    field.import_data(data["field"])
    clouds.import_data(data["clouds"])
    helicopter.import_data(data["helicopter"])
    tick = data.get("tick", 1)
    return (field, clouds, helicopter, tick), "Игра загружена из файла level.json."


def update_world(field, clouds, helicopter, tick):
    messages = []

    if tick % TREE_UPDATE == 0:
        messages.append(field.generate_tree())

    if tick % FIRE_UPDATE == 0:
        messages.append(field.add_fire())
        messages.extend(field.update_fires(helicopter))

    if tick % CLOUD_UPDATE == 0:
        clouds.update()
        messages.append("Погода изменилась.")

    return messages

def main():
    field, clouds, helicopter, tick = create_new_game()
    message = "Игра началась. Управляйте вертолетом."

    while helicopter.lives > 0:
        clear_screen()
        helicopter.print_stats(tick)
        field.print_map(helicopter, clouds)
        print_rules()
        print("Сообщение:", message)
        
        key = read_key(TICK_DELAY)
        messages = []

        if key in MOVES:
            dx, dy = MOVES[key]
            messages.append(helicopter.move(dx, dy))

        elif key == "e":
            messages.append(field.use_action(helicopter))

        elif key == "f":
            messages.append(save_game(field, clouds, helicopter, tick))

        elif key == "g":
            loaded_game, load_message = load_game()
            messages.append(load_message)

            if loaded_game is not None:
                field, clouds, helicopter, tick = loaded_game

        elif key == "q":
            break

        elif key != "":
            messages.append("Неизвестная команда.")

        messages.extend(field.process_helicopter(helicopter, clouds, tick))
        tick += 1
        messages.extend(update_world(field, clouds, helicopter, tick))

        if messages:
            message = " ".join(messages)

    if helicopter.lives <= 0:
        helicopter.game_over()

if __name__ == "__main__":
    main()
