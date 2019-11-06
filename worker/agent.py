""" Worker for IU7Games project. """

import os
import argparse

import gitlab
import worker.wiki
import worker.repo
from games.strgame import split_runner, strtok_runner


IU7GAMES_ID = 2546


def start_competition(game, group_name):
    """ Start competition with collected strategies. """

    git_inst = gitlab.Gitlab.from_config("gitiu7", ["cfg/api_config.cfg"])
    git_inst.auth()

    group = worker.repo.get_group(git_inst, group_name)
    projects = worker.repo.get_group_projects(git_inst, group)

    iu7games = git_inst.projects.get(IU7GAMES_ID)

    results = []

    for prj in projects:
        project = worker.repo.get_project(git_inst, group, prj.name)
        job = worker.repo.get_last_success_job(project, game)

        if job is not None:
            user_result = [
                job.user.get("name"),
                "@" + job.user.get("username")
            ]
            results.append(user_result)
            worker.repo.get_artifacts(project, job)

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

    worker.wiki.update_wiki(iu7games, game, results)


def add_args():
    """ Add command line arguments to agent. """

    parser = argparse.ArgumentParser()
    parser.add_argument("game", help="Select a game")
    parser.add_argument("group_name", help="Select a GitLab group")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    ARGS = add_args()
    start_competition(ARGS.game, ARGS.group_name)
