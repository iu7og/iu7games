"""
    Модуль для работы над Wiki-страницами.
"""


import os
import pickle
import operator
from datetime import datetime
from copy import deepcopy
from functools import cmp_to_key

from jinja2 import Template
import intervals
import gitlab

DOUBLE_TESTS_COL = 3
DOUBLE_RES_COL = 4
DOUBLE_TIME_COL = 5
DOUBLE_SORT_KEYS = (DOUBLE_TESTS_COL, DOUBLE_RES_COL)

SINGLE_RES_COL = 3
SINGLE_TIME_COL = 4
SINGLE_SORT_KEYS = (SINGLE_RES_COL, )

GT = 1
LT = -1

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

    try:
        page = project.wikis.get(page_slug)
        page.title = title
        page.content = content
        page.save()
    except (gitlab.exceptions.GitlabHttpError, gitlab.exceptions.GitlabGetError):
        create_page(project, title, content)


def delete_page(project, page_slug):
    """
        Удаление Wiki-страницы.
    """

    page = project.wikis.get(page_slug)
    page.delete()


def get_date():
    """
        Получение текущей даты.
    """

    now = datetime.now()
    date = now.strftime("%H:%M:%S %d.%m.%Y")

    return date


def dispcmp(frec, srec):
    """
        Компаратор, учитывающий временное отклонение выполнения.
    """

    if frec[DOUBLE_RES_COL] < srec[DOUBLE_RES_COL]:
        return GT
    if frec[DOUBLE_RES_COL] > srec[DOUBLE_RES_COL]:
        return LT
    if frec[DOUBLE_RES_COL].overlaps(srec[DOUBLE_RES_COL]):
        if frec[DOUBLE_TIME_COL] < srec[DOUBLE_TIME_COL]:
            return GT
        return LT

    return GT


def equalcmp(frec, srec):
    """
        Компаратор, учитывающий равенство полученных очков.
    """

    if frec[SINGLE_RES_COL] < srec[SINGLE_RES_COL]:
        return GT
    if frec[SINGLE_RES_COL] > srec[SINGLE_RES_COL]:
        return LT
    if frec[SINGLE_RES_COL] == srec[SINGLE_RES_COL]:
        if frec[SINGLE_TIME_COL] < srec[SINGLE_TIME_COL]:
            return GT
        return LT

    return GT


def params_sort(results, sort_keys, output_params, game):
    """
        Сортировка результатов в зависимости от игры.
    """

    timedep_games = ["NUM63RSgame", "7EQUEENCEgame", "STRgame", "TR4V31game"]
    timedepless_games = ["XOgame", "TEEN48game"]

    if game in timedep_games:
        results = sorted(results, key=cmp_to_key(dispcmp), reverse=True)
        results = sorted(results, key=operator.itemgetter(sort_keys[0]))

        for rec in results:
            if rec[sort_keys[1]] == intervals.closed(1337, intervals.inf):
                rec[sort_keys[1]] = output_params[1]
            rec[DOUBLE_TIME_COL] = rec[DOUBLE_TIME_COL].strftime(
                "%H:%M:%S %d.%m.%Y")

    if game in timedepless_games:
        results = sorted(results, key=cmp_to_key(equalcmp))

        for rec in results:
            if rec[sort_keys[0]] == output_params[0]:
                if game == "XOgame":
                    rec[sort_keys[0]] = 1000
                if game == "TEEN48game":
                    rec[sort_keys[0]] = 0
            rec[SINGLE_TIME_COL] = rec[SINGLE_TIME_COL].strftime(
                "%H:%M:%S %d.%m.%Y")

    return results


def form_table(results, sort_keys, output_params, game, compet):
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

    return results_new


def handle_num63rsgame(fresults):
    """
        Обновление таблицы для NUM63RSgame.
    """

    results = form_table(fresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                         "NUM63RSgame", "")

    with open(os.path.abspath("templates/num63rsgame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results=results, date=get_date())

    return page


def handle_7equeencegame(fresults):
    """
        Обновление таблицы для 7EQUEENCEgame.
    """

    results = form_table(fresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                         "7EQUEENCEgame", "")

    with open(os.path.abspath("templates/7equeencegame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results=results, date=get_date())

    return page


def handle_xogame(fresults, sresults):
    """
        Обновление таблицы для XOgame.
    """

    results_3x3 = form_table(fresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                             "XOgame", "3x3")
    results_5x5 = form_table(sresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                             "XOgame", "5x5")

    with open(os.path.abspath("templates/xogame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results_3x3=results_3x3,
                                results_5x5=results_5x5, date=get_date())

    return page


def handle_strgame(fresults, sresults):
    """
        Обновление таблицы для STRgame.
    """

    results_split = form_table(fresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                               "STRgame", "split")
    results_strtok = form_table(sresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                                "STRgame", "strtok")

    with open(os.path.abspath("templates/strgame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results_split=results_split,
                                results_strtok=results_strtok, date=get_date())

    return page


def handle_teen48game(fresults, sresults):
    """
        Обновление таблицы для TEEN48game.
    """

    results_4x4 = form_table(fresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                             "TEEN48game", "4x4")
    results_6x6 = form_table(sresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                             "TEEN48game", "6x6")

    with open(os.path.abspath("templates/teen48game.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results_4x4=results_4x4,
                                results_6x6=results_6x6, date=get_date())

    return page


def handle_tr4v31game(fresults):
    """
        Обновление таблицы для TR4V31game.
    """

    results = form_table(fresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                         "TR4V31game", "")

    with open(os.path.abspath("templates/tr4v31game.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results=results, date=get_date())

    return page


def update_wiki(project, game, fresults, sresults):
    """
        Обновление Wiki-страницы с обновленными результатами.
    """

    games = {
        "NUM63RSgame Leaderboard": "NUM63RSgame-Leaderboard",
        "7EQUEENCEgame Leaderboard": "7EQUEENCEgame-Leaderboard",
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard",
        "TR4V31game Leaderboard": "TR4V31game-Leaderboard",
        "NUM63RSgame_practice Leaderboard": "NUM63RSgame_practice-Leaderboard",
        "7EQUEENCEgame_practice Leaderboard": "7EQUEENCEgame_practice-Leaderboard",
        "XOgame_practice Leaderboard": "XOgame_practice-Leaderboard",
        "STRgame_practice Leaderboard": "STRgame_practice-Leaderboard",
        "TEEN48game_practice Leaderboard": "TEEN48game_practice-Leaderboard",
        "TR4V31game_practice Leaderboard": "TR4V31game_practice-Leaderboard"
    }

    page = ""

    if game.startswith("NUM63RSgame"):
        page = handle_num63rsgame(fresults)
    elif game.startswith("7EQUEENCEgame"):
        page = handle_7equeencegame(fresults)
    elif game.startswith("XOgame"):
        page = handle_xogame(fresults, sresults)
    elif game.startswith("STRgame"):
        page = handle_strgame(fresults, sresults)
    elif game.startswith("TEEN48game"):
        page = handle_teen48game(fresults, sresults)
    elif game.startswith("TR4V31game"):
        page = handle_tr4v31game(fresults)

    for key in games:
        if game in key:
            update_page(project, games.get(key), key, page)
