"""
    ===== T3TR15 RUNNER v.1.1.a =====

    Copyright (C) 2019 - 2020 IU7Games Team.

    - Данный скрипт предназначен для проведения соревнований
      по игре tetris.

    - В соревновании принимают участие функции, имеющие сигнатуру:

    - int tetris_game(char **bf, char figure, int *angle)

    - Возвращаемое значение - номер столбца, в которую помещается верхний
     левый угол фигуры
"""

import ctypes
from random import randint
import games.utils.utils as utils

ROWS = 20
COLUMNS = 10
MAX_LEN_FIGURE = 4
COUNT_FIGURES = 7
MIN_INDEX = 0
MAX_INDEX = 9

ASCII_X = 88

POINTS = 10
ADD_POINTS = 5
MAX_SCORE = 1000


def print_gamefield(c_strings):
    """
        Печать игрового поля.
    """

    print("\033[33m{}\033[0m" .format("\nGAMEFIELD:"))
    print("\033[30m{}\033[0m" .format("┏" + "━" * COLUMNS + "┓"))

    for i in range(ROWS):
        line = c_strings[i].value.decode(utils.Constants.utf_8)
        print("\033[30m{}" .format("┃"), end="")
        for j in range(COLUMNS):
            if line[j] == 'J':
                print("\033[31m{}\033[0m" .format(line[j]), end="")
            if line[j] == 'I':
                print("\033[32m{}\033[0m" .format(line[j]), end="")
            if line[j] == 'O':
                print("\033[33m{}\033[0m" .format(line[j]), end="")
            if line[j] == 'L':
                print("\033[34m{}\033[0m" .format(line[j]), end="")
            if line[j] == 'Z':
                print("\033[35m{}\033[0m" .format(line[j]), end="")
            if line[j] == 'T':
                print("\033[36m{}\033[0m" .format(line[j]), end="")
            if line[j] == 'S':
                print("\033[37m{}\033[0m" .format(line[j]), end="")
            if line[j] == 'X':
                print("\033[30m{}\033[0m" .format(line[j]), end="")
        print("\033[30m{}\033[0m" .format("┃"))

    print("\033[30m{}\033[0m" .format("┗" + "━" * COLUMNS + "┛"))


def scoring(count_full_lines):
    """
        Подсчет очков.
    """
    points = 0

    for i in range(count_full_lines):
        points += POINTS * i + POINTS

    return points


def remove_lines(c_strings, line, c_strings_copy):
    """
        Удаление заполненных строк.
    """
    empty_line = [ctypes.create_string_buffer(
        b'X' * COLUMNS) for i in range(ROWS)]

    for i in range(line, 0, -1):
        c_strings[i].value = c_strings[i - 1].value

    c_strings[0].value = empty_line[0].value


def find_filled_lines(c_strings, c_strings_copy):
    """
        Подсчет заполненных строк.
        Их удаление.
    """

    count = 0
    i = ROWS - 1

    while i > 0:
        fl = True
        for j in range(COLUMNS):
            if (c_strings[i].value)[j] == ASCII_X:
                fl = False
        if fl:
            count += 1
            remove_lines(c_strings, i, c_strings_copy)
        else:
            i -= 1

    return count


def copy(c_strings_copy, c_strings):
    """
        Копирование игрового поля.
    """

    for i in range(ROWS):
        c_strings_copy[i].value = c_strings[i].value


def print_now_score(player, points):
    """
        Печать текущих очков игрока.
    """
    print("\033[33m{}\033[0m" .format("PLAYER: "), end="")
    print("\033[37m{}\033[0m" .format(player))

    print("\033[33m{}\033[0m" .format("NOW SCORE: "), end="")
    print("\033[37m{}\033[0m" .format(str(points)))


def get_height_figure(figure):
    """
        Подсчет высоты фигуры.
    """

    max_height = 0
    for j in range(MAX_LEN_FIGURE):
        now_height = 0

        for i in range(MAX_LEN_FIGURE):
            if figure[i][j] != 'X':
                now_height +=1

        if now_height > max_height:
            max_height = now_height

    return max_height


def shift_figure(matrix_figure):
    """
        Сдвиг фигуры в матрице фигуры в левый угол.
    """
    i = 0
    while i < MAX_LEN_FIGURE - 1:
        count = 0
        for j in range(MAX_LEN_FIGURE):
            if matrix_figure[i][j] == 'X':
                count += 1

        if count == MAX_LEN_FIGURE:
            for k in range(MAX_LEN_FIGURE - 1):
                for j in range(MAX_LEN_FIGURE):
                    matrix_figure[k][j] = matrix_figure[k + 1][j]
            for j in range(MAX_LEN_FIGURE):
                matrix_figure[MAX_LEN_FIGURE - i - 1][j] = 'X'
        else:
            break

    j = 0
    while j < MAX_LEN_FIGURE - 1:
        count = 0
        for i in range(MAX_LEN_FIGURE):
            if matrix_figure[i][j] == 'X':
                count += 1

        if count == MAX_LEN_FIGURE:
            for k in range(MAX_LEN_FIGURE - 1):
                for i in range(MAX_LEN_FIGURE):
                    matrix_figure[i][k] = matrix_figure[i][k + 1]
            for i in range(MAX_LEN_FIGURE):
                matrix_figure[i][MAX_LEN_FIGURE - j - 1] = 'X'
        else:
            break

    return matrix_figure


def rotate_figure(figure):
    """
        Поворот фигуры на 90 градусов по часовой стрелке.
    """
    return [[figure[j][i] for j in range(MAX_LEN_FIGURE - 1, -1, -1)] for i in range(MAX_LEN_FIGURE)]


def move_figure(move, angle, figure, c_strings):
    """
        Ход в указанную игроком позицию.
    """

    if angle.value not in [0, 3, 6, 9]:
        return False

    for i in range(angle.value // 3):
        figure = rotate_figure(figure)

    figure = shift_figure(figure)
    height = get_height_figure(figure)

    if (c_strings[0].value)[move] != ASCII_X:
        return False

    free_position = 0
    while (c_strings[free_position].value)[move] == ASCII_X:
        free_position += 1

        if free_position == ROWS:
            break

    free_position -= 1

    for i in range(MAX_LEN_FIGURE):
        for j in range(MAX_LEN_FIGURE):
            if figure[i][j] != 'X':
                if move + j > COLUMNS - 1 or free_position - (height - i - 1) < 0 or \
                    free_position - (height - i - 1) > ROWS - 1:
                    return False
                if (c_strings[free_position - (height - i - 1)].value)[move + j] != ASCII_X:
                    return False

                replacement_string = list(c_strings[free_position - (height - i - 1)].value)
                replacement_string[move + j] = ord(figure[i][j])
                c_strings[free_position - (height - i - 1)].value = bytes(replacement_string)

    return True


def check_player_move(move, c_strings, c_strings_copy):
    """
       Проверка корректности возвращаемого игроком значения.
    """

    if move < MIN_INDEX or move > MAX_INDEX:
        return False

    for i in range(ROWS):
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

    print("\033[33m{}\033[0m" .format("\nNEW FIGURE:"))
    for i in range(MAX_LEN_FIGURE):
        for j in range(MAX_LEN_FIGURE):
            if (j == MAX_LEN_FIGURE - 1):
                print(figure[i][j], end = "\n")
            else:
                print(figure[i][j], end = "")
    print("")


def get_figure():
    """
        Выбор новой фигуры.
        Создание матрицы, представляющей фигуру.
    """

    figures = ['J', 'I', 'O', 'L', 'Z', 'T', 'S']

    figure = figures[randint(0, COUNT_FIGURES - 1)]

    matrix_figure = [['X'] * MAX_LEN_FIGURE for i in range(MAX_LEN_FIGURE)]

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
        for i in range(1, 3):
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
        b'X' * COLUMNS) for i in range(ROWS)]
    c_strings_copy = [ctypes.create_string_buffer(
        b'X' * COLUMNS) for i in range(ROWS)]
    c_gamefield = (ctypes.c_char_p * ROWS)(*
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
        if player == "NULL":
            results.append(utils.GameResult.no_result)
            continue

        player_lib = ctypes.CDLL(player)

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
            move_info = check_player_move(move, c_strings, c_strings_copy)

            if move_info:
                is_done = move_figure(move, angle, matrix_figure, c_strings)

                if not is_done:
                    print_now_score(player, points)
                    break
                points += ADD_POINTS
                copy(c_strings_copy, c_strings)

                count_full_line = find_filled_lines(c_strings, c_strings_copy)

                if count_full_line:
                    copy(c_strings_copy, c_strings)
                    points += scoring(count_full_line)

                print_now_score(player, points)
                print_gamefield(c_strings)

                if points >= MAX_SCORE:
                    game = False

            else:
                print_now_score(player, points)
                game = False

        results.append(points)

    print("\033[33m{}\033[0m" .format("RESULTS: "), end="")
    print(results)
    return results


if __name__ == "__main__":
    start_tetris_competition(["games/tetrisgame/Anna.so", "NULL", "games/tetrisgame/Oleg.so", "games/tetrisgame/Misha.so"])