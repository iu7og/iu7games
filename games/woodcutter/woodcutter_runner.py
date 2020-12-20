"""
    ===== W00DCUTT3R RUNNER v.1.0.a =====

    Copyright (C) 2019 - 2020 IU7Games Team.

    - Данный скрипт предназначен для проведения
      игры woodcutter. Правила игры:

    - Имеется дерево с отмеченными вершинами (корнями).
      За ход игрок разрубает ветку (стирает ребро),
      причем из двух получившихся компонент связности остается
      только та, которая содержит корень - остальная отваливается
      вместе с корнем. Проигрывает тот, кто не может сделать ход.

    - В соревновании принимают участие функции, имеющие следующую
      сигнатуру:

    - int woodcutter(int **tree, const int size)

    - int **tree - дерево, заданное матрицей смежности.
    - const int size - число вершин в дереве.

    - Возвращаемое значение: порядковый номер ячейки
      в матрице tree (tree[0][2] = 0 * size + 2 = 2)

"""

import ctypes
from random import randint, choice
from dataclasses import dataclass
import games.utils.utils as utils

SAMPLE_PATH = utils.Constants.sample_path + "/woodcutter.c"


@dataclass
class Woodcutter:
    """
        Константы игры woodcutter.
    """

    max_count_nodes = 20
    min_count_nodes = 10

    connected = 1
    not_connected = 0

    player_one_win = 1
    player_two_win = 2

    spaces = 30


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
        Запись и подсчет очков в результирующий массив points.
    """

    if round_info == Woodcutter.player_one_win:
        player1_result = 1
        player2_result = 0
    else:
        player1_result = 0
        player2_result = 1

    pts1 = points[player1_index]
    pts2 = points[player2_index]
    points[player1_index] = int(
        calculate_elo_rating(pts1, pts2, player1_result))
    points[player2_index] = int(
        calculate_elo_rating(pts2, pts1, player2_result))

    return points


def start_game_print(player1, player2):
    """
        Информация о начале раунда.
    """

    print(
        "GAME",
        utils.parsing_name(player1), "VS",
        utils.parsing_name(player2)
    )


def end_game_print(player, info):
    """
        Печать результатов раунда.
    """

    print(
        utils.parsing_name(player), info, "\n",
        "=" * Woodcutter.spaces, sep=""
    )


def print_results(points, players_info, players_amount):
    """
        Печать результатов в виде:
        ИГРОК : ОЧКИ
    """

    for i in range(players_amount):
        if players_info[i][0] != "NULL":
            print("PLAYER", utils.parsing_name(
                players_info[i][0]), "POINTS:", points[i])


def print_tree(tree, size, player_name):
    """
        Печать матрицы смежности, описывающей дерево.
    """

    print(utils.parsing_name(player_name), "player move: ")

    frame = "┏" + "━" * size + "┓"
    print(f"\033[30m{frame}\033[0m")

    for i in range(size):
        print("\033[30m┃", end="")
        for j in range(size):
            if tree[i][j] == Woodcutter.connected:
                print(f"\033[32m{tree[i][j]}\033[0m", end="")
            else:
                print(f"\033[36m{tree[i][j]}\033[0m", end="")
        print("\033[30m┃")

    frame = "┗" + "━" * size + "┛"
    print(f"\033[30m{frame}\033[0m")


def check_win(tree, size):
    """
        Проверка дерева на победу одного из игроков.
    """

    for k in range(size):
        if tree[k][k]:
            root_edges = 0
            for i in range(size):
                if tree[k][i] and k != i:
                    root_edges += 1
                    break
            if root_edges:
                return False

    return True


def delete_node(node, tree, size):
    """
        Удаление вершины в дереве.
    """

    for i in range(size):
        tree[i][node] = Woodcutter.not_connected
        tree[node][i] = Woodcutter.not_connected


def bfs(node, tree, size):
    """
        Поиск в ширину в дереве.
    """

    distances = [-1] * size
    distances[node] = 0

    queue = [node]
    qstart = 0

    while qstart < len(queue):
        top = queue[qstart]
        qstart += 1

        for i in range(size):
            if tree[top][i] and distances[i] == -1:
                distances[i] = distances[top] + 1
                queue.append(i)

    return distances


def connected_with_root(node, tree, size):
    """
        Функция проверки вершины:
        соединена ли вершина с корнем.
    """

    distances = bfs(node, tree, size)

    for i in range(size):
        if tree[i][i] or distances[i]:
            return True

    return False


def make_move(tree, move, size):
    """
        Ход игрока.
    """

    row_move = move // size
    column_move = move % size

    tree[row_move][column_move] = Woodcutter.not_connected
    tree[column_move][row_move] = Woodcutter.not_connected

    for i in range(size):
        if not connected_with_root(i, tree, size):
            delete_node(i, tree, size)

    return tree


def check_move_correctness(tree, tree_copy, move, size, player):
    """
        Проверка на корректность присланного игроком хода и
        на испорченость дерева стратегией игрока.
    """

    if move == utils.Error.segfault:
        print("▼ This player caused segmentation fault. ▼")
        return False

    str_tree = ""

    for i in range(size):
        for j in range(size):
            str_tree += str(tree[i][j])

    memory_leak_check_res = utils.memory_leak_check(
        SAMPLE_PATH, player,
        [
            str_tree,
            str(size)
        ]
    )

    if memory_leak_check_res:
        print("▼ This player caused memory leaks. ▼")
        return False

    row_move = move // size
    column_move = move % size
    min_border = 0
    max_border = size * size + size

    if (row_move == column_move or move > max_border \
         or move < min_border):
        return False

    for i in range(size):
        for j in range(size):
            if tree[i][j] != tree_copy[i][j]:
                return False

    return True


def ctypes_wrapper(player_lib, move, tree, count_nodes):
    """
        Обертка для отловки segmentation fault.
    """

    move.value = player_lib.woodcutter(tree, count_nodes)


def woodcutter_round(player1_lib, player2_lib, tree, size, players_names):
    """
        Запуск одного раунда для двух игроков.
    """

    start_game_print(*players_names)

    tree_copy = create_tree(size)
    copy_tree(tree, tree_copy, size)

    while not check_win(tree, size):

        move = utils.call_libary(
            player1_lib, ctypes_wrapper, 'i', utils.Error.segfault,
            tree, size)

        if not check_move_correctness(tree, tree_copy, move, size, players_names[0]):
            end_game_print(players_names[0], " CHEATING")
            return Woodcutter.player_two_win

        tree = make_move(tree, move, size)
        copy_tree(tree, tree_copy, size)
        print_tree(tree, size, players_names[0])

        if check_win(tree, size):
            end_game_print(players_names[0], " WIN")
            return Woodcutter.player_one_win

        move = utils.call_libary(
            player2_lib, ctypes_wrapper, 'i', utils.Error.segfault,
            tree, size)

        if not check_move_correctness(tree, tree_copy, move, size, players_names[1]):
            end_game_print(players_names[1], " CHEATING")
            return Woodcutter.player_one_win

        tree = make_move(tree, move, size)
        copy_tree(tree, tree_copy, size)
        print_tree(tree, size, players_names[1])

        if check_win(tree, size):
            end_game_print(players_names[1], " WIN")
            return Woodcutter.player_two_win


def copy_tree(tree, tree_copy, size):
    """
        Копирование дерева.
    """

    for i in range(size):
        for j in range(size):
            tree_copy[i][j] = tree[i][j]


def get_node(position, size):
    """
        Нахождение узла по позиции.
    """

    count_prev = 0
    count = 0
    row = 0

    while position > count - 1:
        count_prev = count
        count += size - 1 - row
        row += 1

    return row - 1, position - count_prev + row


def fill_tree(tree, size):
    """
        Заполнение матрицы смежности, описывающей дерево.
    """

    max_border = (size - 1) * size - 1 - size * (size + 1) // 2
    count_edges = randint(size // 2, max_border)
    count_roots = randint(1, size // 2)

    positions = list(range(max_border))

    for i in range(count_edges):
        position = choice(positions)
        positions.remove(position)

        row, column = get_node(position, size)
        tree[row][column] = Woodcutter.connected
        tree[column][row] = Woodcutter.connected

    positions = list(range(size))

    for i in range(count_roots):
        rote = choice(positions)
        positions.remove(rote)
        tree[rote][rote] = Woodcutter.connected


def create_tree(count_nodes):
    """
        Создание матрицы смежности, описывающей дерево.
    """

    c_int_p = ctypes.POINTER(ctypes.c_int)
    value_array = ctypes.c_int * count_nodes
    pointer_array = c_int_p * count_nodes
    matrix_pointer = pointer_array()

    for i in range(count_nodes):
        matrix_pointer[i] = value_array()
        for j in range(count_nodes):
            matrix_pointer[i][j] = 0

    return matrix_pointer


def start_woodcutter_game(players_info):
    """
        Функция запускает каждую стратегию с каждой.
    """

    utils.redirect_ctypes_stdout()

    points = [players_info[i][1] for i in range(len(players_info))]

    for i in range(len(players_info) - 1):
        if players_info[i][0] != "NULL":
            player_lib = ctypes.CDLL(players_info[i][0])

            for j in range(i + 1, len(players_info)):
                if players_info[j][0] != "NULL":
                    rival_lib = ctypes.CDLL(players_info[j][0])

                    count_nodes = randint(Woodcutter.min_count_nodes,
                                          Woodcutter.max_count_nodes)

                    tree = create_tree(count_nodes)
                    tree_copy = create_tree(count_nodes)

                    fill_tree(tree, count_nodes)
                    copy_tree(tree, tree_copy, count_nodes)

                    round_info = woodcutter_round(
                        player_lib,
                        rival_lib,
                        tree,
                        count_nodes,
                        (players_info[i][0], players_info[j][0])
                    )
                    points = scoring(points, i, j, round_info)

                    round_info = woodcutter_round(
                        rival_lib,
                        player_lib,
                        tree_copy,
                        count_nodes,
                        (players_info[j][0], players_info[i][0])
                    )
                    points = scoring(points, j, i, round_info)

                else:
                    points[j] = utils.GameResult.no_result
        else:
            points[i] = utils.GameResult.no_result

    print_results(points, players_info, len(players_info))

    return points


if __name__ == "__main__":
    start_woodcutter_game([("games/woodcutter/Dasha.so", 100),
                           ("games/woodcutter/Oleg.so", 50)])
