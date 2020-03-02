"""
        ===== NUMBERS RUNNER v.1.0c =====
        Copyright (C) 2019 - 2020 IU7Games Team.

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
from math import gcd
from functools import reduce
import games.utils.utils as utils

MAX_LBORDER = 14
MAX_RBORDER = 22

TIMEIT_REPEATS = 1001

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

    return {"l_border": left_border, "r_border": right_border, "solution": solution}


def player_results(player_lib, intervals):
    """
        Получение и обработка результатов игрока. Подсчёт времени выполнения его функции.
    """

    player_solution = player_lib.numbers_game(intervals["l_border"], intervals["r_border"])
    if player_solution != intervals["solution"]:
        return (utils.SOLUTION_FAIL, 0, 0)

    def timeit_wrapper():
        """
            Обёртка для Timeit.
        """

        player_lib.numbers_game(intervals["l_border"], intervals["r_border"])

    time_results = Timer(timeit_wrapper, process_time_ns).repeat(TIMEIT_REPEATS, 1)
    median, dispersion = utils.process_time(time_results)

    return (utils.OK, median, dispersion)


def print_conditions(intervals):
    """
        Печать условий раунда.
    """

    print(
        f'LEFT: {intervals["l_border"]}' +
        f'RIGHT: {intervals["r_border"]}' +
        f'SOLUTION: {intervals["solution"]}'
    )


def start_numbers_game(players_info):
    """
        Открытие библиотеки с функциями игроков, подсчёт времени исполнения их функций,
        печать результатов.
    """

    utils.redirect_ctypes_stdout()
    intervals = round_intervals()
    print_conditions(intervals)
    results = []

    for player_lib in players_info:
        if player_lib != "NULL":
            lib = ctypes.CDLL(player_lib)
            results.append(player_results(lib, intervals))
        else:
            results.append((utils.NO_RESULT, 0, 0))

    utils.print_results(results, players_info)
    return results

if __name__ == "__main__":
    start_numbers_game(["games/numbers/test.so", "NULL", "games/numbers/test.so"])
