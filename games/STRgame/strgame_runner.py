import timeit, functools, ctypes
test_X = ctypes.CDLL("./test_strgame.so")


def run_tests():
    for i in range(100):
        f = open("test_" + str(i - i + 1) + ".txt",  "r+")
        time = run_split(str.encode(f.readline()))
        f.close()


def run_split(string):
    str = ctypes.create_string_buffer(string)
    string_buffers = [ctypes.create_string_buffer(9) for i in range(8)]
    pointers = (ctypes.c_char_p*8)(*map(ctypes.addressof, string_buffers))
    symb = ctypes.c_char(32)
    arr = []

    def timeit_wrapper(str, pointers, symb):
        size = test_X.split_test(str, pointers, symb)
        arr.append(size)

    run_time = timeit.Timer(functools.partial(timeit_wrapper, str, pointers,symb))
    time = run_time.timeit(1)
    print(arr)
    return time

    
if __name__ == "__main__":
    run_tests()
