"""
    Модуль для работы над Wiki-страницами.
"""


import os
import pickle
import operator
from datetime import datetime
from copy import deepcopy

STRG_TABLE_WIDTH = 6

STRG_TESTS_COL = 2
STRG_RES_COL = 3
STRG_SORT_KEYS = (STRG_TESTS_COL, STRG_RES_COL)

SPLIT_TESTS_COL = 2
SPLIT_STRG_RES_COL = 3
SPLIT_REMOVABLE = (SPLIT_TESTS_COL, SPLIT_STRG_RES_COL)

STRTOK_TESTS_COL = 4
STRTOK_STRG_RES_COL = 5
STRTOK_REMOVABLE = (STRTOK_TESTS_COL, STRTOK_STRG_RES_COL)

XOG_TABLE_WIDTH = 5

XOG_RES_COL = 2
XOG_SORT_KEYS = (XOG_RES_COL, )

XOG_3X3_RES_COL = 2
XOG_5X5_RES_COL = 3

XOG_3X3_REMOVABLE = (XOG_5X5_RES_COL, XOG_5X5_RES_COL)
XOG_5X5_REMOVABLE = (XOG_3X3_RES_COL, XOG_3X3_RES_COL)

NO_RESULT = -1337
MSG = "Отсутствует стратегия"
OUTPUT_PARAMS = (NO_RESULT, MSG)

POS_CHANGE = ("🔺", "🔻")
STRG_RESULT = ("✅", "❌")


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


def fix_date(results):
    """
        Перемещение даты завершения job'ы в последний столбец таблицы.
    """

    for rec in results:
        job_date = rec.pop(2)
        rec.append(job_date)

    return results


def form_table(results, removable, sort_keys, output_params, game):
    """
        Предварительное формирование таблицы.
    """

    new = deepcopy(results)

    for rec in new:
        del rec[removable[0]:removable[1] + 1]

    if game == "STRgame":
        new = sorted(new, key=operator.itemgetter(sort_keys[1]))
        new = sorted(new, key=operator.itemgetter(sort_keys[0]))

        for rec in new:
            if rec[sort_keys[1]] == str(output_params[0])[1:]:
                rec[sort_keys[1]] = output_params[1]

    if game == "XOgame":
        new = sorted(new, key=operator.itemgetter(sort_keys[0]), reverse=True)

        for rec in new:
            if rec[sort_keys[0]] == output_params[0]:
                rec[sort_keys[0]] = 0

    return new


def print_table(head, theme, columns, results, compet):
    """
        Печать таблицы с предопределенной шапкой.
    """

    results_old = []

    if os.path.exists(f"tbdump_{compet}.obj"):
        results_dump = open(f"tbdump_{compet}.obj", "rb")
        results_old = pickle.load(results_dump)

    res = theme + head

    prize = {1: "🥇", 2: "🥈", 3: "🥉"}

    for ind_new, new in enumerate(results):
        place = prize.setdefault(ind_new + 1, str(ind_new + 1))

        for ind_old, old in enumerate(results_old):
            if new[0] == old[0]:
                if ind_new > ind_old:
                    place += f"{POS_CHANGE[1]}-{ind_new - ind_old}"
                elif ind_new < ind_old:
                    place += f"{POS_CHANGE[0]}+{ind_old - ind_new}"

        res += f"|{place}|"
        for field in range(columns - 1):
            res += f"{new[field]}|"
        res += "\n"

    return res


def handle_strgame(results):
    """
        Обновление таблицы для STRgame.
    """

    res = ""

    split_theme = "# SPLIT\n\n"
    strtok_theme = "\n# STRTOK\n\n"
    str_head = "|**№**|**ФИ Студента**|**GitLab ID**|**Тесты**|"\
        "**Результат**|**Последнее обновление**|\n"\
        "|---|---|---|:---:|---|---|\n"

    sorted_split = form_table(
        results, STRTOK_REMOVABLE, STRG_SORT_KEYS, OUTPUT_PARAMS, "STRgame")
    sorted_strtok = form_table(
        results, SPLIT_REMOVABLE, STRG_SORT_KEYS, OUTPUT_PARAMS, "STRgame")

    res += print_table(str_head, split_theme,
                       STRG_TABLE_WIDTH, sorted_split, "split")
    res += print_table(str_head, strtok_theme,
                       STRG_TABLE_WIDTH, sorted_strtok, "strtok")

    split_dump = open("tbdump_split.obj", "wb")
    pickle.dump(sorted_split, split_dump)

    strtok_dump = open("tbdump_strtok.obj", "wb")
    pickle.dump(sorted_strtok, strtok_dump)

    return res


def handle_xogame(results):
    """
        Обновление таблицы для XOgame.
    """

    res = ""

    div_3x3_theme = "# 3X3 DIVISION\n\n"
    div_5x5_theme = "\n# 5X5 DIVISION\n\n"
    xo_head = "|**№**|**ФИ Студента**|**GitLab ID**|"\
        "**Очки**|**Последнее обновление**|\n"\
        "|---|---|---|:---:|---|\n"

    sorted_3x3 = form_table(
        results, XOG_3X3_REMOVABLE, XOG_SORT_KEYS, OUTPUT_PARAMS, "XOgame")
    sorted_5x5 = form_table(
        results, XOG_5X5_REMOVABLE, XOG_SORT_KEYS, OUTPUT_PARAMS, "XOgame")

    res += print_table(xo_head, div_3x3_theme,
                       XOG_TABLE_WIDTH, sorted_3x3, "xogame_3x3")
    res += print_table(xo_head, div_5x5_theme,
                       XOG_TABLE_WIDTH, sorted_5x5, "xogame_5x5")

    results_3x3_dump = open("tbdump_xogame_3x3.obj", "wb")
    pickle.dump(sorted_3x3, results_3x3_dump)

    results_5x5_dump = open("tbdump_xogame_5x5.obj", "wb")
    pickle.dump(sorted_5x5, results_5x5_dump)

    return res


def update_wiki(project, game, results):
    """
        Обновление Wiki-страницы с обновленными результатами.
    """

    games = {
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard"
    }

    res = ""

    results = fix_date(results)

    if game == "STRgame":
        res = handle_strgame(results)
    elif game == "XOgame":
        res = handle_xogame(results)

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    res += f"\n**Обновлено:** {date} **МСК**"

    for key in games:
        if game in key:
            update_page(project, games.get(key), key, res)
