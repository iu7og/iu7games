"""
      ===== SPLIT RUNNER v.1.2c =====
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
    - Функция НЕ должна ставить терминальный нуль в конце каждого разбитого слова.
"""


import ctypes
import gc
import time
import psutil
from timeit import Timer
from functools import partial
from time import process_time_ns
from math import sqrt
#from games.strgame.runner import runner
from runner import runner


OK = 0
INCORRECT_LEN = 1
INCORRECT_TEST = 2

ENCODING = "utf-8"
DELIMITER = ' '

WORDS_COUNT = 5300 * 20000
MAX_LEN_WORD = 17
TIMEIT_REPEATS = 11


def create_c_objects(bytes_string, delimiter):
    """
        Создание объектов для языка СИ, используемых функцией split
        1. c_string - массив символов (char *string)
        2. c_array_string - массив, содержащий массивы символов для получаемой матрицы
        3. c_array_pointer - массив указателей на эти строки (char **matrix)
        4. c_delimiter - символ-разделитель (const char symbol)
    """

    a = time.time()

    print(psutil.virtual_memory())
    print("START")
    c_string = ctypes.create_string_buffer(bytes_string)
    print(psutil.virtual_memory())
    c_array_strings = ctypes.create_string_buffer(b' ' * WORDS_COUNT * MAX_LEN_WORD)
    print(psutil.virtual_memory())
    test_lib = ctypes.CDLL("./test.so")
    c_array_pointer = (ctypes.c_char_p * WORDS_COUNT)()
    test_lib.filling_pointers_array(c_array_pointer, c_array_strings, ctypes.c_int(MAX_LEN_WORD), ctypes.c_int(WORDS_COUNT))
    c_delimiter = ctypes.c_wchar(delimiter)
    print("OFF", time.time() - a)

    return c_string, c_array_strings, c_array_pointer, c_delimiter


def check_split_correctness(player_size, player_strings_array, correct_strings_array):
    """
        Проверка корректности разбиения и возвращаемого
        значения тестируемой функции split.
    """

    #if player_size != len(correct_strings_array):
        #return INCORRECT_LEN

    a = psutil.virtual_memory()
    print(a[1], a)
    #k = 1000000

    k = a[1] // 100
    print(k)
    correct_strings_array = correct_strings_array.split(' ', k)
    print(psutil.virtual_memory())
    for i in range(WORDS_COUNT // k):
        print(psutil.virtual_memory())
        for j in range(k):
            if player_strings_array[k * i + j].decode(ENCODING) != correct_strings_array[j]:
                print(i)
                print(k * i + j)
                print(player_strings_array[j].decode(ENCODING))
                print(correct_strings_array[j])
                return INCORRECT_TEST

        del correct_strings_array[:k]
        correct_strings_array = correct_strings_array[0].split(' ', k)

    """
    for i in range(len(correct_strings_array)):
        if correct_strings_array[i] != player_strings_array[i].decode(ENCODING):
            return INCORRECT_TEST
    """

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
    print(run_time_info)

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

    bytes_string = test_data.encode(ENCODING)

    c_string, c_array_strings, c_array_pointer, c_delimiter = \
        create_c_objects(bytes_string, delimiter)

    print(psutil.virtual_memory())
    #exit(0)

    split_size = lib_player.split(c_string, c_array_pointer, c_delimiter)
    print(psutil.virtual_memory())
    del bytes_string

    error_code = 0
    error_code = check_split_correctness(
        split_size,
        c_array_pointer,
        test_data
    )
    print(psutil.virtual_memory())

    run_time, dispersion = split_time_counter(lib_player, c_string, c_array_pointer, c_delimiter)

    return run_time, error_code, dispersion


def start_split(player_lib, tests_dir):
    """
        Открытие файлов с тестами и запуск split.
        Печать количество успешных тестов и время ранинга.
    """

    a = psutil.virtual_memory()
    print(a)
    lib_player = ctypes.CDLL(player_lib)
    total_tests, total_time, dispersion = runner(
        tests_dir,
        partial(run_split_test, lib_player, DELIMITER)
    )

    print("SPLIT TESTS:", total_tests, "/ 1 TIME:", total_time, "DISPERSION:", dispersion)
    return total_tests, total_time, dispersion


if __name__ == "__main__":
    start_split("./split_lib.so", "tests/split")
