"""
    ===== XO RUNNER v.1.2a =====
    Copyright (C) 2019 - 2020 IU7Games Team.

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
import games.utils.utils as utils

DRAW = 0
PLAYER_ONE_WIN = 1
PLAYER_TWO_WIN = 2

ASCII_O = 79
ASCII_X = 88
ASCII_SPACE = 32
N = 30


def print_field(c_strings, field_size, player_name):
    """
        Печать игрового поля.
    """

    print(utils.parsing_name(player_name), "player move: ")

    print("┏", "━" * field_size, "┓", sep="")
    for i in range(field_size):
        print("┃", c_strings[i].value.decode(
            utils.Constants.utf_8), "┃", sep="")
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

    c_strings = [ctypes.create_string_buffer(
        b' ' * field_size) for i in range(field_size)]
    c_strings_copy = [ctypes.create_string_buffer(
        b' ' * field_size) for i in range(field_size)]
    c_battlefield = (ctypes.c_char_p * field_size)(*
                                                   map(ctypes.addressof, c_strings))
    return c_strings, c_strings_copy, c_battlefield


def check_move_correctness(c_strings, c_strings_copy, move, field_size):
    """
        Проверка на корректность присланного игроком хода и
        на испорченость матрицы стратегией игрока.
    """

    if move == utils.Error.segfault:
        print("▼ This player caused segmentation fault. ▼")
        return False

    for i in range(field_size):
        if c_strings_copy[i].value != c_strings[i].value:
            return False

    if move >= field_size * field_size:
        return False

    if (c_strings[move // field_size].value)[move % field_size] != ASCII_SPACE:
        return False

    return True


def make_move(c_strings, move, symb, field_size):
    """
        Ход в указанную игроком клетку.
    """

    replacement_string = list(c_strings[move // field_size].value)
    replacement_string[move % field_size] = symb
    c_strings[move // field_size].value = bytes(replacement_string)

    return c_strings


def ctypes_wrapper(player_lib, move, c_battlefield, field_size, char):
    """
        Обертка для отловки segmentation fault.
    """

    move.value = player_lib.xogame(
        c_battlefield, ctypes.c_int(field_size), ctypes.c_wchar(char))


def xogame_round(player1_lib, player2_lib, field_size, players_names):
    """
        Запуск одного раунда игры для двух игроков.
    """

    utils.start_game_print(*players_names)

    c_strings, c_strings_copy, c_battlefield = create_c_objects(field_size)
    shot_count = 0

    while shot_count < field_size * field_size:
        shot_count += 1

        move = utils.call_libary(
            player1_lib, ctypes_wrapper, 'i', utils.Error.segfault, c_battlefield, field_size, 'X'
        )

        if not check_move_correctness(c_strings, c_strings_copy, move, field_size):
            utils.end_game_print(players_names[0], " CHEATING", N)

            return PLAYER_TWO_WIN

        c_strings = make_move(c_strings, move, ASCII_X, field_size)
        c_strings_copy = make_move(c_strings_copy, move, ASCII_X, field_size)
        print_field(c_strings, field_size, players_names[0])
        if check_win(c_strings, ASCII_X, field_size):
            utils.end_game_print(players_names[0], " WIN", N)

            return PLAYER_ONE_WIN

        if shot_count == field_size * field_size:
            print("TIE\n", "=" * N, sep="")

            return DRAW

        shot_count += 1

        move = utils.call_libary(
            player2_lib, ctypes_wrapper, 'i', utils.Error.segfault, c_battlefield, field_size, 'O'
        )

        if not check_move_correctness(c_strings, c_strings_copy, move, field_size):
            utils.end_game_print(players_names[1], " CHEATING", N)

            return PLAYER_ONE_WIN

        c_strings = make_move(c_strings, move, ASCII_O, field_size)
        c_strings_copy = make_move(c_strings_copy, move, ASCII_O, field_size)
        print_field(c_strings, field_size, players_names[1])
        if check_win(c_strings, ASCII_O, field_size):
            utils.end_game_print(players_names[1], " WIN", N)

            return PLAYER_TWO_WIN


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
    points[player1_index] = int(
        utils.calculate_elo_rating(pts1, pts2, player1_round_result))
    points[player2_index] = int(
        utils.calculate_elo_rating(pts2, pts1, player2_round_result))

    return points


def start_xogame_competition(players_info, field_size):
    """
        Функция запускает каждую стратегию с каждой,
        результаты для каждого игрока записываются в массив points.
    """

    if field_size == 3:
        utils.redirect_ctypes_stdout()

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
                    points[j] = utils.GameResult.no_result
        else:
            points[i] = utils.GameResult.no_result

    utils.print_score_results(points, players_info, len(players_info))

    return points


if __name__ == "__main__":
    start_xogame_competition([("games/xogame/dima.so", 1400),
                              ("games/xogame/misha.so", 1000)], 5)
