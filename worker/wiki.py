"""
    Модуль для работы над Wiki-страницами.
"""


import os
import pickle
import operator
from datetime import datetime
from copy import deepcopy

import markdown_table

DOUBLE_TESTS_COL = 3
DOUBLE_RES_COL = 4
DOUBLE_SORT_KEYS = (DOUBLE_TESTS_COL, DOUBLE_RES_COL)

SINGLE_RES_COL = 3
SINGLE_SORT_KEYS = (SINGLE_RES_COL, )

NO_RESULT = -1337
MSG = "Отсутствует стратегия"
OUTPUT_PARAMS = (NO_RESULT, MSG)

POS_CHANGE = ("🔺", "🔻")
SIGN = ("✅", "❌")


def create_page(project, title, content):
    """
        Создание Wiki-страницы.
    """

    project.wikis.create(
        {
            "title": title,
            "content": content
        }
    )


def update_page(project, page_slug, title, content):
    """
        Обновление Wiki-страницы.
    """

    page = project.wikis.get(page_slug)
    page.title = title
    page.content = content
    page.save()


def delete_page(project, page_slug):
    """
        Удаление Wiki-страницы.
    """

    page = project.wikis.get(page_slug)
    page.delete()


def params_sort(results, sort_keys, output_params, game):
    """
        Сортировка результатов в зависимости от игры.
    """

    if game == "STRgame":
        results = sorted(results, key=operator.itemgetter(sort_keys[1]))
        results = sorted(results, key=operator.itemgetter(sort_keys[0]))

        for rec in results:
            if rec[sort_keys[1]] == str(output_params[0])[1:]:
                rec[sort_keys[1]] = output_params[1]

    if game == "XOgame" or game == "TEEN48game":
        results = sorted(results, key=operator.itemgetter(
            sort_keys[0]), reverse=True)

        for rec in results:
            if rec[sort_keys[0]] == output_params[0]:
                if game == "XOgame":
                    rec[sort_keys[0]] = 1000
                if game == "TEEN48game":
                    rec[sort_keys[0]] = 0

    return results


def form_table(results, sort_keys, output_params, game, compet, theme, head):
    """
        Формирование таблицы.
    """

    results_new = deepcopy(results)
    results_new = params_sort(results_new, sort_keys, output_params, game)

    results_old = []

    if os.path.exists(f"tbdump_{game.lower()}_{compet}.obj"):
        results_dump = open(f"tbdump_{game.lower()}_{compet}.obj", "rb")
        results_old = pickle.load(results_dump)

    prize = {1: "🥇", 2: "🥈", 3: "🥉"}

    for ind_new, new_rec in enumerate(results_new):
        place = prize.setdefault(ind_new + 1, str(ind_new + 1))

        for ind_old, old_rec in enumerate(results_old):
            if new_rec[1] == old_rec[1]:
                if ind_new > ind_old:
                    place += f"{POS_CHANGE[1]}-{ind_new - ind_old}"
                elif ind_new < ind_old:
                    place += f"{POS_CHANGE[0]}+{ind_old - ind_new}"

        new_rec[0] = place

    results_dump = open(f"tbdump_{game.lower()}_{compet}.obj", "wb")
    pickle.dump(results_new, results_dump)

    results_new = [list(map(str, rec)) for rec in results_new]
    table = theme + str(markdown_table.Table(head, results_new)) + "\n"

    return table


def handle_strgame(fresults, sresults):
    """
        Обновление таблицы для STRgame.
    """

    split_theme = "# SPLIT\n\n"
    strtok_theme = "# STRTOK\n\n"
    str_head = ["**№**", "**ФИ Студента**", "**GitLab ID**", "**Тесты**",
                "**Результат**", "**Последнее обновление**"]

    res = form_table(fresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                     "STRgame", "split", split_theme, str_head) + \
        form_table(sresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                   "STRgame", "strtok", strtok_theme, str_head)

    return res


def handle_xogame(fresults, sresults):
    """
        Обновление таблицы для XOgame.
    """

    div_3x3_theme = "# 3X3 DIVISION\n\n"
    div_5x5_theme = "# 5X5 DIVISION\n\n"
    xo_head = ["**№**", "**ФИ Студента**", "**GitLab ID**",
               "**Очки**", "**Последнее обновление**"]

    res = form_table(fresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                     "XOgame", "3x3", div_3x3_theme, xo_head) + \
        form_table(sresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                   "XOgame", "5x5", div_5x5_theme, xo_head)

    return res


def handle_teen48game(fresults, sresults):
    """
        Обновление таблицы для TEEN48game.
    """

    div_4x4_theme = "# 4X4 DIVISION\n\n"
    div_6x6_theme = "# 6X6 DIVISION\n\n"
    teen48_head = ["**№**", "**ФИ Студента**", "**GitLab ID**",
                   "**Очки**", "**Последнее обновление**"]

    res = form_table(fresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                     "TEEN48game", "4x4", div_4x4_theme, teen48_head) + \
        form_table(sresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                   "TEEN48game", "6x6", div_6x6_theme, teen48_head)

    return res


def update_wiki(project, game, fresults, sresults):
    """
        Обновление Wiki-страницы с обновленными результатами.
    """

    games = {
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard"
    }

    res = ""

    if game == "STRgame":
        res = handle_strgame(fresults, sresults)
    elif game == "XOgame":
        res = handle_xogame(fresults, sresults)
    elif game == "TEEN48game":
        res = handle_teen48game(fresults, sresults)

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    res += f"\n**Обновлено:** {date} **МСК**"

    for key in games:
        if game in key:
            update_page(project, games.get(key), key, res)
