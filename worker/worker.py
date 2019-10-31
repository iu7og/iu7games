""" Worker for IU7Games project. """


import gitlab
import os
import subprocess
import argparse


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


def get_group(instance, name):
    """ Get group by it's name. """

    groups = instance.groups.list(all=True)
    for group in groups:
        if group.name == name:
            return group

    return None


def get_group_projects(instance, group):
    """ Get group's projects. """

    group = instance.groups.get(group.id)
    projects = group.projects.list(all=True)

    return projects


def get_project(instance, group, name):
    """ Get project by it' name. """

    projects = get_group_projects(instance, group)
    for project in projects:
        if project.name == name:
            return instance.projects.get(project.id)

    return None


def get_last_success_job(project, ref):
    """ Get project's last success job by ref name. """

    jobs = project.jobs.list(all=True)
    for job in jobs:
        if job.status == "success" and job.ref == ref:
            return job

    return None


def get_artifacts(project, success_job):
    """ Get success job's artifacts. """

    job = project.jobs.get(success_job.id)

    ziparts = str(project.name) + ".zip"
    with open(ziparts, "wb") as f:
        job.artifacts(streamed=True, action=f.write)
    subprocess.run(["unzip", "-bo", ziparts])
    os.unlink(ziparts)


def update_wiki():
    """ Update Wiki pages with new games results. """

    games = {
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard"
    }
    games_keys = games.keys()
    games_content = "Game Leaderboard"


def start_competition(game, group_name):
    """ Start competition with collected strategies. """

    gl = gitlab.Gitlab.from_config("gitiu7", ["cfg/api_config.cfg"])
    gl.auth()

    group = get_group(gl, group_name)
    for proj in get_group_projects(gl, group):
        try:
            project = get_project(gl, group, proj.name)
            jobs = get_last_success_job(project, game)
            get_artifacts(project, jobs)
        except (gitlab.exceptions.GitlabListError, gitlab.exceptions.GitlabHttpError):
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game", help="Select a game to be played")
    parser.add_argument(
        "group_name", help="Select a GitLab group name to be searched")
    args = parser.parse_args()
    start_competition(args.game, args.group_name)
