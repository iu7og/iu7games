"""
    ===== T3TR15 RUNNER v.2.1.b =====

    Copyright (C) 2019 - 2020 IU7Games Team.

    - Данный скрипт предназначен для проведения соревнований
      по игре tetris.

    - В соревновании принимают участие функции, имеющие сигнатуру:

    - int tetris_game(char **bf, char figure, int *angle)

    - Возвращаемое значение - номер столбца, в которую помещается верхний
     левый угол фигуры
"""

import ctypes
from dataclasses import dataclass
from random import randint
import games.utils.utils as utils


@dataclass
class Tetris:
    """
        Константы игры тетрис.
    """
    rows = 20
    columns = 10
    height_figure = 4
    count_figures = 7
    min_move = 0
    max_move = 9

    ascii_x = 88

    max_score = 25000
    points = 10
    bonus = 5


def print_gamefield(c_strings):
    """
        Печать игрового поля.
    """
    frame = "┏" + "━" * Tetris.columns + "┓"
    print("\033[33m\nGAMEFIELD\033[0m")
    print(f"\033[30m{frame}\033[0m")

    for i in range(Tetris.rows):
        line = c_strings[i].value.decode(utils.Constants.utf_8)
        print("\033[30m┃", end="")
        for symbol in line:
            if symbol == 'J':
                print(f"\033[31m{symbol}\033[0m", end="")
            if symbol == 'I':
                print(f"\033[32m{symbol}\033[0m", end="")
            if symbol == 'O':
                print(f"\033[33m{symbol}\033[0m", end="")
            if symbol == 'L':
                print(f"\033[34m{symbol}\033[0m", end="")
            if symbol == 'Z':
                print(f"\033[35m{symbol}\033[0m", end="")
            if symbol == 'T':
                print(f"\033[36m{symbol}\033[0m", end="")
            if symbol == 'S':
                print(f"\033[37m{symbol}\033[0m", end="")
            if symbol == 'X':
                print(f"\033[30m{symbol}\033[0m", end="")
        print("\033[30m┃")

    frame = "┗" + "━" * Tetris.columns + "┛"
    print(f"\033[30m{frame}\033[0m")


def scoring(count_full_lines):
    """
        Подсчет очков.
    """
    points = 0

    for i in range(count_full_lines):
        points += Tetris.points * i + Tetris.points

    return points


def remove_lines(c_strings, line):
    """
        Удаление заполненных строк.
    """
    empty_line = [ctypes.create_string_buffer(
        b'X' * Tetris.columns) for i in range(Tetris.rows)]

    for i in range(line, 0, -1):
        c_strings[i].value = c_strings[i - 1].value

    c_strings[0].value = empty_line[0].value


def find_filled_lines(c_strings):
    """
        Подсчет заполненных строк.
        Их удаление.
    """

    count = 0
    i = Tetris.rows - 1

    while i > 0:
        full = True
        for j in range(Tetris.columns):
            if (c_strings[i].value)[j] == Tetris.ascii_x:
                full = False
        if full:
            count += 1
            remove_lines(c_strings, i)
        else:
            i -= 1

    return count


def copy(c_strings_copy, c_strings):
    """
        Копирование игрового поля.
    """

    for i in range(Tetris.rows):
        c_strings_copy[i].value = c_strings[i].value


def print_now_score(player, points):
    """
        Печать текущих очков игрока.
    """
    print("\033[33mPLAYER: \033[0m", end="")
    print(f"\033[37m{player}\033[0m")

    print("\033[33mNOW SCORE: \033[0m", end="")
    print(f"\033[37m{str(points)}\033[0m")


def try_move(figure, c_strings, move, free_position):
    """
        Попытка поставить фигуру в свбодную позицию
        в указанном столбце.
    """

    for i in range(Tetris.height_figure):
        for j in range(Tetris.height_figure):
            if figure[i][j] != 'X':
                if move + j > Tetris.columns - 1 or free_position + i < 0 or \
                    free_position + i > Tetris.rows - 1:
                    return False
                if (c_strings[free_position + i].value)[move + j] != Tetris.ascii_x:
                    return False
    return True


def get_free_position(c_strings, move):
    """
        Получить свободную позицию столбца.
    """
    free_position = 0
    while (c_strings[free_position].value)[move] == Tetris.ascii_x:
        free_position += 1

        if free_position == Tetris.rows:
            break
    free_position -= 1

    return free_position


def shift_figure(matrix_figure):
    """
        Сдвиг фигуры в матрице фигуры в левый угол.
    """
    i = 0
    count = Tetris.height_figure
    while i < Tetris.height_figure - 1 and count == Tetris.height_figure:
        count = 0
        for j in range(Tetris.height_figure):
            if matrix_figure[i][j] == 'X':
                count += 1

        if count == Tetris.height_figure:
            for k in range(Tetris.height_figure - 1):
                for j in range(Tetris.height_figure):
                    matrix_figure[k][j] = matrix_figure[k + 1][j]
            for j in range(Tetris.height_figure):
                matrix_figure[Tetris.height_figure - i - 1][j] = 'X'

    j = 0
    count = Tetris.height_figure
    while j < Tetris.height_figure - 1 and count == Tetris.height_figure:
        count = 0
        for i in range(Tetris.height_figure):
            if matrix_figure[i][j] == 'X':
                count += 1

        if count == Tetris.height_figure:
            for k in range(Tetris.height_figure - 1):
                for i in range(Tetris.height_figure):
                    matrix_figure[i][k] = matrix_figure[i][k + 1]
            for i in range(Tetris.height_figure):
                matrix_figure[i][Tetris.height_figure - j - 1] = 'X'

    return matrix_figure


def rotate_figure(figure):
    """
        Поворот фигуры на 90 градусов по часовой стрелке.
    """
    return [[figure[j][i] for j in range(Tetris.height_figure - 1, -1, -1)] \
        for i in range(Tetris.height_figure)]


def move_figure(move, angle, figure, c_strings):
    """
        Ход в указанную игроком позицию.
    """

    if angle.value not in (0, 3, 6, 9):
        return False

    for i in range(angle.value // 3):
        figure = rotate_figure(figure)

    figure = shift_figure(figure)

    if (c_strings[0].value)[move] != Tetris.ascii_x:
        return False

    free_position = get_free_position(c_strings, move)
    is_moved = False

    while not is_moved:

        if try_move(figure, c_strings, move, free_position):
            is_moved = True

            for i in range(Tetris.height_figure):
                for j in range(Tetris.height_figure):
                    if figure[i][j] != 'X':
                        replacement_string = list(c_strings[free_position + i].value)
                        replacement_string[move + j] = ord(figure[i][j])
                        c_strings[free_position + i].value = bytes(replacement_string)
        else:
            free_position -= 1

        if free_position == -1:
            return False

    return True


def check_player_move(move, c_strings, c_strings_copy):
    """
       Проверка корректности возвращаемого игроком значения.
    """

    if move < Tetris.min_move or move > Tetris.max_move:
        return False

    for i in range(Tetris.rows):
        if c_strings_copy[i].value != c_strings[i].value:
            return False

    return True


def ctypes_wrapper(player_lib, move, gamefield, figure, angle):
    """
       Обёртка для отловки segmentation fault.
    """

    move.value = player_lib.tetris_game(gamefield, figure, angle)


def print_figure(figure):
    """
        Печать текущей фигуры.
    """

    print("\033[33m\nNEW FIGURE:\033[0m")
    for i in range(Tetris.height_figure):
        for j in range(Tetris.height_figure):
            if j == Tetris.height_figure - 1:
                print(figure[i][j], end="\n")
            else:
                print(figure[i][j], end="")
    print("")


def get_figure():
    """
        Выбор новой фигуры.
        Создание матрицы, представляющей фигуру.
    """

    figures_analogues = ('J', 'I', 'O', 'L', 'Z', 'T', 'S')

    figure = figures_analogues[randint(0, Tetris.count_figures - 1)]

    matrix_figure = [['X'] * Tetris.height_figure for i in range(Tetris.height_figure)]

    # The borders - height and lenght of the figure
    if figure == 'J':
        for i in range(2):
            matrix_figure[2][i] = 'J'
        for i in range(2):
            matrix_figure[i][1] = 'J'

    if figure == 'I':
        for i in range(4):
            matrix_figure[i][0] = 'I'

    if figure == 'O':
        for i in range(2):
            for j in range(2):
                matrix_figure[i][j] = 'O'

    if figure == 'L':
        for i in range(1, 2):
            matrix_figure[2][i] = 'L'
        for i in range(3):
            matrix_figure[i][0] = 'L'

    if figure == 'Z':
        for i in range(2):
            matrix_figure[0][i] = 'Z'
        for i in range(1, 3):
            matrix_figure[1][i] = 'Z'

    if figure == 'T':
        for i in range(3):
            matrix_figure[0][i] = 'T'
        matrix_figure[1][1] = 'T'

    if figure == 'S':
        for i in range(1, 3):
            matrix_figure[0][i] = 'S'
        for i in range(2):
            matrix_figure[1][i] = 'S'

    return figure, matrix_figure


def create_c_objects():
    """
        Создание игрового поля.
        Создание его копии.
    """

    c_strings = [ctypes.create_string_buffer(
        b'X' * Tetris.columns) for i in range(Tetris.rows)]
    c_strings_copy = [ctypes.create_string_buffer(
        b'X' * Tetris.columns) for i in range(Tetris.rows)]
    c_gamefield = (ctypes.c_char_p * Tetris.rows)(*
    map(ctypes.addressof, c_strings))

    return c_strings, c_strings_copy, c_gamefield


def start_tetris_competition(players_info):
    """
        Создание игрового поля.
        Запуск игры для каждого игрока.
        Подсчет очков.
    """

    utils.redirect_ctypes_stdout()

    results = []

    for player in players_info:
        if player[0] == "NULL":
            results.append(utils.GameResult.no_result)
            continue

        player_lib = ctypes.CDLL(player[0])

        c_strings, c_strings_copy, gamefield = create_c_objects()
        angle = ctypes.c_int()
        game = True
        points = 0

        while game:

            figure, matrix_figure = get_figure()
            c_figure = ctypes.c_char(figure.encode(utils.Constants.utf_8))
            print_figure(matrix_figure)

            move = utils.call_libary(
                player_lib, ctypes_wrapper, 'i', utils.Error.segfault, gamefield, c_figure,
                ctypes.byref(angle))

            if move == utils.Error.segfault:
                print("▼ This player caused segmentation fault. ▼")
                break

            move = player_lib.tetris_game(gamefield, c_figure, ctypes.byref(angle))

            if check_player_move(move, c_strings, c_strings_copy):

                if not move_figure(move, angle, matrix_figure, c_strings):
                    print_now_score(player[0], points)
                    break

                points += Tetris.bonus
                copy(c_strings_copy, c_strings)

                count_full_line = find_filled_lines(c_strings)

                if count_full_line:
                    copy(c_strings_copy, c_strings)
                    points += scoring(count_full_line)

                print_now_score(player[0], points)
                print_gamefield(c_strings)

                if points >= Tetris.max_score:
                    game = False

            else:
                print_now_score(player[0], points)
                game = False

        results.append(points if points > player[1] else player[1])

    print(f"\033[33mRESULTS: {results}\033[0m")

    return results


if __name__ == "__main__":
    start_tetris_competition([("games/tetrisgame/Oleg.so", 0), ("NULL", 50),
                              ("games/tetrisgame/test.so", 0)])
