"""
          ===== RUNNERS UTILS v.1.0b =====
          Copyright (C) 2019 - 2020 IU7Games Team.

        - Модуль с функциями и константами, которые вызываются в нескольких ранерах.
"""


import sys
import os
import subprocess
from statistics import median, pvariance
from functools import reduce
from multiprocessing import Process, Value
from psutil import virtual_memory

OK = 0
SOLUTION_FAIL = 1
INVALID_PTR = 1
NO_RESULT = -1337
SEGFAULT = -1
CHAR_SEGFAULT = '0'
PTR_SEGF = '0'

ENCODING = "utf-8"
TEST_FILE = "/test_data.txt"

STRTOK_DELIMITERS = " ,.;:"
SPLIT_DELIMITER = ' '
NULL = 0


def call_libary(player_lib, wrapper, argtype, stdval, *args):
    """
        Вызов функции игрока с помощью multiprocessing, для отловки segfault.
    """

    move = Value(argtype, stdval)
    proc = Process(target=wrapper, args=(player_lib, move, *args))
    proc.start()
    proc.join()

    return move.value


def print_memory_usage(stage):
    """
        Печать текущего состояния использования памяти
    """

    memory_usage = virtual_memory()

    print(
        f"STAGE: {stage} "
        f"AVAILABLE MEMORY: {memory_usage[1]} "
        f"USAGE PERCENTAGE: {memory_usage[2]}"
    )


def memory_leak_check(sample_path, lib_path, sample_args):
    """
        Проверка наличия утечек памяти через valgrind

        sample_path - полный путь до тестовой программы
        lib_path - полный путь до тестируемой библиотеки
        sample_args - аргументы запуска тестовой программы

        Возвращаемое значение - кол-во утечек
    """

    executable = './memory_leak_check.out'
    subprocess.run(
        [
            'gcc',
            '--std=c99',
            '-O3',
            sample_path,
            lib_path,
            '-o',
            executable
        ],
        check=True
    )

    process = subprocess.Popen(
        [
            'valgrind',
            '--quiet',
            '--verbose',
            '--leak-check=full',
            '--show-leak-kinds=all',
            '--track-origins=yes',
            '--error-exitcode=1',
            executable
        ] + sample_args,
        stderr=subprocess.PIPE
    )

    check_res = process.wait() == 0

    subprocess.run(['rm', executable], check=True)

    return 0 if check_res else int(next(
        filter(
            lambda x: x.isdigit(),
            process.stderr.readlines()[-1].split()
        )
    ).decode('utf-8'))


def redirect_ctypes_stdout():
    """
        Выключение принтов в стратегиях игроков.
    """

    new_stdout = os.dup(1)
    sys.stdout.flush()
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)
    os.close(devnull)
    sys.stdout = os.fdopen(new_stdout, 'w')


def process_time(time_results):
    """
        Обработка результатов (по времени) игрока. Подсчёт медианы и дисперсии.
    """

    return median(time_results), pvariance(time_results)


def parsing_name(lib_path):
    """
        Преобразование полного пути к файлу с библиотекой игрока
        к gitlab логину игрока.
    """
    return lib_path[lib_path.rindex('/') + 1: len(lib_path) - 3]


def print_strgame_results(game, incorrect_test, total_time, dispersion):
    """
        Печать результатов для STRGAME.
    """

    print(
        f"{game} TESTS: {'FAIL' if incorrect_test else 'OK'} "
        f"TIME: {total_time} "
        f"DISPERSION: {dispersion}"
    )


def print_results(results, players_info):
    """
        Печать финальных результатов для каждого игрока.
    """

    for player, result in zip(players_info, results):
        if player != "NULL":
            print(
                f"PLAYER: {parsing_name(player)} ",
                f"SOLUTION: {'FAIL' if result[0] else 'OK'} ",
                f"MEDIAN: {result[1]} ",
                f"DISPERSION: {result[2]}"
            )


def concat_strings(f_obj):
    """
        Склеивание каждой строки файла в одну единственную строку,
        удаление символов окончания строки.
    """

    return reduce(lambda x, y: x + y[:-1], f_obj)


def strgame_runner(tests_path, tests_runner):
    """
        Универсальная функция, производящая запуск STR игр (split, strtok)
    """

    with open(tests_path + TEST_FILE, "r") as f_obj:
        test_data = concat_strings(f_obj)

    time, error_code, dispersion = tests_runner(test_data)

    return error_code, time, dispersion
