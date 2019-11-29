"""
      ===== STRTOK RUNNER v.1.2c =====
      Copyright (C) 2019 IU7Games Team.

    - Данный скрипт предназначен для тестирования самописной функции strtok,
      реализованной на СИ. Функция на СИ имеет сигнатуру:

    - char *strtok(char *string, const char *delim)

    - char *string - указатель на начало разбиваемой строки
    - const char *delim - указатель на начало строки с разделителями

    - Возвращаемое значение: указатель на следующий элемент
      после первого встреченного делителя.
    - Функция должна полностью повторять поведение стандартного strtok (c99).
"""


import ctypes
from timeit import Timer
from time import process_time_ns
from functools import partial
from math import sqrt
from games.strgame.runner import runner

OK = 0
INVALID_PTR = 1

DELIMITERS = " ,.;:"
ENCODING = "utf-8"
NULL = 0

STRING_MULTIPLIER = 15
TIMEIT_REPEATS = 1
TIME_COUNTER_REPEATS = 101


def check_strtok_correctness(player_ptr, correct_ptr):
    """
        Проверка корректности возвращаемого указателя
        из функции strtok, сравнение со стандартным поведением
        функции в СИ.
    """

    if not player_ptr and correct_ptr:
        return INVALID_PTR

    if player_ptr.value is not None:
        if player_ptr.value.decode(ENCODING) != correct_ptr.value.decode(ENCODING):
            return INVALID_PTR

    return OK


def create_c_objects(bytes_string, delimiters):
    """
        Создание объектов для языка СИ, используемых функцией strtok
        1. c_delimiters_string - массив символов-компараторов (char *delim)
        2. c_string_player - массив символов для игрока (const char *string)
        3. c_string - массив символов для проверки ходов игрока (const char *string)
    """

    c_delimiters_string = ctypes.create_string_buffer(delimiters)
    c_string = ctypes.create_string_buffer(bytes_string)
    c_string_player = ctypes.create_string_buffer(bytes_string)

    return c_delimiters_string, c_string, c_string_player


def strtok_iteration(c_delimiters_string, c_string_player, c_string, libs):
    """
        Запуск одной итерации функции strtok игрока,
        и одной итерации функци strtok из стандартной билиотеки.
        Сравнение возвращаемых результатов этих функций.
    """

    player_ptr = libs["player"].strtok(c_string_player, c_delimiters_string)
    libary_ptr = libs["libary"].strtok(c_string, c_delimiters_string)

    player_ptr = ctypes.cast(player_ptr, ctypes.c_char_p)
    libary_ptr = ctypes.cast(libary_ptr, ctypes.c_char_p)
    error_code = check_strtok_correctness(player_ptr, libary_ptr)

    return error_code, libary_ptr


def strtok_time_counter(player_lib, bytes_string, delimiters, iterations):
    """
        Запуск strtok без проверки на корректность действий,
        для замеров времени.
    """

    def timeit_wrapper():
        """
            Обёртка для timeit.
        """

        player_lib.strtok(c_string_player, c_delimiters_string)
        for _ in range(iterations):
            player_lib.strtok(NULL, c_delimiters_string)

    run_time_info = []
    for _ in range(TIME_COUNTER_REPEATS):
        c_delimiters_string, _, c_string_player = \
            create_c_objects(bytes_string, delimiters.encode(ENCODING))

        run_time_info.append(Timer(timeit_wrapper, process_time_ns).timeit(TIMEIT_REPEATS))

    run_time_info.sort()
    median = run_time_info[TIMEIT_REPEATS // 2]

    avg_time = sum(run_time_info) / len(run_time_info)
    run_time_info = list(map(lambda x: (x - avg_time) * (x - avg_time), run_time_info))
    dispersion = sqrt(sum(run_time_info) / len(run_time_info))

    return median, dispersion


def run_strtok_test(delimiters, libs, test_data):
    """
        Запуск функций strtok, пока исходная строка не будет
        полностью уничтожена (функция strtok вернёт NULL).
    """

    bytes_string = test_data.encode(ENCODING)
    c_delimiters_string, c_string, c_string_player = \
        create_c_objects(bytes_string, delimiters.encode(ENCODING))

    error_code, std_ptr = \
        strtok_iteration(c_delimiters_string, c_string_player, c_string, libs)

    iterations = 0
    while std_ptr.value is not None and not error_code:
        error_code, std_ptr = strtok_iteration(c_delimiters_string, NULL, NULL, libs)
        iterations += 1

    run_time, dispersion = strtok_time_counter(libs["player"], bytes_string, delimiters, iterations)

    return run_time, error_code, dispersion


def start_strtok(player_lib, tests_path):
    """
        Открытие библиотек, запуск ранера, печать результатов.
    """

    lib_player = ctypes.CDLL(player_lib)
    libc = ctypes.CDLL("libc.so.6")
    libc.strtok.restype = ctypes.POINTER(ctypes.c_char)
    lib_player.strtok.restype = ctypes.POINTER(ctypes.c_char)
    libs = {"player": lib_player, "libary": libc}

    tests_correctness, total_time, dispersion = runner(
        tests_path,
        partial(run_strtok_test, DELIMITERS, libs)
    )

    print(
        "STRTOK TESTS:", "FAIL" if tests_correctness else "OK",
        "TIME:", total_time,
        "DISPERSION: ", dispersion
    )

    return tests_correctness, total_time, dispersion


if __name__ == "__main__":
    start_strtok("./strtok_lib.so", "tests/strtok")
