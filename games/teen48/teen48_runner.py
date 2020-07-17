"""===== TEEN48 RUNNER v.1.1a =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    - Данный скрипт предназначен для проведения соревнований по игре teen48 (2048).

    - В соревновании принимают функции, имеющие сигнатуру:
    char teen48game(matrix_t game_field)

    - Структура matrix_t:
      typedef struct
      {
         int rows;
         int columns;
         int **game_field;
      } matrix_t;

    - Функция должна возвращать char-значение: r, l, d, u, в зависимости
    от того, в какую сторону нужно сделать ход (право, лево, вниз и вверх соответственно)
"""

import ctypes
from random import randint, random
import games.utils.utils as utils

class Matrix(ctypes.Structure):
    """
        Класс Matrix описывает одноименную структуру в С.
        Класс имеет поля:
        - rows - количество строк матрицы
        - columns - количество столбцов матрицы
        - matrix - указатель на начало матрицы.
    """

    _fields_ = [("rows", ctypes.c_int),
                ("columns", ctypes.c_int),
                ("matrix", ctypes.POINTER(ctypes.POINTER(ctypes.c_int)))]

    def __init__(self, rows, columns):
        """
            Конструктор для класса Matrix
        """

        self.rows = rows
        self.columns = columns
        self.matrix = init_matrix(rows, columns)


def fill_random_cell(game_field, number, rows, columns):
    """
        Заполнение передаваемой цифрой случайной и пустой клетки игрового поля.
    """

    i = randint(0, rows - 1)
    j = randint(0, columns - 1)

    while game_field[i][j] != 0:
        i = randint(0, rows - 1)
        j = randint(0, columns - 1)

    game_field[i][j] = number


def get_random_numb():
    """
        Получение цифры 2 или 4 для дальнейшего спавна
        этой цифры на игровом поле.
    """

    return 2 if random() > 0.1 else 4


def init_matrix(rows, columns):
    """
        Заполнение матрицы нулями.
    """

    c_int_p = ctypes.POINTER(ctypes.c_int)
    value_array = ctypes.c_int * columns
    pointer_array = c_int_p * rows
    matrix_pointer = pointer_array()

    for i in range(rows):
        matrix_pointer[i] = value_array()
        for j in range(columns):
            matrix_pointer[i][j] = 0

    return matrix_pointer


def check_end_game(game_field):
    """
        Проверка поля на возможность хода.
    """

    for i in range(game_field.rows - 1):
        for j in range(game_field.rows - 1):
            if game_field.matrix[i][j] == game_field.matrix[i + 1][j] or \
                game_field.matrix[i][j + 1] == game_field.matrix[i][j]:
                return False

    for i in range(game_field.rows):
        for j in range(game_field.rows):
            if game_field.matrix[i][j] == 0:
                return False

    for i in range(game_field.rows - 1):
        if game_field.matrix[game_field.rows - 1][i] == \
            game_field.matrix[game_field.rows -1][i + 1]:
            return False

    for i in range(game_field.rows - 1):
        if game_field.matrix[i][game_field.rows - 1] == \
            game_field.matrix[i + 1][game_field.rows - 1]:
            return False

    return True


def reverse_field(game_field):
    """
        Переворачивает каждую строку матрицы.
    """

    for i in range(game_field.rows):
        for j in range(game_field.columns // 2):
            temp = game_field.matrix[i][j]
            game_field.matrix[i][j] = game_field.matrix[i][game_field.columns - j - 1]
            game_field.matrix[i][game_field.columns - j - 1] = temp

    return game_field


def transpose_field(game_field):
    """
        Транспонирует матрицу.
    """

    for i in range(game_field.rows):
        for j in range(game_field.columns - i):
            temp = game_field.matrix[i][j + i]
            game_field.matrix[i][j + i] = game_field.matrix[j + i][i]
            game_field.matrix[j + i][i] = temp

    return game_field


def shift_field(game_field):
    """
        Сдвиг ненулевых ячеек игрового поля в левую сторону.
    """

    new_matrix = Matrix(game_field.rows, game_field.columns)

    for i in range(game_field.rows):
        nonzero_elements = 0

        for j in range(game_field.columns):
            if game_field.matrix[i][j] != 0:
                new_matrix.matrix[i][nonzero_elements] = game_field.matrix[i][j]
                nonzero_elements += 1

    shift_is_done = is_fields_identical(game_field, new_matrix)

    return new_matrix, not shift_is_done


def merge_field_cells(game_field):
    """
        Соединение соседних ячеек игрового, если они равны.
    """

    merge_is_done = False

    for i in range(game_field.rows):
        for j in range(game_field.columns - 1):
            if game_field.matrix[i][j] == game_field.matrix[i][j + 1] \
                and game_field.matrix[i][j] != 0:

                game_field.matrix[i][j] *= 2
                game_field.matrix[i][j + 1] = 0
                merge_is_done = True

    return game_field, merge_is_done


def update_field(game_field, field_location):
    """
        Обновление матрицы взависимости от сделаного хода игроком.
        Сначала матрица приводится к такому виду, чтобы любой ход
        можно было обработать как ход влево (манипуляции с транспонированием и реверсом строк).
        После обновления матрицы, она приводится к исходному виду. (транспонирование и/или реверс)
    """

    if field_location is not None:
        game_field = field_location(game_field)

    game_field, shift_is_done = shift_field(game_field)
    game_field, merge_is_done = merge_field_cells(game_field)
    game_field, _ = shift_field(game_field)

    if field_location is not None:
        game_field = field_location(game_field)

    return game_field, shift_is_done or merge_is_done


def make_move(move, game_field):
    """
        Создание хода влево, вправо, вверх или вниз, в зависимости от переданного
        игроком значения (l, r, u, d соответственно).
        В случае невалидного переданного значения, функция возвращает исходную матрицу.
    """

    is_done = False

    if move == 'l':
        game_field, is_done = update_field(game_field, None)
    elif move == 'r':
        game_field, is_done = update_field(game_field, reverse_field)
    elif move == 'u':
        game_field, is_done = update_field(game_field, transpose_field)
    elif move == 'd':
        game_field, is_done = update_field(game_field, lambda x: reverse_field(transpose_field(x)))

    return game_field, is_done


def is_fields_identical(game_field, matrix_field_copy):
    """
        Проверка на равенство двух матриц.
    """

    for i in range(game_field.rows):
        for j in range(game_field.columns):
            if game_field.matrix[i][j] != matrix_field_copy.matrix[i][j]:
                return False

    return True


def copy_field(game_field, matrix_field_copy):
    """
        Копирование ячеек исходного игрового поля в поле-копию, для сравнения
        на испорченость матрицы после вызова функции игрока.
    """

    for i in range(game_field.rows):
        for j in range(game_field.columns):
            matrix_field_copy.matrix[i][j] = game_field.matrix[i][j]

    return matrix_field_copy


def scoring(game_field):
    """
        Подсчёт итоговой суммы очков игрока.
    """

    score = 0
    for i in range(game_field.rows):
        for j in range(game_field.columns):
            score += game_field.matrix[i][j]

    return score


def print_field(game_field, player_name, score, field_size):
    """
        Печать итогового состояния игрового поля и количество набранных очков.
    """

    print(f"PLAYER: {player_name} SCORE: {score}")

    for i in range(field_size):
        for j in range(field_size):
            print(game_field.matrix[i][j], end="\t")

        print("")


def ctypes_wrapper(player_lib, move, game_field):
    """
        Обертка для отловки segmentation fault.
    """

    move.value = player_lib.teen48game(game_field).decode('utf-8')


def start_teen48game_competition(players_info, field_size):
    """
        Создание игрового поля и запуск игры для каждого
        игрока, подсчёт его очков. Если количество очков менее, чем
        было набрано в прошлый раз, то очки не обновляются.
    """

    if field_size == 4:
        utils.redirect_ctypes_stdout()

    results = []

    for player in players_info:
        if player[0] == "NULL":
            results.append(utils.NO_RESULT)
            continue

        player_lib = ctypes.CDLL(player[0])
        player_lib.teen48game.argtypes = [Matrix]
        player_lib.teen48game.restype = ctypes.c_char

        game_field = Matrix(field_size, field_size)
        game_field_copy = Matrix(field_size, field_size)

        fill_random_cell(game_field.matrix, get_random_numb(), game_field.rows, game_field.columns)
        fill_random_cell(game_field.matrix, get_random_numb(), game_field.rows, game_field.columns)
        game_is_end = False
        prev_move = "_"

        while not game_is_end:
            copy_field(game_field, game_field_copy)

            move = utils.call_libary(
                player_lib, ctypes_wrapper, ctypes.c_wchar, utils.CHAR_SEGFAULT, game_field
            )

            game_field, is_done = make_move(move, game_field)

            if is_done:
                rand_numb = get_random_numb()
                fill_random_cell(game_field.matrix, rand_numb, game_field.rows, game_field.columns)

            game_is_end = check_end_game(game_field)

            if move == utils.CHAR_SEGFAULT:
                print("▼ This player caused segmentation fault. ▼")
                game_is_end = True

            if prev_move == move and not is_done:
                print(f"Two identical moves that do not change the field. Move: {move}")
                game_is_end = True

            prev_move = move

        score = scoring(game_field)
        results.append(score if score > player[1] else player[1])
        print_field(game_field, utils.parsing_name(player[0]), score, field_size)

    return results

if __name__ == "__main__":
    start_teen48game_competition([("games/teen48/teen48lib.so", 0), ("NULL", 1000)], 4)
