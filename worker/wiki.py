""" GitLab Wiki handling module. """


import pickle
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

NO_RESULT = 1337
NO_RESULT_PREC = "1337.000000000"
MSG = "Отсутствует стратегия"
OUTPUT_PARAMS = (NO_RESULT, MSG, NO_RESULT_PREC)

POS_CHANGE = ("🔺", "🔻")


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
        rec[sort_keys[0]] = f"{str(rec[sort_keys[0]])}/1"

        if rec[sort_keys[1]] == f"{output_params[2]}±{output_params[2]}":
            rec[sort_keys[1]] = output_params[1]

    return new


def print_table(head, theme, columns, results, compet):
    """ Print table with specified head. """

    try:
        results_dump = open(f"tbdump_{compet}.obj", "rb")
        results_old = pickle.load(results_dump)
    except FileNotFoundError:
        results_old = []

    res = theme + head

    prize = {1: "🥇", 2: "🥈", 3: "🥉"}

    num = 1
    for i in range(len(results)):
        place = prize.setdefault(num, str(num))

        for j in range(len(results_old)):
            if (results[i][1] == results_old[j][1]):
                if i > j:
                    place += f"{POS_CHANGE[1]}-{i - j}"
                elif i < j:
                    place += f"{POS_CHANGE[0]}+{j - i}"

        res += f"|{place}|"
        for field in range(columns - 1):
            res += f"{results[i][field]}|"
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
            "**SPLIT Время**|**Последнее обновление**|\n" \
            "|---|---|---|---|---|---|\n"
        strtok_head = "|**№**|**ФИ Студента**|**GitLab ID**|**STRTOK Тесты**|" \
            "**STRTOK Время**|**Последнее обновление**|\n" \
            "|---|---|---|---|---|---|\n"

        sorted_split = form_table(
            results, STRTOK_REMOVABLE, SORT_KEYS, OUTPUT_PARAMS)
        sorted_strtok = form_table(
            results, SPLIT_REMOVABLE, SORT_KEYS, OUTPUT_PARAMS)

        res += print_table(split_head, split_theme,
                           STRG_TABLE_WIDTH, sorted_split, "split")
        res += print_table(strtok_head, strtok_theme,
                           STRG_TABLE_WIDTH, sorted_strtok, "strtok")

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    res += f"\n**Обновлено:** {date} **МСК**"

    for key in games_keys:
        if game in key:
            update_page(project, games.get(key), key, res)

    split_dump = open("tbdump_split.obj", "wb")
    pickle.dump(sorted_split, split_dump)

    strtok_dump = open("tbdump_strtok.obj", "wb")
    pickle.dump(sorted_strtok, strtok_dump)
