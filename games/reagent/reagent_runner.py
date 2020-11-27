"""
    ===== R3463NT RUNNER v.1.1.a =====

    Copyright (C) 2019 - 2020 IU7Games Team.

    - Данный скрипт предназначен для проведения
      игры reagent. Правила игры:
      
    - В каждой клетке поля размером NxN лежит либо реактив A,
      либо реактив B, либо O - отсутствие реактива.
    - За ход можно положить в некоторую непустую клетку реактив A, 
      причем преобразование вещества идет так: A+A->B, B+A->0
    - При этом в результате последней реакции происходит взрыв,
      а в соседние непустые клетки по сторонам света,
      попадает по порции реактива A.
    - Необходимо очистить поле.

    - В соревновании принимают участие фукнции,
      имеющие следующую сигнатуру:

    - int reagent_game(char **bf, const int size)

    - char **bf - квадратное игровое поле (матрица символов).
    - const int size - размер игрового поля.
    
    - Возвращаемое значение: порядковый номер ячейки
      в матрице bf (bf[0][2] = 0 * size + 2 = 2)
"""

import ctypes
from random import choice
from dataclasses import dataclass
import games.utils.utils as utils


@dataclass
class Reagent:
    """
        Констатнты игры reagent.
    """

    ascii_a = 65
    ascii_b = 66
    ascii_o = 79

    min_move = 0

    max_count_games = 100


def check_end_game(c_strings, field_size):
    """
        Проверка поля на конец игры.
    """

    for i in range(field_size):
        for j in range(field_size):
            if (c_strings[i].value)[j] != Reagent.ascii_o:
                return False

    return True


def copy(c_strings_copy, c_strings, field_size):
    """
        Копирование игрового поля.
    """

    for i in range(field_size):
        c_strings_copy[i].value = c_strings[i].value


def splash_bomb(move, c_strings, field_size):
    """
        Ход в указанную игроком позицию.
    """

    count_explosions = 0

    reagent = (c_strings[move // field_size].value)[move % field_size]
    replacement_string = list(c_strings[move // field_size].value)

    if reagent == Reagent.ascii_a:
        replacement_string[move % field_size] = Reagent.ascii_b
        c_strings[move // field_size].value = bytes(replacement_string)
    elif reagent == Reagent.ascii_b:
        replacement_string[move % field_size] = Reagent.ascii_o
        count_explosions += 1
        c_strings[move // field_size].value = bytes(replacement_string)

        if move % field_size - 1 >= Reagent.min_move:
            count_explosions += splash_bomb(move - 1, c_strings, field_size)

        if move % field_size + 1 < field_size:
            count_explosions += splash_bomb(move + 1, c_strings, field_size)

        if move // field_size - 1 >= Reagent.min_move:
            count_explosions += splash_bomb(move - field_size, c_strings, field_size)

        if move // field_size + 1  < field_size:
            count_explosions += splash_bomb(move + field_size, c_strings, field_size)

    return count_explosions


def check_player_move(move, c_strings, c_strings_copy, field_size):
    """
        Проверка корректности возвращаемого игроком значения.
    """

    if move < Reagent.min_move or move > field_size * field_size + field_size:
        return False

    for i in range(field_size):
        if c_strings_copy[i].value != c_strings[i].value:
            return False

    return True


def ctypes_wrapper(player_lib, move, gamefield, field_size):
    """
        Обертка для отловки segmentation fault.
    """

    move.value = player_lib.reagent_game(gamefield, field_size)


def print_gamefield(c_strings, field_size):
    """
        Печать игрового поля.
    """
    frame = "┏" + "━" * field_size + "┓"
    print(f"\033[30m{frame}\033[0m")

    for i in range(field_size):
        line = c_strings[i].value.decode(utils.Constants.utf_8)

        print("\033[30m┃", end="")

        for symbol in line:
            if symbol == 'O':
                print(f"\033[30m{symbol}\033[0m", end="")
            if symbol == 'A':
                print(f"\033[32m{symbol}\033[0m", end="")
            if symbol == 'B':
                print(f"\033[36m{symbol}\033[0m", end="")
        print("\033[30m┃")

    frame = "┗" + "━" * field_size + "┛"
    print(f"\033[30m{frame}\033[0m")


def print_round_info(player, score, c_strings, field_size):
    """
        Печать информации о раунде игры.
    """

    print("\033[37mPLAYER: \033[0m", end="")
    print(f"\033[37m{player}\033[0m")

    print("\033[37mNOW SCORE: \033[0m", end="")
    print(f"\033[37m{str(score)}\033[0m")

    print_gamefield(c_strings, field_size)


def random_fill_field(c_strings, field_size):
    """
        Заполнение поля случайным типом реактива.
    """

    reagents = (Reagent.ascii_a, Reagent.ascii_b, Reagent.ascii_o)

    for i in range(field_size):
        replacement_string = list(c_strings[i].value)
        for j in range(field_size):
            symbol = choice(reagents)
            replacement_string[j] = symbol
        c_strings[i].value = bytes(replacement_string)


def create_c_objects(field_size):
    """
        Создание игрового поля.
        Создание его копии.
    """

    c_strings = [ctypes.create_string_buffer(
        b'O' * field_size) for i in range(field_size)]
    c_strings_copy = [ctypes.create_string_buffer(
        b'O' * field_size) for i in range(field_size)]

    random_fill_field(c_strings, field_size)
    copy(c_strings_copy, c_strings, field_size)

    c_gamefield = (ctypes.c_char_p * field_size)(*
    map(ctypes.addressof, c_strings))

    return c_strings, c_strings_copy, c_gamefield


def start_reagent_competition(players_info, field_size):
    """
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

        c_strings, c_strings_copy, gamefield = create_c_objects(field_size)
        game = True
        count_games = Reagent.max_count_games
        points = 0

        while game and count_games:

            count_games -= 1

            print_round_info(player, points, c_strings, field_size)

            move = utils.call_libary(
                player_lib, ctypes_wrapper, 'i', utils.Error.segfault,
                gamefield, field_size)

            if move == utils.Error.segfault:
                print("▼ This player caused segmentation fault. ▼")
                break

            move = player_lib.reagent_game(gamefield, field_size)
            count_explosions = 0

            if check_player_move(move, c_strings, c_strings_copy, field_size):

                count_explosions += splash_bomb(move, c_strings, field_size)
                copy(c_strings_copy, c_strings, field_size)
                points += count_explosions - 1

                if check_end_game(c_strings, field_size):
                    game = False

            else:
                game = False

        results.append(points if points > player[1] else player[1])

    print(f"\033[32mRESULTS: {results}\033[0m")

    return results


if __name__ == "__main__":
    start_reagent_competition([("games/reagent/Oleg.so", 0), ("NULL", 50),
                              ("games/reagent/Misha.so", 0)], 5)
