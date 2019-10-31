import timeit, functools, ctypes
test_X = ctypes.CDLL("./test_strgame.so")


def run_tests():
    for i in range(1):
        f = open("test_" + str(i - i + 1) + ".txt",  "r+")
        k = 0
        buff = ""
        for line in f:
            buff += line[:-1]
        time = run_split(str.encode(buff))
        f.close()


def run_split(string):
    test = string.decode('utf-8')
    #print(test)
    #print(test.split())
    #return
    n = 32000
    str = ctypes.create_string_buffer(string)
    string_buffers = [ctypes.create_string_buffer(n) for i in range(n)]
    pointers = (ctypes.c_char_p*n)(*map(ctypes.addressof, string_buffers))
    symb = ctypes.c_char(32)
    arr = []

    def timeit_wrapper(str, pointers, symb):
        size = test_X.split_test(str, pointers, symb)
        arr.append(size)

    run_time = timeit.Timer(functools.partial(timeit_wrapper, str, pointers,symb))
    time = run_time.timeit(1)
    string = string.decode('utf-8')
    string_arr = string.split(' ')

    print(arr[0])
    print(len(string_arr))
    if (arr[0] != len(string_arr)):
        print("INVALID LEN")
    k = 0

    for i in range(len(string_arr)):
        string_buffers[i] = string_buffers[i].value.decode('utf-8')
        #print(string_buffers[i], string_arr[i])
        if string_buffers[i] == string_arr[i]:
            k += 1
        else:
            print("C: ", string_buffers[i], "PYTHON: ", string_arr[i])
            print("INVALID ", i)
            break
    if (k == len(string_arr)):
        print("TEST CORRECT")

    return time


if __name__ == "__main__":
    run_tests()
