"""
    Модуль для работы над Wiki-страницами.
"""


import os
import pickle
import operator
from datetime import datetime
from copy import deepcopy

from jinja2 import Template

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


def get_date():
    """ 
        Получение текущей даты.
    """

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    return date


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


def handle_strgame(fresults, sresults):
    """
        Обновление таблицы для STRgame.
    """

    results_split = form_table(fresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                               "STRgame", "split")
    results_strtok = form_table(sresults, DOUBLE_SORT_KEYS, OUTPUT_PARAMS,
                                "STRgame", "strtok")
    tmp = open(os.path.abspath("templates/strgame.template")).read()
    page = Template(tmp).render(results_split=results_split,
                                results_strtok=results_strtok, date=get_date())

    return page


def handle_xogame(fresults, sresults):
    """
        Обновление таблицы для XOgame.
    """

    results_3x3 = form_table(fresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                             "XOgame", "3x3")
    results_5x5 = form_table(sresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                             "XOgame", "5x5")

    tmp = open(os.path.abspath("templates/xogame.template")).read()
    page = Template(tmp).render(results_3x3=results_3x3,
                                results_5x5=results_5x5, date=get_date())

    return page


def handle_teen48game(fresults, sresults):
    """
        Обновление таблицы для TEEN48game.
    """

    results_4x4 = form_table(fresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                             "TEEN48game", "4x4")
    results_6x6 = form_table(sresults, SINGLE_SORT_KEYS, OUTPUT_PARAMS,
                             "TEEN48game", "6x6")

    tmp = open(os.path.abspath("templates/teen48game.template")).read()
    page = Template(tmp).render(results_4x4=results_4x4,
                                results_6x6=results_6x6, date=get_date())

    return page


def update_wiki(project, game, fresults, sresults):
    """
        Обновление Wiki-страницы с обновленными результатами.
    """

    games = {
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard"
    }

    page = ""

    if game == "STRgame":
        page = handle_strgame(fresults, sresults)
    elif game == "XOgame":
        page = handle_xogame(fresults, sresults)
    elif game == "TEEN48game":
        page = handle_teen48game(fresults, sresults)

    for key in games:
        if game in key:
            update_page(project, games.get(key), key, page)
