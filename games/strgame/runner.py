"""
      ===== SMART RUNNER v.1.2a =====
      Copyright (C) 2019 IU7Games Team.

    - В этом модуле расположена универсальная функция запуска
      тестирования функций как strtok, так и split.
"""

from functools import reduce
from psutil import virtual_memory

def print_memory_usage(stage):
    """
        Печать текущего состояния использования памяти
    """

    memory_usage = virtual_memory()
    print(
        "STAGE:", stage,
        "AVAILABLE MEMORY:", memory_usage[1],
        "USAGE PERCENTAGE:", memory_usage[2]
    )


def concat_strings(file):
    """
        Склеивание каждой строки файла в одну единственную строку,
        удаление символов окончания строки.
    """

    return reduce(lambda x, y: x + y[:-1], file)


def runner(tests_path, tests_runner):
    """
        Функция на вход принимает дирректорию путь к папке с тестами и
        функцию, запускающую тесты для strtok или split.
    """

    file = open(tests_path + "/test_data.txt", "r")
    test_data = concat_strings(file)
    file.close()

    time, error_code, dispersion = tests_runner(test_data)

    return error_code, time, dispersion
