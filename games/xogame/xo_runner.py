"""
      ===== XO RUNNER v.1.1a =====
      Copyright (C) 2019 IU7Games Team.

    - Данный скрипт предназначен для проведения соревнования
      по XOgame (крестики - нолики).

    - В соревновании принимают функции, имеющие сигнатуру:

    - int xogame(char **bf, const int dime, const char symb)

    - char **bf - квадратное игровое поле (матрица символов).
    - const int dime - размеры этого игрового поля.
    - const char symb - символ Х или О, то есть то, чем ходит игрок.

    - Возвращаемое значение: *порядковый номер ячейки в матрице bf.
     *Вычисление порякового номера: bf[1][2] = 1 * 3 + 2 = 5 (для матрицы 3x3)
"""

import ctypes
import sys
from worker.wiki import NO_RESULT

OK = 0
INVALID_MOVE = 1

DRAW = 0
PLAYER_ONE_WIN = 1
PLAYER_TWO_WIN = 2

ASCII_O = 79
ASCII_X = 88
ASCII_SPACE = 32

ENCODING = "utf-8"
N = 30

STDOUT = sys.__stdout__
LOG = open("deploylog_xogame.txt", "w")

def start_game_print(player1, player2):
    """
        Информаиця о начале раунда.
    """

    print(
        "GAME",
        parsing_name(player1), "(X) VS",
        parsing_name(player2), "(O)"
    )


def end_game_print(player, info):
    """
        Печать результатов раунда.
    """

    print(
        parsing_name(player), info, "\n",
        "=" * N, sep=""
    )


def parsing_name(player_name):
    """
        Преобразование полного пути к файлу с библиотекой игрока
        к gitlab логину игрока.
    """
    return player_name[player_name.rindex('/') + 1: len(player_name) - 3]


def print_results(points, players_info, players_amount):
    """
        Печать результатов в виде:
        ИГРОК ОЧКИ
    """

    for i in range(players_amount):
        if players_info[i][0] != "NULL":
            print("PLAYER", parsing_name(players_info[i][0]), "POINTS:", points[i])


def print_field(c_strings, field_size, player_name):
    """
        Печать игрового поля.
    """

    print(parsing_name(player_name), "player move: ")

    print("┏", "━" * field_size, "┓", sep="")
    for i in range(field_size):
        print("┃", c_strings[i].value.decode(ENCODING), "┃", sep="")
    print("┗", "━" * field_size, "┛", sep="")


def check_win(c_strings, symbol, field_size):
    """
        Проверка строк, столбцов и диагоналей
        на признак победы одного из игроков.
    """

    # Проверка строк и столбцов
    for i in range(field_size):
        row_counter = 0
        column_counter = 0
        for j in range(field_size):
            if (c_strings[i].value)[j] == symbol:
                row_counter += 1
            if (c_strings[j].value)[i] == symbol:
                column_counter += 1

        if field_size in (row_counter, column_counter):
            return True

    # Проверка главной и побочной диагонали
    main_diag_counter = 0
    side_diag_counter = 0
    for i in range(field_size):
        if (c_strings[i].value)[i] == symbol:
            main_diag_counter += 1
        if (c_strings[i].value)[field_size - i - 1] == symbol:
            side_diag_counter += 1

    if field_size in (side_diag_counter, main_diag_counter):
        return True

    return False


def create_c_objects(field_size):
    """
        Создание боевого поля и его копии (массива строк) в виде С объекта.
    """

    c_strings = [ctypes.create_string_buffer(b' ' * field_size) for i in range(field_size)]
    c_strings_copy = [ctypes.create_string_buffer(b' ' * field_size) for i in range(field_size)]
    c_battlefield = (ctypes.c_char_p * field_size)(*map(ctypes.addressof, c_strings))
    return c_strings, c_strings_copy, c_battlefield


def check_move_correctness(c_strings, c_strings_copy, move, field_size):
    """
        Проверка на корректность присланного игроком хода и
        на испорченость матрицы стратегией игрока.
    """

    for i in range(field_size):
        if c_strings_copy[i].value != c_strings[i].value:
            return INVALID_MOVE

    if move >= field_size * field_size:
        return INVALID_MOVE

    if (c_strings[move // field_size].value)[move % field_size] != ASCII_SPACE:
        return INVALID_MOVE

    return OK


def make_move(c_strings, move, symb, field_size):
    """
        Ход в указанную игроком клетку.
    """

    replacement_string = list(c_strings[move // field_size].value)
    replacement_string[move % field_size] = symb
    c_strings[move // field_size].value = bytes(replacement_string)

    return c_strings


def xogame_round(player1_lib, player2_lib, field_size, players_names):
    """
        Запуск одного раунда игры для двух игроков.
    """

    start_game_print(*players_names)
    sys.stdout = LOG
    start_game_print(*players_names)

    c_strings, c_strings_copy, c_battlefield = create_c_objects(field_size)
    shot_count = 0

    while shot_count < field_size * field_size:
        shot_count += 1
        move = player1_lib.xogame(c_battlefield, ctypes.c_int(field_size), ctypes.c_wchar('X'))
        if check_move_correctness(c_strings, c_strings_copy, move, field_size) == INVALID_MOVE:
            end_game_print(players_names[0], " CHEATING")
            sys.stdout = STDOUT
            end_game_print(players_names[0], " CHEATING ")

            return PLAYER_TWO_WIN

        c_strings = make_move(c_strings, move, ASCII_X, field_size)
        c_strings_copy = make_move(c_strings_copy, move, ASCII_X, field_size)
        print_field(c_strings, field_size, players_names[0])
        if check_win(c_strings, ASCII_X, field_size):
            end_game_print(players_names[0], " WIN")
            sys.stdout = STDOUT
            print_field(c_strings, field_size, players_names[0])
            end_game_print(players_names[0], " WIN ")

            return PLAYER_ONE_WIN

        if shot_count == field_size * field_size:
            print("DRAW\n", "=" * N, sep="")
            sys.stdout = STDOUT
            print_field(c_strings, field_size, players_names[0])
            print("DRAW\n", "=" * N, sep="")

            return DRAW

        shot_count += 1
        move = player2_lib.xogame(c_battlefield, ctypes.c_int(field_size), ctypes.c_wchar('O'))
        if check_move_correctness(c_strings, c_strings_copy, move, field_size) == INVALID_MOVE:
            end_game_print(players_names[1], " CHEATING")
            sys.stdout = STDOUT
            end_game_print(players_names[1], " CHEATING")

            return PLAYER_ONE_WIN

        c_strings = make_move(c_strings, move, ASCII_O, field_size)
        c_strings_copy = make_move(c_strings_copy, move, ASCII_O, field_size)
        print_field(c_strings, field_size, players_names[1])
        if check_win(c_strings, ASCII_O, field_size):
            end_game_print(players_names[1], " WIN")
            sys.stdout = STDOUT
            print_field(c_strings, field_size, players_names[1])
            end_game_print(players_names[1], " WIN")

            return PLAYER_TWO_WIN


def calculate_coefficient(pts):
    """
        Подсчёт коэффициента, который отвечает за балансировку набора очков.
    """

    if pts > 2400:
        return 10

    if pts > 1800:
        return 20

    return 40


def calculate_expectation(pts1, pts2):
    """
        Подсчёт математического ожидания.
    """

    return 1 / (1 + 10 ** ((pts2 - pts1) / 400))


def calculate_elo_rating(pts1, pts2, result):
    """
        Подсчёт рейтинга Эло.
    """

    expected_value = calculate_expectation(pts1, pts2)
    coefficient = calculate_coefficient(pts1)
    pts1 += coefficient * (result - expected_value)

    return pts1


def scoring(points, player1_index, player2_index, round_info):
    """
        Запись и подсчёт очков в результирующий массив points.
        Система подсчёта очков по рейтинговой системе Эло.
    """

    if round_info == DRAW:
        player1_round_result = 0.5
        player2_round_result = 0.5
    elif round_info == PLAYER_ONE_WIN:
        player1_round_result = 1
        player2_round_result = 0
    else:
        player1_round_result = 0
        player2_round_result = 1


    pts1 = points[player1_index]
    pts2 = points[player2_index]
    points[player1_index] = int(calculate_elo_rating(pts1, pts2, player1_round_result))
    points[player2_index] = int(calculate_elo_rating(pts2, pts1, player2_round_result))

    return points


def start_xogame_competition(players_info, field_size):
    """
        Функция запускает каждую стратегию с каждой,
        результаты для каждого игрока записываются в массив points.
    """

    points = [players_info[i][1] for i in range(len(players_info))]

    for i in range(len(players_info) - 1):
        if players_info[i][0] != "NULL":
            player_lib = ctypes.CDLL(players_info[i][0])

            for j in range(i + 1, len(players_info)):
                if players_info[j][0] != "NULL":
                    opponent_lib = ctypes.CDLL(players_info[j][0])

                    round_info = xogame_round(
                        player_lib,
                        opponent_lib,
                        field_size,
                        (players_info[i][0], players_info[j][0])
                    )
                    points = scoring(points, i, j, round_info)

                    round_info = xogame_round(
                        opponent_lib,
                        player_lib,
                        field_size,
                        (players_info[j][0], players_info[i][0])
                    )
                    points = scoring(points, j, i, round_info)

                else:
                    points[j] = NO_RESULT
        else:
            points[i] = NO_RESULT

    print_results(points, players_info, len(players_info))
    sys.stdout = LOG
    print_results(points, players_info, len(players_info))
    sys.stdout = STDOUT

    return points


if __name__ == "__main__":
    start_xogame_competition([("./dima.so", 1400),
                              ("./misha.so", 1000)], 5)