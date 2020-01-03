"""
      ===== NUMBERS RUNNER v.1.0a =====
      Copyright (C) 2019 IU7Games Team.

      - Ранер для игры NUM63RSGAME, суть которой заключается в получении
        минимально возможного числа, который делится на все числа на интервале [a, b]

      - В соревновании принимают функции, имеющие следующую сигнатуру:
      - int numbers_game(int min, int max)

      - int min - левая граница интервала
      - int max - правая граница интервал

      - Возвращаемое значение: минимально возможное число, являющееся решением задачи.
"""

import ctypes
from random import randint
from timeit import Timer
from time import process_time_ns
from math import sqrt, gcd
from functools import reduce
from worker.wiki import NO_RESULT

OK = 0
SOLUTION_FAIL = 1

MAX_LBORDER = 1
MAX_RBORDER = 22

TIMEIT_REPEATS = 10001


def parsing_name(lib_path):
    """
        Преобразование полного пути к файлу с библиотекой игрока
        к gitlab логину игрока.
    """
    return lib_path[lib_path.rindex('/') + 1: len(lib_path) - 3]


def print_results(results, player_info):
    """
        Печать финальных результатов.
    """

    if player_info != "NULL":
        print(
            "PLAYER:", parsing_name(player_info),
            "SOLUTION:", "OK" if not results["solution"] else "FAIL",
            "MEDIAN:", results["median"],
            "DISPERSON:", results["dispersion"]
        )


def lcm(interval):
    """
        Функция вычисляющая НОК на заданном интервале
    """
    return reduce(lambda x, y: (x * y) // gcd(x, y), interval, 1)


def round_intervals():
    """
        Генерация левой, правой границы интервала и решения для текущего раунда.
    """

    left_border = randint(MAX_LBORDER, MAX_RBORDER)
    right_border = randint(left_border, MAX_RBORDER)
    solution = lcm(range(left_border, right_border + 1))

    return {"l_border": right_border, "r_border": left_border, "solution": solution}


def pack_results(solution, median, dispersion):
    """
        Упаковка результатов в словарь.
    """

    return {"solution": solution, "median": median, "dispersion": dispersion}


def player_results(player_lib, intervals):
    """
        Получение и обработка результатов игрока. Подсчёт времени выполнения его функции.
    """

    player_solution = player_lib.numbers_game(intervals["l_border"], intervals["r_border"])
    if player_solution != intervals["solution"]:
        return pack_results(SOLUTION_FAIL, 0, 0)

    def timeit_wrapper():
        """
            Обёртка для Timeit.
        """

        player_lib.numbers_game(intervals["l_border"], intervals["r_border"])

    time_results = Timer(timeit_wrapper, process_time_ns).repeat(TIMEIT_REPEATS, 1)
    time_results.sort()

    median = time_results[TIMEIT_REPEATS // 2]
    avg_time = sum(time_results) / len(time_results)
    time_results = list(map(lambda x: (x - avg_time) * (x - avg_time), time_results))
    dispersion = sqrt(sum(time_results) / len(time_results))

    return pack_results(OK, median, dispersion)


def start_numbers_game(player_lib):
    """
        Открытие библиотеки с функцией игрока, подсчёт времени исполнения его функции,
        печать результатов.
    """

    intervals = round_intervals()

    if player_lib != "NULL":
        lib = ctypes.CDLL(player_lib)
        results = player_results(lib, intervals)
    else:
        results = pack_results(NO_RESULT, 0, 0)

    print_results(results, player_lib)
    return results["solution"], results["median"], results["dispersion"]

if __name__ == "__main__":
    start_numbers_game("./test.so")
