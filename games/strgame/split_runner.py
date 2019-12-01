"""
      ===== SPLIT RUNNER v.1.3a =====
      Copyright (C) 2019 IU7Games Team.

    - Данный скрипт предназначен для тестирования самописной функции split,
    - реализованной на СИ. Функция на СИ имеет сигнатуру:

    - int split(const char *string, char **matrix, const char symbol)

    - const char *string - указатель на начало разбиваемой строки (строка)
    - char **matrix - указатель на массив указателей, который в свою очередь
      указывает на разбиваемые сплитом строки (матрица)
    - const char symbol - делитель для разбиваемой строки

    - Возвращаемое значение: длина массива строк (кол-во строк в matrix)
    - Функция должна полностью повторяет поведение одноименной функции в Python 3.X,
      за исключением того, что делителей не может быть несколько.
"""


import ctypes
from functools import partial
from time import process_time_ns
from math import sqrt
from timeit import Timer
from psutil import virtual_memory
from games.strgame.runner import runner
#from runner import runner


OK = 0
INCORRECT_LEN = 1
INCORRECT_TEST = 2

ENCODING = "utf-8"
DELIMITER = ' '

STRING_MULTIPLIER = 1000
WORDS_COUNT = 5400 * STRING_MULTIPLIER
MAX_LEN_WORD = 17
TIMEIT_REPEATS = 11
MEMORY_RATIO = 100


def create_c_objects(bytes_string, delimiter):
    """
        Создание объектов для языка СИ, используемых функцией split
        1. c_string - массив символов (char *string)
        2. c_array_string - массив, содержащий массивы символов для получаемой матрицы
        3. c_array_pointer - массив указателей на эти строки (char **matrix)
        4. c_delimiter - символ-разделитель (const char symbol)
    """

    c_string = ctypes.create_string_buffer(bytes_string)
    c_array_strings = ctypes.create_string_buffer(b' ' * WORDS_COUNT * MAX_LEN_WORD)
    filling_lib = ctypes.CDLL("filling.so")
    c_array_pointer = (ctypes.c_char_p * WORDS_COUNT)()

    filling_lib.filling_pointers_array(
        c_array_pointer,
        c_array_strings,
        ctypes.c_int(MAX_LEN_WORD),
        ctypes.c_int(WORDS_COUNT)
    )

    c_delimiter = ctypes.c_wchar(delimiter)

    return c_string, c_array_strings, c_array_pointer, c_delimiter


def check_split_correctness(player_size, player_string_array, correct_string_array):
    """
        Проверка корректности разбиения и возвращаемого
        значения тестируемой функции split.
    """

    correct_string_array.pop()
    correct_size = len(correct_string_array)

    if correct_size * STRING_MULTIPLIER != player_size:
        return INCORRECT_TEST

    split_comparator = ctypes.CDLL("./split_comparator.so")
    split_string_array = (ctypes.c_char_p * correct_size)()
    split_string_array[:] = list(map(lambda str: str.encode(ENCODING), correct_string_array))

    error_code = split_comparator.check_correctness(
        player_string_array,
        split_string_array,
        ctypes.c_int(correct_size),
        ctypes.c_int(STRING_MULTIPLIER)
    )

    if error_code != OK:
        return INCORRECT_TEST

    return OK


def split_time_counter(lib_player, c_string, c_array_pointer, c_delimiter):
    """
        Запуск split без проверки на корректность действий,
        для замеров времени. Подсчёт медианы и среднеквадр. отклонения.
    """

    def timeit_wrapper():
        """
            Обёртка для timeit.
        """

        lib_player.split(c_string, c_array_pointer, c_delimiter)

    run_time_info = Timer(timeit_wrapper, process_time_ns).repeat(TIMEIT_REPEATS, 1)
    run_time_info.sort()

    median = run_time_info[TIMEIT_REPEATS // 2]
    avg_time = sum(run_time_info) / len(run_time_info)
    run_time_info = list(map(lambda x: (x - avg_time) * (x - avg_time), run_time_info))
    dispersion = sqrt(sum(run_time_info) / len(run_time_info))

    return median, dispersion


def run_split_test(lib_player, delimiter, test_data):
    """
        Вызов функций split, сравнения поведения функции
        из Python и функции игрока реализованной в СИ.
        Замеры времени.
    """

    correct_split = test_data.split(delimiter)
    test_data *= STRING_MULTIPLIER
    test_data = test_data[:len(test_data) - 1]
    bytes_string = test_data.encode(ENCODING)

    c_string, _, c_array_pointer, c_delim = create_c_objects(bytes_string, delimiter)
    print("MEMORY USAGE AT END: ", virtual_memory())

    player_size = lib_player.split(c_string, c_array_pointer, c_delim)
    error_code = check_split_correctness(
        player_size,
        c_array_pointer,
        correct_split
    )

    if error_code == OK:
        run_time, dispersion = split_time_counter(lib_player, c_string, c_array_pointer, c_delim)
    else:
        run_time, dispersion = 0.0, 0.0

    return run_time, error_code, dispersion


def start_split(player_lib, tests_path):
    """
        Открытие файлов с тестами и запуск split.
        Печать количество успешных тестов и время ранинга.
    """

    print("MEMORY USAGE AT START:", virtual_memory())
    lib_player = ctypes.CDLL(player_lib)
    tests_correctness, total_time, dispersion = runner(
        tests_path,
        partial(run_split_test, lib_player, DELIMITER)
    )

    print(
        "SPLIT TESTS:", "FAIL" if tests_correctness else "OK",
        "TIME:", total_time,
        "DISPERSION:", dispersion
    )

    return tests_correctness, total_time, dispersion


if __name__ == "__main__":
    start_split("./split_lib.so", "tests/split")
