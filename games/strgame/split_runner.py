"""
    split runner v.1.1

    Данный скрипт предназначен для тестирования самописной функции split,
    реализованной на СИ. Функция на СИ имеет сигнатуру:

    int split(const char *string, char **matrix, const char symbol)

    const char *string - указатель на начало разбиваемой строки (строка)
    char **matrix - указатель на массив указателей, который в свою очередь
    указывает на разбиваемые сплитом строки (матрица)
    const char symbol - делитель для разбиваемой строки

    Возвращаемое значение: длина массива строк (кол-во строк в matrix)
    Функция должна полностью повторяет поведение одноименной функции в Python 3.X,
    за исключением того, что делителей не может быть несколько.
"""


import timeit
import ctypes
from functools import partial
from games.strgame.runner import runner

OK = 0
INCORRECT_LEN = 1
INCORRECT_TEST = 2

TIMEIT_REPEAT = 1
ENCODING = "utf-8"
ARRAY_SIZE = 32000

DELIMITERS = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ',', \
    '1', '0', '-', 'X', '!', '?', '.', ';', 'N']


def create_c_objects(bytes_string, delimiter):
    """
        Создание объектов для языка СИ, используемых функцией split
        1. c_string - массив символов (char *string)
        2. c_array_string - массив, содержащий массивы символов для получаемой матрицы
        3. c_array_pointer - массив указателей на эти строки (char **matrix)
        4. c_delimiter - символ-разделитель (const char symbol)
    """

    c_string = ctypes.create_string_buffer(bytes_string)
    c_array_strings = [ctypes.create_string_buffer(ARRAY_SIZE) for i in range(ARRAY_SIZE)]
    c_array_pointer = (ctypes.c_char_p * ARRAY_SIZE)(*map(ctypes.addressof, c_array_strings))
    c_delimiter = ctypes.c_wchar(delimiter)

    return c_string, c_array_strings, c_array_pointer, c_delimiter


def check_split_correctness(player_size, player_strings_array, correct_strings_array):
    """
        Проверка корректности разбиения и возвращаемого
        значения тестируемой функции split.
    """

    if player_size != len(correct_strings_array):
        return INCORRECT_LEN

    for string in correct_strings_array:
        if string != player_strings_array[0].value.decode(ENCODING):
            return INCORRECT_TEST

        player_strings_array.pop(0)

    return OK


def run_split_test(lib_player, test_data, delimiter):
    """
        Вызов функций split, сравнения поведения функции
        из Python и функции игрока (СИ).
        Замеры времени ранинга с помощью timeit.
    """

    size_buffer = []
    correct_strings_array = test_data.split(delimiter)
    bytes_string = test_data.encode(ENCODING)

    c_string, c_array_strings, c_array_pointer, c_delimiter = \
        create_c_objects(bytes_string, delimiter)

    def timeit_wrapper(string, matrix, delimiter):
        """
            Обёртка для timeit, для сохранения возвращаемого split значения
        """
        size_buffer.append(lib_player.split(string, matrix, delimiter))


    run_time = \
        timeit.Timer(partial(timeit_wrapper, c_string, c_array_pointer, c_delimiter))
    time = run_time.timeit(TIMEIT_REPEAT)

    error_code = check_split_correctness(size_buffer[0], c_array_strings, correct_strings_array)
    return time, error_code


def start_split(player_lib, tests_dir):
    """
        Открытие файлов с тестами и запуск split.
        Печать количество успешных тестов и время ранинга.
    """

    lib_player = ctypes.CDLL(player_lib)
    total_tests, total_time = runner(
        tests_dir,
        partial(run_split_test, lib_player),
        DELIMITERS
    )

    print("SPLIT TESTS:", total_tests, "/ 100 TIME:", total_time)
    return total_tests, total_time


if __name__ == "__main__":
    start_split("./split_lib.so", "./split_tests")
