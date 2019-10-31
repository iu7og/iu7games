"""
    char *strtok(char *string, const char *delim)
"""


import timeit, functools, ctypes
strtok_lib = ctypes.CDLL("./strtok_lib.so")
std_strtok_lib = ctypes.CDLL("./std_strtok.so")

NUMBER_OF_TESTS = 1
TEST_REPEAT = 1
ENCODING = "utf-8"

COMPARATORS = [' ', ',', '.', ';', ':']

def check_strtok_correctness(player_ptr, correct_ptr, ):
    pass


def concat_strings(f):
    """
        Склеивание каждой строки файла в одну единственную строку
        и удаление символов окончания строки.
    """

    return functools.reduce(lambda x, y: x + y[:-1], f)

def create_c_objects(bytes_string, comparators):
    c_comparators_string = ctypes.create_string_buffer(comparators)
    c_pointer = ctypes.c_char_p
    c_player_pointer = ctypes.c_char_p
    c_string = ctypes.create_string_buffer(bytes_string)
    c_string_player = ctypes.create_string_buffer(bytes_string)
    c_null_ptr = ctypes.POINTER(ctypes.c_char)()

    return c_comparators_string, c_pointer, c_player_pointer, c_string, c_string_player, c_null_ptr

#def strtok_wrapper():


def run_strtok(test_data, comparators):
    pointers_buffer = []
    strtok_ptr_not_null = False
    bytes_string = test_data.encode(ENCODING)
    total_time = 0

    c_comparators_string, c_pointer, c_player_pointer, \
        c_string, c_string_player, c_null_ptr = create_c_objects(bytes_string, comparator)

    def timeit_wrapper(c_pointer, c_comparators):
        pointers_buffer.append(strtok_lib.strtok(c_pointer, c_comparators_string))


    run_time = timeit.Timer(functools.partial(timeit_wrapper, c_string_player, c_comparators))
    total_time += run_time.timeit(TEST_REPEAT)
    c_pointer = std_strtok_lib.strtok(c_null_ptr, c_comparators_string)
    #check_strtok_correctness()

    while strtok_ptr_not_null:
        run_time = timeit.Timer(functools.partial(timeit_wrapper, c_null_ptr, c_comparators))
        total_time += run_time.timeit(TEST_REPEAT)

        try:
            c_pointer = pointers_buffer
            pointers_buffer.pop()
        except:
            strtok_ptr_not_null = True

        c_pointer = strtok_lib.std_strtok(c_null_ptr, c_comparators_string)
        #check_strtok_correctness()


    return total_time, 0

def main():
    """
        Открытие файлов с тестами и запуск strtok.
        Печатает количество успешных тестов и время ранинга.
    """

    total_time = 0
    total_tests = 0

    for i in range(NUMBER_OF_TESTS):
        f = open("test_strtok_" + str(i + 1) + ".txt",  "r")
        test_data = concat_strings(f)
        f.close()

        time, error_code = run_strtok(test_data, COMPARATORS)
        if not error_code:
            total_tests += 1
        total_time += time

    print("TESTS:", total_tests, "TIME:", total_time)


if __name__ == "__main__":
    main()
