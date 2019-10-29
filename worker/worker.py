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


def get_success_jobs(project, ref):
    """ Get project's successful jobs by ref name. """

    success_jobs = []

    jobs = project.jobs.list(all=True)
    for job in jobs:
        if job.status == "success" and job.ref == ref:
            success_jobs.append(job)

    return success_jobs


def get_artifacts(project, success_jobs):
    """ Get success job's artifacts. """

    for success_job in success_jobs:
        job = project.jobs.get(success_job.id)

        ziparts = str(job.id) + "artifacts.zip"
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

    gl = gitlab.Gitlab.from_config("gitiu7", ["./api_config.cfg"])
    gl.auth()

    group = get_group(gl, "iu7-cprog-labs-2019")
    project = get_project(gl, group, "iu7-cprog-labs-2019-kononenkosergey")
    jobs = get_success_jobs(project, "lab_10")
    get_artifacts(project, jobs)


if __name__ == "__main__":
    worker()
