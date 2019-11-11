""" GitLab Wiki handling module. """


import operator
from datetime import datetime
from copy import deepcopy

STRG_TABLE_WIDTH = 5

TESTS_COL = 2
RES_COL = 3
SORT_KEYS = (TESTS_COL, RES_COL)

SPLIT_TESTS_COL = 2
SPLIT_RES_COL = 3
SPLIT_REMOVABLE = (SPLIT_TESTS_COL, SPLIT_RES_COL)

STRTOK_TESTS_COL = 4
STRTOK_RES_COL = 5
STRTOK_REMOVABLE = (STRTOK_TESTS_COL, STRTOK_RES_COL)

TEST_COEF = 5
NO_RESULT = 1337
MSG = "Отсутствует стратегия"
OUTPUT_PARAMS = (TEST_COEF, NO_RESULT, MSG)


def create_page(project, title, content):
    """ Create Wiki page. """

    project.wikis.create(
        {
            "title": title,
            "content": content
        }
    )


def update_page(project, page_slug, title, content):
    """ Update Wiki page. """

    page = project.wikis.get(page_slug)
    page.title = title
    page.content = content
    page.save()


def delete_page(project, page_slug):
    """ Delete Wiki page. """

    page = project.wikis.get(page_slug)
    page.delete()


def form_table(results, removable, sort_keys, output_params):
    """ Preprinting table format. """

    new = deepcopy(results)

    for rec in new:
        del rec[removable[0]:removable[1] + 1]

    new = sorted(new, key=operator.itemgetter(sort_keys[1]))
    new = sorted(new, key=operator.itemgetter(sort_keys[0]), reverse=True)

    for rec in new:
        rec[sort_keys[0]] = str(rec[sort_keys[0]] // output_params[0]) + "/20"

        if rec[sort_keys[1]] == output_params[1]:
            rec[sort_keys[1]] = output_params[2]

    return new


def print_table(head, theme, columns, results):
    """ Print table with specified head. """

    res = theme + head

    prize = {1: "🥇", 2: "🥈", 3: "🥉"}

    num = 1
    for student in results:
        place = prize.setdefault(num, num)
        res += "|{0}|".format(place)
        for field in range(columns - 1):
            res += "{0}|".format(student[field])
        num += 1
        res += "\n"

    return res


def update_wiki(project, game, results):
    """ Update Wiki pages with new games results. """

    games = {
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard"
    }
    games_keys = games.keys()

    res = ""

    if game == "STRgame":
        split_theme = "# SPLIT\n\n"
        strtok_theme = "\n# STRTOK\n\n"
        split_head = "|**№**|**ФИ Студента**|**GitLab ID**|**SPLIT Тесты**|" \
            "**SPLIT Время**|\n" \
            "|---|---|---|---|---|\n"
        strtok_head = "|**№**|**ФИ Студента**|**GitLab ID**|**STRTOK Тесты**|" \
            "**STRTOK Время**|\n" \
            "|---|---|---|---|---|\n"

        sorted_split = form_table(
            results, STRTOK_REMOVABLE, SORT_KEYS, OUTPUT_PARAMS)
        sorted_strtok = form_table(
            results, SPLIT_REMOVABLE, SORT_KEYS, OUTPUT_PARAMS)

        res += print_table(split_head, split_theme,
                           STRG_TABLE_WIDTH, sorted_split)
        res += print_table(strtok_head, strtok_theme,
                           STRG_TABLE_WIDTH, sorted_strtok)

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    res += "\n**Обновлено:** {0} **МСК**".format(date)

    for key in games_keys:
        if game in key:
            update_page(project, games.get(key), key, res)
