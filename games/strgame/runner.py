"""
    В этом модуле расположена универсальная функция запуска
    тестов как для strtok, так и split.
"""

from functools import reduce

TESTS_REPEATS = 100
NUMBER_OF_TESTS = 20

def concat_strings(file):
    """
        Склеивание каждой строки файла в одну единственную строку,
        удаление символов окончания строки.
    """

    return reduce(lambda x, y: x + y[:-1], file)


def runner(args_tests, tests_runner, delims=None):
    """
        Функция на вход принимает дирректорию папку с тестами,
        функцию, запускающую тесты для strtok или split.
        У deilms есть дефолтное значение, в случае
        если этот аргумент не передан (в strtok он не нужен)
        Суть функции: загружает файлы с тестами и запускает их.
    """

    total_time = 0
    total_tests = 0

    for i in range(TESTS_REPEATS):
        file = open(args_tests + "/test_" + str((i % NUMBER_OF_TESTS) + 1) + ".txt", "r")
        test_data = concat_strings(file)
        file.close()

        if delims is not None:
            time, error_code = tests_runner(test_data, delims[i % NUMBER_OF_TESTS])
        else:
            time, error_code = tests_runner(test_data)

        if not error_code:
            total_tests += 1
        total_time += time

    return total_tests, total_time
