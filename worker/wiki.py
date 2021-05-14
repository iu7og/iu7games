"""
    Модуль для работы над Wiki-страницами.
"""


import os
import pickle
import operator
from datetime import datetime
from copy import deepcopy
from functools import cmp_to_key
from dataclasses import dataclass

from jinja2 import Template
import intervals
import gitlab


@dataclass
class Wiki:
    """
        Константы wiki.
    """
    double_tests_col = 3
    double_res_col = 4
    double_time_col = 5
    double_sort_keys = (double_tests_col, double_res_col)

    single_res_col = 3
    single_time_col = 4
    single_sort_keys = (single_res_col, )

    gt = 1
    lt = -1

    no_result = -1337
    msg = "Отсутствует стратегия"
    output_params = (no_result, msg)

    pos_change = ("🔺", "🔻")
    sign = ("✅", "❌")


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

    if frec[Wiki.double_res_col] < srec[Wiki.double_res_col]:
        return Wiki.gt
    if frec[Wiki.double_res_col] > srec[Wiki.double_res_col]:
        return Wiki.lt
    if frec[Wiki.double_res_col].overlaps(srec[Wiki.double_res_col]):
        if frec[Wiki.double_time_col] < srec[Wiki.double_time_col]:
            return Wiki.gt
        return Wiki.lt

    return Wiki.gt


def equalcmp(frec, srec):
    """
        Компаратор, учитывающий равенство полученных очков.
    """

    if frec[Wiki.single_res_col] < srec[Wiki.single_res_col]:
        return Wiki.gt
    if frec[Wiki.single_res_col] > srec[Wiki.single_res_col]:
        return Wiki.lt
    if frec[Wiki.single_res_col] == srec[Wiki.single_res_col]:
        if frec[Wiki.single_time_col] < srec[Wiki.single_time_col]:
            return Wiki.gt
        return Wiki.lt

    return Wiki.gt


def params_sort(results, sort_keys, output_params, game):
    """
        Сортировка результатов в зависимости от игры.
    """

    timedep_games = ("NUM63RSgame", "7EQUEENCEgame", "STRgame", "TR4V31game")
    timedepless_games = ("XOgame", "TEEN48game", "T3TR15game", "R3463NTgame",
                         "W00DCUTT3Rgame")

    if game in timedep_games:
        results = sorted(results, key=cmp_to_key(dispcmp), reverse=True)
        results = sorted(results, key=operator.itemgetter(sort_keys[0]))

        for rec in results:
            if rec[sort_keys[1]] == intervals.closed(1337, intervals.inf):
                rec[sort_keys[1]] = output_params[1]
            rec[Wiki.double_time_col] = rec[Wiki.double_time_col].strftime(
                "%H:%M:%S %d.%m.%Y")

    if game in timedepless_games:
        results = sorted(results, key=cmp_to_key(equalcmp))

        for rec in results:
            if rec[sort_keys[0]] == output_params[0]:
                if game in ("XOgame", "W00DCUTT3Rgame"):
                    rec[sort_keys[0]] = 1000
                if game in ("TEEN48game", "T3TR15game", "R3463NTgame"):
                    rec[sort_keys[0]] = 0
            rec[Wiki.single_time_col] = rec[Wiki.single_time_col].strftime(
                "%H:%M:%S %d.%m.%Y")

    return results


def form_table(results, sort_keys, output_params, game, compet):
    """
        Формирование таблицы.
    """

    results_new = deepcopy(results)
    results_new = params_sort(results_new, sort_keys, output_params, game)

    results_old = []

    if os.path.exists(f"tbdump_{game.lower()}{compet}.obj"):
        with open(f"tbdump_{game.lower()}{compet}.obj", "rb") as results_dump:
            results_old = pickle.load(results_dump)

    prize = {1: "🥇", 2: "🥈", 3: "🥉"}

    for ind_new, new_rec in enumerate(results_new):
        place = prize.setdefault(ind_new + 1, str(ind_new + 1))

        for ind_old, old_rec in enumerate(results_old):
            if new_rec[1] == old_rec[1]:
                if ind_new > ind_old:
                    place += f"{Wiki.pos_change[1]}-{ind_new - ind_old}"
                elif ind_new < ind_old:
                    place += f"{Wiki.pos_change[0]}+{ind_old - ind_new}"

        new_rec[0] = place

    with open(f"tbdump_{game.lower()}{compet}.obj", "wb") as results_dump:
        pickle.dump(results_new, results_dump)

    if sort_keys == Wiki.double_sort_keys:
        for user in results_new:
            if user[4] != output_params[1]:
                user[4] = "[{0:.7f}, {1:.7f}]".format(user[4].lower() * 10 ** 7,
                                                       user[4].upper() * 10 ** 7)

    return results_new


def handle_num63rsgame(fresults):
    """
        Обновление таблицы для NUM63RSgame.
    """

    results = form_table(fresults, Wiki.double_sort_keys, Wiki.output_params,
                         "NUM63RSgame", "")

    with open(os.path.abspath("templates/num63rsgame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results=results, date=get_date())

    return page


def handle_7equeencegame(fresults):
    """
        Обновление таблицы для 7EQUEENCEgame.
    """

    results = form_table(fresults, Wiki.double_sort_keys, Wiki.output_params,
                         "7EQUEENCEgame", "")

    with open(os.path.abspath("templates/7equeencegame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results=results, date=get_date())

    return page


def handle_xogame(fresults, sresults):
    """
        Обновление таблицы для XOgame.
    """

    results_3x3 = form_table(fresults, Wiki.single_sort_keys, Wiki.output_params,
                             "XOgame", "_3x3")
    results_5x5 = form_table(sresults, Wiki.single_sort_keys, Wiki.output_params,
                             "XOgame", "_5x5")

    with open(os.path.abspath("templates/xogame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results_3x3=results_3x3,
                                results_5x5=results_5x5, date=get_date())

    return page


def handle_strgame(fresults, sresults):
    """
        Обновление таблицы для STRgame.
    """

    results_split = form_table(fresults, Wiki.double_sort_keys, Wiki.output_params,
                               "STRgame", "_split")
    results_strtok = form_table(sresults, Wiki.double_sort_keys, Wiki.output_params,
                                "STRgame", "_strtok")

    with open(os.path.abspath("templates/strgame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results_split=results_split,
                                results_strtok=results_strtok, date=get_date())

    return page


def handle_teen48game(fresults, sresults):
    """
        Обновление таблицы для TEEN48game.
    """

    results_4x4 = form_table(fresults, Wiki.single_sort_keys, Wiki.output_params,
                             "TEEN48game", "_4x4")
    results_6x6 = form_table(sresults, Wiki.single_sort_keys, Wiki.output_params,
                             "TEEN48game", "_6x6")

    with open(os.path.abspath("templates/teen48game.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results_4x4=results_4x4,
                                results_6x6=results_6x6, date=get_date())

    return page


def handle_tr4v31game(fresults):
    """
        Обновление таблицы для TR4V31game.
    """

    results = form_table(fresults, Wiki.double_sort_keys, Wiki.output_params,
                         "TR4V31game", "")

    with open(os.path.abspath("templates/tr4v31game.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results=results, date=get_date())

    return page


def handle_t3tr15game(fresults):
    """
        Обновление таблицы для T3TR15game.
    """

    results = form_table(fresults, Wiki.single_sort_keys, Wiki.output_params,
                         "T3TR15game", "")

    with open(os.path.abspath("templates/t3tr15game.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results=results, date=get_date())

    return page


def handle_r3463ntgame(fresults, sresults):
    """
        Обновление таблицы для R3463NTgame.
    """

    results_10x10 = form_table(fresults, Wiki.single_sort_keys, Wiki.output_params,
                               "R3463NTgame", "_10x10")
    results_20x20 = form_table(sresults, Wiki.single_sort_keys, Wiki.output_params,
                               "R3463NTgame", "_20x20")

    with open(os.path.abspath("templates/r3463ntgame.template")) as template:
        tmp = template.read()

    page = Template(tmp).render(results_10x10=results_10x10,
                                results_20x20=results_20x20, date=get_date())

    return page


def handle_w00dcutt3rgame(fresults):
    """
        Обновление таблицы для W00DCUTT3Rgame.
    """

    results = form_table(fresults, Wiki.single_sort_keys, Wiki.output_params,
                         "W00DCUTT3Rgame", "")

    with open(os.path.abspath("templates/w00dcutt3rgame.template")) as template:
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
        "T3TR15game Leaderboard": "T3TR15game-Leaderboard",
        "R3463NTgame Leaderboard": "R3463NTgame-Leaderboard",
        "W00DCUTT3Rgame Leaderboard": "W00DCUTT3Rgame-Leaderboard",
        "NUM63RSgame_practice Leaderboard": "NUM63RSgame_practice-Leaderboard",
        "7EQUEENCEgame_practice Leaderboard": "7EQUEENCEgame_practice-Leaderboard",
        "XOgame_practice Leaderboard": "XOgame_practice-Leaderboard",
        "STRgame_practice Leaderboard": "STRgame_practice-Leaderboard",
        "TEEN48game_practice Leaderboard": "TEEN48game_practice-Leaderboard",
        "TR4V31game_practice Leaderboard": "TR4V31game_practice-Leaderboard",
        "T3TR15game_practice Leaderboard": "T3TR15game_practice-Leaderboard",
        "R3463NTgame_practice Leaderboard": "R3463NTgame_practice-Leaderboard",
        "W00DCUTT3Rgame_pratice Leaderboard": "W00DCUTT3Rgame_practice-Leaderboard"
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
    elif game.startswith("T3TR15game"):
        page = handle_t3tr15game(fresults)
    elif game.startswith("R3463NTgame"):
        page = handle_r3463ntgame(fresults, sresults)
    elif game.startswith("W00DCUTT3Rgame"):
        page = handle_w00dcutt3rgame(fresults)

    for key in games:
        if game in key:
            update_page(project, games.get(key), key, page)
