""" Worker for IU7Games project. """


import gitlab


def create_page(instance, project_id, title, content):
    """ Create Wiki page. """

    project = instance.projects.get(project_id)
    page = project.wikis.create(
        {
            "title": title,
            "content": content
        }
    )


def update_page(instance, project_id, page_slug, title, content):
    """ Update Wiki page. """

    project = instance.projects.get(project_id)
    page = project.wikis.get(page_slug)
    page.title = title
    page.content = content
    page.save()


def delete_page(instance, project_id, page_slug):
    """ Delete Wiki page. """

    project = instance.projects.get(project_id)
    page = project.wikis.get(page_slug)
    page.delete()


def worker():
    """ API Worker to collect students' repos' artifacts. """

    games = {
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard"
    }
    games_keys = games.keys()
    games_content = "Game Leaderboard"

    gl = gitlab.Gitlab.from_config("gitiu7", ["./api_config.cfg"])
    gl.auth()

    for key in games_keys:
        create_page(gl, 2546, key, games_content)


if __name__ == "__main__":
    worker()
