""" Worker for IU7Games project. """


import os
import subprocess
import argparse
from datetime import datetime

import gitlab
from games.strgame import split_runner, strtok_runner


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


def get_group(instance, name):
    """ Get group by it's name. """

    group = None

    groups = instance.groups.list(all=True)
    for grp in groups:
        if grp.name == name:
            group = grp
            break

    return group


def get_group_projects(instance, group):
    """ Get group's projects. """

    group = instance.groups.get(group.id)
    projects = group.projects.list(all=True)

    return projects


def get_project(instance, group, name):
    """ Get project by it' name. """

    project = None

    projects = get_group_projects(instance, group)
    for prj in projects:
        if prj.name == name:
            project = instance.projects.get(prj.id)
            break

    return project


def get_last_success_job(project, ref):
    """ Get project's last success job by ref name. """

    success_job = None

    jobs = project.jobs.list(all=True, ref=ref)
    for job in jobs:
        if job.status == "success" and job.ref == ref:
            success_job = job
            break

    return success_job


def get_artifacts(project, success_job):
    """ Get success job's artifacts. """

    job = project.jobs.get(success_job.id)

    zip_arts = job.user.get("username") + ".zip"

    try:
        with open(zip_arts, "wb") as file:
            job.artifacts(streamed=True, action=file.write)
        subprocess.run(["unzip", "-boq", zip_arts])
    except gitlab.exceptions.GitlabGetError:
        pass
    os.unlink(zip_arts)


def update_wiki(project, game, results):
    """ Update Wiki pages with new games results. """

    games = {
        "XOgame Leaderboard": "XOgame-Leaderboard",
        "STRgame Leaderboard": "STRgame-Leaderboard",
        "TEEN48game Leaderboard": "TEEN48game-Leaderboard"
    }
    games_keys = games.keys()

    res = None

    if game == "STRgame":
        res = "|**ФИ Студента**|**GitLab ID**|**SPLIT Тесты**|**SPLIT Время**|" \
            "**STRTOK Тесты**|**STRTOK Время**|\n" \
            "|---|---|---|---|---|---|\n"

        for student in results:
            res += "|{0}|{1}|{2}|{3}|{4}|{5}|\n".format(
                student[0], student[1], student[2],
                student[3], student[4], student[5])

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    res += "\n**Обновлено:** {0} **МСК**".format(date)

    for key in games_keys:
        if game in key:
            update_page(project, games.get(key), key, res)


def start_competition(game, group_name):
    """ Start competition with collected strategies. """

    gl = gitlab.Gitlab.from_config("gitiu7", ["cfg/api_config.cfg"])
    gl.auth()

    group = get_group(gl, group_name)
    projects = get_group_projects(gl, group)

    iu7games_id = 2546
    iu7games = gl.projects.get(iu7games_id)

    results = []

    for prj in projects:
        project = get_project(gl, group, prj.name)
        job = get_last_success_job(project, game)
        user_result = [job.user.get("name"), "@" + job.user.get("username")]
        results.append(user_result)
        get_artifacts(project, job)

    if game == "STRgame":
        print("STRGAME RESULTS\n")
        for data in results:
            print(data[0] + ":")

            try:
                lib_path = os.path.abspath(data[1][1:] + "_split_lib.so")
                test_path = os.path.abspath("/IU7Games/STRgame/tests/split")
                split_res = split_runner.start_split(lib_path, test_path)
            except OSError:
                split_res = (0, "Отсутствует стратегия")

            data.append(str(split_res[0]) + "/20")
            data.append(split_res[1])

            try:
                lib_path = os.path.abspath(data[1][1:] + "_strtok_lib.so")
                test_path = os.path.abspath("/IU7Games/STRgame/tests/strtok")
                strtok_res = strtok_runner.start_strtok(lib_path, test_path)
            except OSError:
                strtok_res = (0, "Отсутствует стратегия")

            data.append(str(strtok_res[0]) + "/20")
            data.append(strtok_res[1])

            print()
    elif game == "XOgame":
        pass
    elif game == "TEEN48game":
        pass
    else:
        pass

    update_wiki(iu7games, game, results)


def add_args():
    """ Add command line arguments to agent. """

    parser = argparse.ArgumentParser()
    parser.add_argument("game", help="Select a game to be played")
    parser.add_argument(
        "group_name", help="Select a GitLab group name to be searched")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    ARGS = add_args()
    start_competition(ARGS.game, ARGS.group_name)
