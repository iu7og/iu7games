"""
    XO runner v.0.1 (alpha)

    Данный скрипт предназначен для проведения соревнования
    по XOgame (крестики - нолики).

    В сореновании принимают функции, имеющие сигнатуру:

    int xogame(char **bf, const int dime, const char symb)

    char **bf - квадратное игровое поле (матрица символов).
    const int dime - размеры этого игрового поля.
    const char symb - символ Х или О, то есть то, чем ходит игрок.

    Возвращаемое значение: *порядковый номер ячейки в матрице bf.
    *Вычисление порякового номера: bf[2][2] = 2 * 3 + 2 = 7 (для матрицы 3x3)
"""

import ctypes

OK = 0
INVALID_MOVE = 1

DRAW = 0
PLAYER_ONE_WIN = 1
PLAYER_TWO_WIN = 2

WIN_POINTS = 3
DRAW_POINTS = 1
DIME = 3

ASCII_O = 79
ASCII_X = 88
ASCII_SPACE = 32

def check_win(c_strings, symbol):
    """
        Проверка строк, столбцов и диагоналей
        на признак победы одного из игроков.
    """

    # Проверка строк и столбцов
    for i in range(DIME):
        row_counter = 0
        column_counter = 0
        for j in range(DIME):
            if (c_strings[i].value)[j] == symbol:
                row_counter += 1
            if (c_strings[j].value)[i] == symbol:
                column_counter += 1

        if row_counter == DIME or column_counter == DIME:
            return True

    # Проверка главной и побочной диагонали
    main_diag_counter = 0
    side_diag_counter = 0
    for i in range(DIME):
        if (c_strings[i].value)[i] == symbol:
            main_diag_counter += 1
        if (c_strings[i].value)[DIME - i - 1] == symbol:
            side_diag_counter += 1

    if side_diag_counter == DIME or main_diag_counter == DIME:
        return True

    return False


def create_c_objects():
    """
        Создание боевого поля (массива строк) в виде С объекта.
    """

    c_strings = [ctypes.create_string_buffer(b' ' * DIME) for i in range(DIME)]
    c_battlefield = (ctypes.c_char_p * DIME)(*map(ctypes.addressof, c_strings))
    return ctypes.c_wchar('O'), ctypes.c_wchar('X'), c_strings, c_battlefield


def check_move_correctness(c_strings, move):
    """
        Проверка на корректность присланного игроком хода.
    """

    # ADD: Проверка на испорченность матрицы
    if move >= DIME * DIME:
        return INVALID_MOVE

    if (c_strings[move // DIME].value)[move % DIME] != ASCII_SPACE:
        return INVALID_MOVE

    return OK


def make_move(c_strings, move, symb):
    """
        Ход в указанную игроком клетку.
    """

    replacement_string = list(c_strings[move // DIME].value)
    replacement_string[move % DIME] = symb
    c_strings[move // DIME].value = bytes(replacement_string)
    return c_strings


def xogame_round(player1_lib, player2_lib):
    """
        Запуск одного раунда игры для двух игроков.
        Каждому игроку предоставляется возможность сходить как за Х, так и за О.
    """

    c_symb_x, c_symb_o, c_strings, c_battlefield = create_c_objects()
    shot_count = 0

    while shot_count != DIME * DIME:
        shot_count += 1
        move = player1_lib.xogame(c_battlefield, DIME, c_symb_x)
        if check_move_correctness(c_strings, move):
            return PLAYER_TWO_WIN

        c_strings = make_move(c_strings, move, ASCII_X)
        if check_win(c_strings, ASCII_X):
            return PLAYER_ONE_WIN

        if shot_count == DIME * DIME:
            return DRAW

        shot_count += 1
        move = player2_lib.xogame(c_battlefield, DIME, c_symb_o)
        if check_move_correctness(c_strings, move):
            return PLAYER_ONE_WIN

        c_strings = make_move(c_strings, move, ASCII_O)
        if check_win(c_strings, ASCII_O):
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


def start_xogame_competition(players_libs):
    """
        Функция запускает каждую стратегию с каждой,
        результаты для каждого игрока записываются в массив points.
    """

    points = [0] * DIME

    for i in range(len(players_libs) - 1):
        player_lib = ctypes.CDLL(players_libs[i])
        for j in range(i + 1, len(players_libs)):
            opponent_lib = ctypes.CDLL(players_libs[j])
            points = scoring(points, i, j, xogame_round(player_lib, opponent_lib))
            points = scoring(points, j, i, xogame_round(opponent_lib, player_lib))

    print(points)
    return points


if __name__ == "__main__":
    start_xogame_competition(["./test1.so", "./test2.so", "./test3.so"])
