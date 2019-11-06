""" GitLab Wiki handling module. """


from datetime import datetime

STRGAME_TABLE = 7

SPLIT_COL = 3
STRTOK_COL = 5
NO_RESULT = 100.0


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


def by_split(student):
    """ Key to sort by split results. """

    if isinstance(student[SPLIT_COL], float):
        return student[SPLIT_COL]

    return NO_RESULT


def by_strtok(student):
    """ Key to sort by strtok results. """

    if isinstance(student[STRTOK_COL], float):
        return student[STRTOK_COL]

    return NO_RESULT


def print_table(head, theme, columns, results):
    """ Print table with specified head. """

    res = theme + head

    num = 1
    for student in results:
        res += "|{0}|".format(num)
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

        sorted_split = sorted(results, key=by_split)
        res += print_table(head, split_theme, STRGAME_TABLE, sorted_split)

        sorted_strtok = sorted(results, key=by_strtok)
        res += print_table(head, strtok_theme, STRGAME_TABLE, sorted_strtok)

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    res += "\n**Обновлено:** {0} **МСК**".format(date)

    for key in games_keys:
        if game in key:
            update_page(project, games.get(key), key, res)
