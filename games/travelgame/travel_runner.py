"""
    ===== TR4V31 RUNNER v.1.3b =====

    Copyright (C) 2019 - 2020 IU7Games Team.

    - Ранер для игры TR4V31GAME, суть которой заключается в нахождении всех рейсов,
    совершенных из аэропорта origin в аэропорт destination, в указанный месяц и день.

    - В соревновании принимают участие функции, имеющие следующую сигнатуру:
    - int travel_game(int **result, const FILE *const flights, const flight route)

    - Структура flight:
      typedef struct
      {
          const char origin[4];
          const char destination[4];
          const int month;
          const int day;
      } flight;

    - Функция должна возвращать int-значение, равное количеству найденных рейсов
"""

import ctypes
from random import randint
from timeit import Timer
from time import process_time_ns
import games.utils.utils as utils

TIMEIT_REPEATS = 100000

MAX_LEN_AIRPORTS_NAME = 4
MAX_COUNT_FLIGHTS = 86395

TESTS_PATH = "games/travelgame/tests"
FILE_FLIGHTS = "/flights.csv"

SAMPLE_PATH = utils.MEMORY_LEAK_SAMPLE_PATH + "/travelgame.c"


class Flight(ctypes.Structure):
    """
        Класс Flight описывает структуру flight в C.
        Класс имеет поля:
        1. origin - идентфикатор аэропорта, откуда самолет вылетел -
                 const char origin[4]
        2. destination - идентификатор аэропорта, куда самолет прилетел -
                 const char destination[4]
        3. month - месяц вылета -  const int month
        4. day - день вылета -  const int month
    """

    _fields_ = [("origin", ctypes.c_char * MAX_LEN_AIRPORTS_NAME),
                ("destination", ctypes.c_char * MAX_LEN_AIRPORTS_NAME),
                ("month", ctypes.c_int),
                ("day", ctypes.c_int)]

    def __init__(self, test_data):
        """
            Конструктор для класса Flight.
        """
        super(Flight, self).__init__()
        self.origin = test_data["origin"].encode(utils.ENCODING)
        self.destination = test_data["destination"].encode(utils.ENCODING)
        self.month = int(test_data["month"])
        self.day = int(test_data["day"])


def init_string(string):
    """
        Инициализация строки.
    """

    bytes_string = string.encode(utils.ENCODING)
    c_string = ctypes.create_string_buffer(bytes_string)

    return c_string


def create_test(file_flights):
    """
        Создание тестовых данных.
    """
    random_flight = randint(1, MAX_COUNT_FLIGHTS)

    for i, line in enumerate(file_flights):
        if i == random_flight:
            month = line.split(',')[0]
            day = line.split(',')[1]
            airport_from = line.split(',')[2]
            airport_to = line.split(',')[3]

    return {"origin": airport_from, "destination": airport_to, "month": month, "day": day}


def solution(file_flights, test_data):
    """
       Поиск рейсов, совершенных из аэропорта from в аэропорт to
       в указанный день и месяц.
    """
    flights = []

    for line in file_flights:
        flight = line.strip().split(',')
        if (flight[2], flight[3]) == (test_data["origin"], test_data["destination"]) \
                and (flight[0], flight[1]) == (str(test_data["month"]), str(test_data["day"])):
            flights.append(int(flight[4]))

    return flights


def print_conditions(test_data, array_flights):
    """
       Печать условий раунда.
    """
    print(
        "GAME CONDITIONS\n" +
        f'ORIGIN: {test_data["origin"]}\n' +
        f'DESTINATION: {test_data["destination"]}\n' +
        f'MONTH: {test_data["month"]}\n' +
        f'DAY: {test_data["day"]}\n' +
        f'SOLUTION: {array_flights}'
    )


def ctypes_wrapper(player_lib, move, c_pointer, file_pointer, route):
    """
       Обёртка для отловки segmentation fault.
    """
    player_lib.travel_game.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
                                       ctypes.c_void_p, Flight]
    player_lib.travel_game.restype = ctypes.c_int

    move.value = player_lib.travel_game(c_pointer, file_pointer, route)


def check_segfault(count):
    """
       Проверка значения на segfault.
    """

    if count == utils.SEGFAULT:
        print("This player caused segmentation fault.")
        return True

    return False


def check_flights(player_count, c_pointer, array_flights, count_flights):
    """
       Проверка полученных игроком рейсов.
    """

    if player_count != count_flights:
        return utils.SOLUTION_FAIL

    flights = (ctypes.c_int * count_flights)()

    for i in range(count_flights):
        flights[i] = array_flights[i]

    for i in range(count_flights):
        equal = 0
        for j in range(count_flights):
            if flights[i] == c_pointer[j]:
                equal = 1
                break

        if equal == 0:
            return utils.SOLUTION_FAIL

    return utils.OK


def player_results(lib_path, c_pointer, file_pointer, route, array_flights, free, rewind):
    """
       Получение и обработка результатов игрока.
       Подсчет времени выполнения функции игрока
    """
    player_lib = ctypes.CDLL(lib_path)
    player_lib.travel_game.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
                                       ctypes.c_void_p, Flight]
    player_lib.travel_game.restype = ctypes.c_int

    player_count = utils.call_libary(
        player_lib, ctypes_wrapper, 'i', utils.SEGFAULT, c_pointer, file_pointer, route)

    if check_segfault(player_count):
        free(c_pointer)
        return (utils.SEGFAULT, 0, 0)

    rewind(file_pointer)

    player_count = player_lib.travel_game(c_pointer, file_pointer, route)
    error_code = check_flights(
        player_count, c_pointer, array_flights, len(array_flights))

    if error_code != utils.OK:
        free(c_pointer)
        return (utils.SOLUTION_FAIL, 0, 0)

    memory_leak_check_res = utils.memory_leak_check(
        SAMPLE_PATH, lib_path,
        [
            TESTS_PATH + FILE_FLIGHTS,
            str(route.origin, utils.ENCODING),
            str(route.destination, utils.ENCODING),
            str(route.month), str(route.day)
        ]
    )
    if memory_leak_check_res:
        return (
            utils.MEMORY_LEAK if memory_leak_check_res > 0
            else utils.MEMORY_LEAK_CHECK_ERROR, 0, 0
        )

    def timeit_wrapper():
        """
           Обертка для Timeit.
        """
        rewind(file_pointer)
        player_lib.travel_game(c_pointer, file_pointer, route)

    time_results = Timer(timeit_wrapper, process_time_ns).repeat(
        TIMEIT_REPEATS, 1)
    free(c_pointer)

    median, dispersion = utils.process_time(time_results)

    return (utils.OK, median, dispersion)


def get_c_functions():
    """
        Подключение стандартных функций из lib.so
    """

    libc = ctypes.CDLL("libc.so.6")

    fopen = libc.fopen
    fopen.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    fopen.restype = ctypes.c_void_p

    rewind = libc.rewind
    rewind.argtypes = [ctypes.c_void_p]
    rewind.restype = None

    fclose = libc.fclose
    fclose.argtypes = [ctypes.c_void_p]
    fclose.restype = ctypes.c_int

    free = libc.free
    free.argtypes = [ctypes.c_void_p]
    free.restype = ctypes.c_void_p

    return fopen, rewind, fclose, free


def start_travel_game(players_info):
    """
       Открытие библиотеки с функциями игроков.
       Подсчет времени выполнения их функций.
       Получение результатов.
    """
    utils.redirect_ctypes_stdout()

    with open(TESTS_PATH + FILE_FLIGHTS, "r") as file_flights:
        test_data = create_test(file_flights)
        file_flights.seek(0)
        array_flights = solution(file_flights, test_data)

    print_conditions(test_data, array_flights)

    fopen, rewind, fclose, free = get_c_functions()

    mode = init_string("r")
    file_name = init_string(TESTS_PATH + FILE_FLIGHTS)

    c_pointer = ctypes.POINTER(ctypes.c_int)()
    file_pointer = fopen(file_name, mode)
    route = Flight(test_data)

    results = []

    for player_lib in players_info:
        if player_lib == "NULL":
            results.append((utils.NO_RESULT, 0, 0))
            continue

        rewind(file_pointer)

        results.append(
            player_results(player_lib, c_pointer, file_pointer, route,
                           array_flights, free, rewind)
        )

    fclose(file_pointer)

    utils.print_results(results, players_info)

    return results


if __name__ == "__main__":
    start_travel_game(["games/travelgame/test.so", "NULL",
                       "games/travelgame/test.so"])
