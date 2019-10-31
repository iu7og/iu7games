"""
    Данный скрипт предназначен для тестирования самописной функции strtok,
    реализованной на СИ. Функция на СИ имеет сигнатуру:

    char *strtok(char *string, const char *delim)

    char *string - указатель на начало разбиваемой строки
    const char *delim - указатель на начало строки с разделителями

    Возвращаемое значение: указатель на следующий элемент
    после первого встреченного делителя.
    Функция должна полностью повторять поведение стандартного strtok c99.
"""


import timeit, functools, ctypes
player_strtok_lib = ctypes.CDLL("./strtok_lib.so")
std_strtok_lib = ctypes.CDLL("./std_strtok.so")

OK = 0
INVALID_PTR = 1

NUMBER_OF_TESTS = 1
TEST_REPEAT = 1
ENCODING = "utf-8"
NULL = 0

DELIMITERS = " ,.;:"

def check_strtok_correctness(player_ptr, correct_ptr):
    """
        Проверка корректности возвращаемого указателя
        из функции strtok, сравнение со стандартным поведением
        функции в СИ.
    """

    if not player_ptr and correct_ptr:
        return INVALID_PTR

    if player_ptr.value != None:
        if player_ptr.value.decode(ENCODING) != correct_ptr.value.decode(ENCODING):
            return INVALID_PTR

    return OK


def concat_strings(f):
    """
        Склеивание каждой строки файла в одну единственную строку
        и удаление символов окончания строки.
    """

    return functools.reduce(lambda x, y: x + y[:-1], f)


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


def strtok_run_iteration(c_delimiters_string, c_string_player, c_string):
    """
        Запуск одной итерации функции strtok игрока,
        и одной итерации функци strtok из стандартной билиотеки.
        Сравнение возвращаемых результатов этих функций.
        Замеры времени ранинга с помощью timeit.
    """

    pointer_buffer = []

    def timeit_wrapper(c_pointer, c_delimiters):
        pointer_buffer.append(player_strtok_lib.strtok(c_pointer, c_delimiters))

    run_time = timeit.Timer(functools.partial(timeit_wrapper, c_string_player, c_delimiters_string))
    time = run_time.timeit(TEST_REPEAT)

    std_ptr = std_strtok_lib.strtok(c_string, c_delimiters_string)
    player_ptr = pointer_buffer[0]

    error_code = check_strtok_correctness(ctypes.cast(player_ptr, ctypes.c_char_p), \
        ctypes.cast(std_ptr, ctypes.c_char_p))

    return time, error_code, ctypes.cast(std_ptr, ctypes.c_char_p)


def run_strtok(test_data, delimiters):
    """
        Запуск функций strtok, пока исходная строка не будет
        полностью уничтожена (ф-я вернёт NULL).
    """

    bytes_string = test_data.encode(ENCODING)
    c_delimiters_string, c_string, c_string_player = \
        create_c_objects(bytes_string, delimiters.encode(ENCODING))

    total_time, error_code, std_ptr = strtok_run_iteration(c_delimiters_string, c_string_player, c_string)
    while std_ptr.value != None and not error_code:
        time, error_code, std_ptr = strtok_run_iteration(c_delimiters_string, NULL, NULL)
        total_time += time

    return total_time, error_code


def main():
    """
        Открытие файлов с тестами и запуск strtok.
        Печать количества успешных тестов и время ранинга.
    """

    total_time = 0
    total_tests = 0

    for i in range(NUMBER_OF_TESTS):
        f = open("test_" + str(i + 1) + ".txt",  "r")
        test_data = concat_strings(f)
        f.close()

        time, error_code = run_strtok(test_data, DELIMITERS)
        if not error_code:
            total_tests += 1
        total_time += time

    print("TESTS:", total_tests, "TIME:", total_time)


if __name__ == "__main__":
    main()
