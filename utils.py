from random import randint, choice
import os
import sys
import time

def randbool(chance, max_chance):
    """Возвращает True с заданной вероятностью."""
    return randint(1, max_chance) <= chance


def randcell(w, h):
    """Случайная клетка карты: x - строка, y - столбец."""
    x = randint(0, h - 1)
    y = randint(0, w - 1)
    return x, y


def rand_neighbor(x, y):
    """Случайная соседняя клетка: вверх, вправо, вниз или влево."""
    dx, dy = choice([(-1, 0), (0, 1), (1, 0), (0, -1)])
    return x + dx, y + dy


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def ask_int(text, default, min_value, max_value):
    """Запрашивает число. Если нажать Enter, берется значение по умолчанию."""
    while True:
        value = input(f"{text} [{default}]: ").strip()

        if value == "":
            return default

        if value.isdigit():
            number = int(value)
            if min_value <= number <= max_value:
                return number

        print(f"Введите число от {min_value} до {max_value}.")


def read_key(wait_seconds=0.5):
    """
    Читает клавишу без обязательного Enter.
    Если игрок ничего не нажал, возвращает пустую строку.
    Благодаря этому игра обновляется сама, даже если вертолет стоит.
    """
    if sys.platform.startswith("win"):
        import msvcrt

        start_time = time.time()
        while time.time() - start_time < wait_seconds:
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()

                # Пропускаем специальные клавиши, например стрелки.
                if key in ("\x00", "\xe0"):
                    msvcrt.getwch()
                    return ""

                return key

            time.sleep(0.03)

        return ""

    try:
        import select

        ready, _, _ = select.select([sys.stdin], [], [], wait_seconds)
        if ready:
            return sys.stdin.read(1).lower()
    except Exception:
        pass

    time.sleep(wait_seconds)
    return ""
