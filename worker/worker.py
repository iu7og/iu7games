""" Worker for IU7Games project. """


import gitlab
import os
import subprocess


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


def collect_artifacts(instance, project_id, job_id):
    """ Collect job's artifacts. """

    project = instance.projects.get(project_id)
    job = project.jobs.get(job_id)

    ziparts = str(project_id) + str(job_id) + "artifacts.zip"
    with open(ziparts, "wb") as f:
        job.artifacts(streamed=True, action=f.write)


def worker():
    """ API Worker to collect students' repos' artifacts. """

    games = {
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard"
    }
    games_keys = games.keys()
    games_content = "Game Leaderboard"

    iu7games_id = 2546
    iu7cprogsems_id = 2303

    gl = gitlab.Gitlab.from_config("gitiu7", ["./api_config.cfg"])
    gl.auth()

    """
    for key in games_keys:
        create_page(gl, iu7games_id, key, games_content)
    collect_artifacts(gl, iu7cprogsems_id, 70250)
    """


if __name__ == "__main__":
    worker()
