"""
    Данный скрипт предназначен для тестирования самописной функции split,
    реализованной на СИ. Функция на СИ имеет сигнатуру:

    int split(const char *string, char **matrix, const char symbol)

    const char *string - указатель на начало разбиваемой строки (строка)
    char **matrix - указатель на массив указателей, который в свою очередь
    указывает на разбиваемые сплитом строки (матрица)
    const char symbol - компаратор для разбиваемой строки

    Возвращаемое значение: длина массива строк (matrix)
    Функция должна полностью повторяет поведение одноименной функции в Python 3.X,
    за исключением того, что, компараторов не может быть несколько.
"""


import timeit, functools, ctypes
split_lib = ctypes.CDLL("./split_lib.so")

OK = 0
INCORRECT_LEN = 1
INCORRECT_TEST = 2

NUMBER_OF_TESTS = 1
TEST_REPEAT = 1
ENCODING = "utf-8"
ARRAY_SIZE = 32000

COMPARATORS = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ',', \
    '1', '0', '-', 'X', '!', '?', '.', ';', 'N']


def concat_strings(f):
    """
        Склеивание каждой строки файла в одну единственную строку
        и удаление символов окончания строки.
    """

    return functools.reduce(lambda x, y: x + y[:-1], f)


def create_c_objects(bytes_string, comparator):
    """
        Создание объектов для языка СИ, используемых функцией split
        1. c_string - массив символов (char *string)
        2. c_array_string - массив, содержащий массивы символов для получаемой матрицы
        3. c_array_pointer - массив указателей на эти строки (char **matrix)
        4. c_comparator - символ-компаратор (chat symbol)
    """

    c_string = ctypes.create_string_buffer(bytes_string)
    c_array_strings = [ctypes.create_string_buffer(ARRAY_SIZE) for i in range(ARRAY_SIZE)]
    c_array_pointer = (ctypes.c_char_p * ARRAY_SIZE)(*map(ctypes.addressof, c_array_strings))
    c_comparator = ctypes.c_wchar(comparator)

    return c_string, c_array_strings, c_array_pointer, c_comparator


def check_split_correctness(player_size, player_strings_array, correct_strings_array):
    """
        Проверка корректности разбиения и возвращаемого
        значения тестируемой функции split.
    """

    if (player_size != len(correct_strings_array)):
        return INCORRECT_LEN

    for i in range(len(correct_strings_array)):
        if (player_strings_array[i].value).decode(ENCODING) != correct_strings_array[i]:
            return INCORRECT_TEST

    return OK


def run_split(test_data, comparator):
    """
        Вызов функции split прямо из СИ,
        замеры времени ее ранинга с помощью timeit и ее тестирование.
    """

    size_buffer = []
    correct_strings_array = test_data.split(comparator)
    bytes_string = test_data.encode(ENCODING)

    c_string, c_array_strings, c_array_pointer, c_comparator = create_c_objects(bytes_string, comparator)

    def timeit_wrapper(string, matrix, comparator):
        """
            Обёртка для timeit, для сохранения возвращаемого split значения
        """
        size_buffer.append(split_lib.split_test(string, matrix, comparator))


    run_time = timeit.Timer(functools.partial(timeit_wrapper, c_string, c_array_pointer, c_comparator))
    time = run_time.timeit(TEST_REPEAT)

    error_code = check_split_correctness(size_buffer[0], c_array_strings, correct_strings_array)
    return time, error_code



def main():
    """
        Открытие файлов с тестами и запуск split.
        Печатает количество успешных тестов и время ранинга.
    """

    total_time = 0
    total_tests = 0

    for i in range(NUMBER_OF_TESTS):
        f = open("test_" + str(i + 1) + ".txt",  "r")
        test_data = concat_strings(f)
        f.close()

        time, error_code = run_split(test_data, COMPARATORS[i])
        if not error_code:
            total_tests += 1
        total_time += time

    print("TESTS:", total_tests, "TIME:", total_time)


if __name__ == "__main__":
    main()
