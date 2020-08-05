"""
    ===== TR4V31 RUNNER v.1.2b =====

    Copyright (C) 2019 - 2020 IU7Games Team.

    - Ранер для игры TR4V31GAME, суть которой заключается в нахождении всех рейсов,
    совершенных из аэропорта _from в аэропорт _to, в указанный месяц и день.

    - В соревновании принимают участие функции, имеющие следующую сигнатуру:
    - int travel_game(int **result, const FILE *const flights, const flight route)

    - Структура flight:
      typedef struct
      {
          const char _from[4];
          const char _to[4];
          const int month;
          const int day;
      } flight;

    - Функция должна возвращать int-значение, равное количеству найденных рейсов
"""

import ctypes
from random import randint, choice
from timeit import Timer
from time import process_time_ns
import games.utils.utils as utils

TIMEIT_REPEATS = 1000

MAX_LEN_AIRPORTS_NAME = 4
MAX_COUNT_AIRPORTS = 322

COUNT_MONTH = 12
COUNT_DAY = 31

FILE_AIRPORTS = "/airports.csv"
FILE_FLIGHTS = "/flights.csv"


class Flight(ctypes.Structure):
    """
        Класс Flight описывает структуру flight в C.
        Класс имеет поля:
        1. _from - идентфикатор аэропорта, откуда самолет вылетел -
                 const char _from[4]
        2. _to - идентификатор аэропорта, куда самолет прилетел -
                 const char _to[4]
        3. month - месяц вылета -  const int month
        4. day - день вылета -  const int month
    """

    _fields_ = [("_from", ctypes.c_char * MAX_LEN_AIRPORTS_NAME),
                ("_to", ctypes.c_char * MAX_LEN_AIRPORTS_NAME),
                ("month", ctypes.c_int),
                ("day", ctypes.c_int)]

    def __init__(self, test_data):
        """
            Конструктор для класса Flight.
        """

        self._from = test_data["from"].encode(utils.ENCODING)
        self._to = test_data["to"].encode(utils.ENCODING)
        self.month = test_data["month"]
        self.day = test_data["day"]


def init_string(string):
    """
        Инициализация строки.
    """

    bytes_string = string.encode(utils.ENCODING)
    c_string = ctypes.create_string_buffer(bytes_string)

    return c_string


def create_test(file_airports):
    """
        Создание тестовых данных.
    """
    line_from = randint(1, MAX_COUNT_AIRPORTS)
    line_to = choice(list(range(1, line_from)) + list(range(line_from + 1, MAX_COUNT_AIRPORTS + 1)))

    for i, line in enumerate(file_airports):
        if i == line_from:
            airport_from = line.split(',')[0]
        elif i == line_to:
            airport_to = line.split(',')[0]

    month = randint(1, COUNT_MONTH)
    day = randint(1, COUNT_DAY)

    return {"from" : airport_from, "to" : airport_to, "month" : month, "day" : day}


def solution(file_flights, test_data):
    """
       Поиск рейсов, совершенных из аэропорта from в аэропорт to
       в указанный день и месяц.
    """
    flights = []

    for line in file_flights:
        info_flight = line.split(',')
        if info_flight[7] == test_data["from"] and info_flight[8] == test_data["to"] \
                and info_flight[1] == str(test_data["month"]) \
                     and info_flight[2] == str(test_data["day"]):
            flights.append(int(info_flight[5]))

    count_flights = len(flights)

    return flights, count_flights


def print_conditions(test_data, array_flights):
    """
       Печать условий раунда.
    """
    print(
        "GAME CONDITIONS\n" +
        f'FROM: {test_data["from"]}\n' +
        f'TO: {test_data["to"]}\n' +
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


def player_results(player_lib, c_pointer, file_pointer, route, array_flights, count_flights, free):
    """
       Получение и обработка результатов игрока.
       Подсчет времени выполнения функции игрока
    """
    player_lib.travel_game.argtypes = [ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
     ctypes.c_void_p, Flight]
    player_lib.travel_game.restype = ctypes.c_int

    player_count = utils.call_libary(
        player_lib, ctypes_wrapper, 'i', utils.SEGFAULT, c_pointer, file_pointer, route)

    if check_segfault(player_count):
        return (utils.SEGFAULT, 0, 0)

    error_code = check_flights(player_count, c_pointer, array_flights, count_flights)
    free(c_pointer)

    if error_code != utils.OK:
        return (utils.SOLUTION_FAIL, 0, 0)

    def timeit_wrapper():
        """
           Обертка для Timeit.
        """
        player_lib.travel_game(c_pointer, file_pointer, route)

    time_results = Timer(timeit_wrapper, process_time_ns).repeat(TIMEIT_REPEATS, 1)
    free(c_pointer)
    median, dispersion = utils.process_time(time_results)

    return (utils.OK, median, dispersion)


def start_travel_game(players_info, tests_path):
    """
       Открытие библиотеки с функциями игроков.
       Подсчет времени выполнения их функций.
       Получение результатов.
    """
    utils.redirect_ctypes_stdout()

    with open(tests_path + FILE_AIRPORTS, "r") as file_airports:
        test_data = create_test(file_airports)

    with open(tests_path + FILE_FLIGHTS, "r") as file_flights:
        array_flights, count_flights = solution(file_flights, test_data)

    print_conditions(test_data, array_flights)

    libc = ctypes.CDLL('libc.so.6')

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
    free.restype = None

    mode = init_string("r")
    file_name = init_string(tests_path + FILE_FLIGHTS)

    c_pointer = ctypes.POINTER(ctypes.c_int)()
    file_pointer = fopen(file_name, mode)
    route = Flight(test_data)

    results = []

    for player_lib in players_info:
        if player_lib != "NULL":
            rewind(file_pointer)
            lib = ctypes.CDLL(player_lib)
            results.append(player_results(
                lib, c_pointer, file_pointer, route, array_flights, count_flights, free))
            free(c_pointer)
        else:
            results.append((utils.NO_RESULT, 0, 0))

    fclose(file_pointer)

    utils.print_results(results, players_info)
    return results


if __name__ == "__main__":
    start_travel_game(["games/travelgame/test.so", "NULL", "games/travelgame/test.so"],
     "games/travelgame/tests")
