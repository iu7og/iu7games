"""
    ===== SEQUENCE RUNNER v.1.0b =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    - Ранер для игры 7EQUEENCEGAME, суть которой заключается в нахождении максимально
    возможного произведения 13 подряд идущих чисел в массиве, состоящего из 1000 цифр.

    - В соревновании принимают функции, имеющие следующую сигнатуру:
    - long long sequence_game(int array[])

    - int array[] - указатель на начало массива, содержащего 1000 цифр.

    - Возвращаемое значение: максимально возможное число, подходящее под условие задачи.
"""

import ctypes
from random import randint
from functools import reduce
from timeit import Timer
from time import process_time_ns
import games.utils.utils as utils

TIMEIT_REPEATS = 100001

ARRAY_LENGTH = 1000
INTERVAL_LENGTH = 13


def generate_array():
    """
        Генерация случайного массива из 1000 цифр.
    """
    return [randint(1, 9) for x in range(ARRAY_LENGTH)]


def solution_counting(array):
    """
        Подсчёт правильно ответа, для данного массива.
    """

    subarrays = [array[i: INTERVAL_LENGTH + i]
                 for i in range(ARRAY_LENGTH - INTERVAL_LENGTH + 1)]
    all_prods = [reduce(lambda x, y: x * y, arrays, 1) for arrays in subarrays]
    return max(all_prods)


def generate_game_conditions():
    """
        Создание массива для игры и и подсчёт решения.
    """

    array = generate_array()
    solution = solution_counting(array)
    return {"array": array, "solution": solution}


def player_results(game_conditions, player_lib):
    """
        Подсчёт времени выполнения стратегии игрока и проверка корректности его ответа.
    """

    c_array = (ctypes.c_int * ARRAY_LENGTH)(*game_conditions["array"])
    player_solution = player_lib.sequence_game(c_array)

    if player_solution != game_conditions["solution"]:
        return (utils.GameResult.fail, 0, 0)

    def timeit_wrapper():
        """
            Обёртка для Timeit.
        """

        player_lib.sequence_game(c_array)

    time_results = Timer(timeit_wrapper, process_time_ns).repeat(
        TIMEIT_REPEATS, 1)
    median, dispersion = utils.process_time(time_results)

    return (utils.GameResult.okay, median, dispersion)


def start_sequence_game(players_libs):
    """
        Открытие функции с библиотеками игроков, запуск их функций, печать результатов.
    """

    utils.redirect_ctypes_stdout()
    game_conditions = generate_game_conditions()
    results = []

    for lib in players_libs:
        if lib != "NULL":
            player_lib = ctypes.CDLL(lib)
            player_lib.sequence_game.restype = ctypes.c_longlong
            results.append(player_results(game_conditions, player_lib))
        else:
            results.append((utils.GameResult.no_result, 0, 0))

    utils.print_results(results, players_libs)
    return results


if __name__ == "__main__":
    start_sequence_game(
        ["games/sequence/test.so", "games/sequence/test.so", "NULL"])
