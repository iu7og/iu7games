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
    return functools.reduce(lambda x, y: x + y[:-1], f)


def create_c_objects(bytes_string, comparator):
    c_string = ctypes.create_string_buffer(bytes_string)
    c_array_strings = [ctypes.create_string_buffer(ARRAY_SIZE) for i in range(ARRAY_SIZE)]
    c_array_pointer = (ctypes.c_char_p * ARRAY_SIZE)(*map(ctypes.addressof, c_array_strings))
    c_comparator = ctypes.c_wchar(comparator)

    return c_string, c_array_strings, c_array_pointer, c_comparator


def check_split_correctness(player_size, player_strings_array, correct_strings_array):
    if (player_size != len(correct_strings_array)):
        return INCORRECT_LEN

    for i in range(len(correct_strings_array)):
        if (player_strings_array[i].value).decode(ENCODING) != correct_strings_array[i]:
            return INCORRECT_TEST

    return OK


def run_split(test_data, comparator):
    size_buffer = []
    correct_strings_array = test_data.split(comparator)
    bytes_string = test_data.encode(ENCODING)

    c_string, c_array_strings, c_array_pointer, c_comparator = create_c_objects(bytes_string, comparator)

    def timeit_wrapper(string, matrix, comparator):
        size_buffer.append(split_lib.split_test(string, matrix, comparator))


    run_time = timeit.Timer(functools.partial(timeit_wrapper, c_string, c_array_pointer, c_comparator))
    time = run_time.timeit(TEST_REPEAT)

    error_code = check_split_correctness(size_buffer[0], c_array_strings, correct_strings_array)
    return time, error_code


def run_tests():
    for i in range(NUMBER_OF_TESTS):
        f = open("test_" + str(i - i + 1) + ".txt",  "r")
        test_data = concat_strings(f)
        time, error_code = run_split(test_data, COMPARATORS[i])
        print(error_code, time)
        f.close()


if __name__ == "__main__":
    run_tests()
