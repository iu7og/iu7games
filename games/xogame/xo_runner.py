"""
    XO runner v.0.1 (alpha)

    Данный скрипт предназначен для проведения соревнования
    по XOgame (крестики - нолики).

    В соревновании принимают функции, имеющие сигнатуру:

    int xogame(char **bf, const int dime, const char symb)

    char **bf - квадратное игровое поле (матрица символов).
    const int dime - размеры этого игрового поля.
    const char symb - символ Х или О, то есть то, чем ходит игрок.

    Возвращаемое значение: *порядковый номер ячейки в матрице bf.
    *Вычисление порякового номера: bf[1][2] = 1 * 3 + 2 = 5 (для матрицы 3x3)
"""

import ctypes

OK = 0
INVALID_MOVE = 1

DRAW = 0
PLAYER_ONE_WIN = 1
PLAYER_TWO_WIN = 2

WIN_POINTS = 3
DRAW_POINTS = 1

ASCII_O = 79
ASCII_X = 88
ASCII_SPACE = 32

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


def xogame_round(player1_lib, player2_lib, field_size):
    """
        Запуск одного раунда игры для двух игроков.
    """

    c_strings, c_strings_copy, c_battlefield = create_c_objects(field_size)
    shot_count = 0

    while shot_count < field_size * field_size:
        shot_count += 1
        move = player1_lib.xogame(c_battlefield, ctypes.c_int(field_size), ctypes.c_wchar('X'))
        if check_move_correctness(c_strings, c_strings_copy, move, field_size) == INVALID_MOVE:
            return PLAYER_TWO_WIN

        c_strings = make_move(c_strings, move, ASCII_X, field_size)
        c_strings_copy = make_move(c_strings_copy, move, ASCII_X, field_size)
        if check_win(c_strings, ASCII_X, field_size):
            return PLAYER_ONE_WIN

        if shot_count == field_size * field_size:
            return DRAW

        shot_count += 1
        move = player2_lib.xogame(c_battlefield, ctypes.c_int(field_size), ctypes.c_wchar('O'))
        if check_move_correctness(c_strings, c_strings_copy, move, field_size) == INVALID_MOVE:
            return PLAYER_ONE_WIN

        c_strings = make_move(c_strings, move, ASCII_O, field_size)
        c_strings_copy = make_move(c_strings_copy, move, ASCII_O, field_size)
        if check_win(c_strings, ASCII_O, field_size):
            return PLAYER_TWO_WIN

    return DRAW


def scoring(points, player1_index, player2_index, result):
    """
        Запись очков в результирующий массив очков points.
    """

    if result == PLAYER_ONE_WIN:
        points[player1_index] += WIN_POINTS
    elif result == PLAYER_TWO_WIN:
        points[player2_index] += WIN_POINTS
    else:
        points[player1_index] += DRAW_POINTS
        points[player2_index] += DRAW_POINTS

    return points


def start_xogame_competition(players_libs, field_size):
    """
        Функция запускает каждую стратегию с каждой,
        результаты для каждого игрока записываются в массив points.
    """

    points = [0] * len(players_libs)

    for i in range(len(players_libs) - 1):
        player_lib = ctypes.CDLL(players_libs[i])
        for j in range(i + 1, len(players_libs)):
            opponent_lib = ctypes.CDLL(players_libs[j])
            points = scoring(points, i, j, xogame_round(player_lib, opponent_lib, field_size))
            points = scoring(points, j, i, xogame_round(opponent_lib, player_lib, field_size))

    print(points)
    return points


if __name__ == "__main__":
    start_xogame_competition(["./test1.so", "./test2.so", "./test3.so"], 3)
