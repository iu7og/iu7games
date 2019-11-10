""" GitLab Wiki handling module. """


import operator
from datetime import datetime

STRG_TABLE_WIDTH = 7

SPLIT_TESTS_COL = 2
SPLIT_RES_COL = 3
STRTOK_TESTS_COL = 4
STRTOK_RES_COL = 5
NO_RESULT = 1337
TEST_COEF = 5


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
        head = "|**№**|**ФИ Студента**|**GitLab ID**|**SPLIT Тесты**|" \
            "**SPLIT Время**|**STRTOK Тесты**|**STRTOK Время**|\n" \
            "|---|---|---|---|---|---|---|\n"

        sorted_split = sorted(
            results, key=operator.itemgetter(SPLIT_RES_COL))
        sorted_split = sorted(
            sorted_split, key=operator.itemgetter(SPLIT_TESTS_COL), reverse=True)

        sorted_strtok = sorted(
            results, key=operator.itemgetter(STRTOK_RES_COL))
        sorted_strtok = sorted(
            sorted_strtok, key=operator.itemgetter(STRTOK_TESTS_COL), reverse=True)

        for rec in sorted_strtok:
            rec[SPLIT_TESTS_COL] = str(
                rec[SPLIT_TESTS_COL] // TEST_COEF) + "/20"
            rec[STRTOK_TESTS_COL] = str(
                rec[STRTOK_TESTS_COL] // TEST_COEF) + "/20"

            if rec[SPLIT_RES_COL] == NO_RESULT:
                rec[SPLIT_RES_COL] = "Отсутствует стратегия"
            if rec[STRTOK_RES_COL] == NO_RESULT:
                rec[STRTOK_RES_COL] = "Отсутствует стратегия"

        res += print_table(head, split_theme, STRG_TABLE_WIDTH, sorted_split)
        res += print_table(head, strtok_theme, STRG_TABLE_WIDTH, sorted_strtok)

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    res += "\n**Обновлено:** {0} **МСК**".format(date)

    for key in games_keys:
        if game in key:
            update_page(project, games.get(key), key, res)
