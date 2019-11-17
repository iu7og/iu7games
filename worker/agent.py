""" Worker for IU7Games project. """

import os
import argparse

import gitlab
import worker.wiki
import worker.repo
from games.strgame import split_runner, strtok_runner


GIT_INST = gitlab.Gitlab.from_config("gitiu7", ["cfg/api_config.cfg"])
GIT_INST.auth()

IU7GAMES_ID = 2546
IU7GAMES = GIT_INST.projects.get(IU7GAMES_ID)


def start_competition(game, group_name):
    """ Start competition with collected strategies. """

    group = worker.repo.get_group(GIT_INST, group_name)
    projects = worker.repo.get_group_projects(GIT_INST, group)

    results = []

    print("START ARTIFACTS COLLECTION")

    for prj in projects:
        project = worker.repo.get_project(GIT_INST, group, prj.name)
        job = worker.repo.get_last_job(project, game)

        if job is None:
            print("THERE IS NO {0} BRANCH JOBS FOR {1}".format(
                game, project.name))
            continue

        developer = None
        members = project.members.list(all=True)

        for mmbr in members:
            member = project.members.get(mmbr.id)
            if member.access_level == gitlab.DEVELOPER_ACCESS:
                developer = member
                break

        if developer is not None:
            user_result = [developer.name, "@" + developer.username]
            results.append(user_result)
            if worker.repo.check_md5(
                    os.path.abspath("cfg/.gitlab-ci.students.yml"),
                    project, game, ".gitlab-ci.yml"
            ) is False:
                print("CORRUPTED CI FOUND FOR " + user_result[1])
                continue
            print("CORRECT CI FOUND FOR " + user_result[1])
            status = worker.repo.get_artifacts(project, job)

            if status == worker.repo.COLLECTED:
                print("ARTIFACTS FOR " + user_result[1] + " ARE COLLECTED")
            elif status == worker.repo.BAD_REQUEST:
                print("THERE IS FAILED JOB FOR " + user_result[1])
            elif status == worker.repo.BAD_CALL:
                print("THERE ARE NO ARTIFACTS FOR " + user_result[1])
        else:
            print("THERE IS NO DEVELOPER FOR " + project.name)

    print("FINISH ARTIFACTS COLLECTION\n")

    if game == "STRgame":
        print("STRGAME RESULTS\n")
        for data in results:
            print(data[0] + ":")

            try:
                lib_path = os.path.abspath(data[1][1:] + "_split_lib.so")
                test_path = os.path.abspath("games/strgame/tests/split")
                split_res = split_runner.start_split(lib_path, test_path)
            except OSError:
                split_res = (0, worker.wiki.NO_RESULT)

            data.append(split_res[0])
            data.append(split_res[1])

            try:
                lib_path = os.path.abspath(data[1][1:] + "_strtok_lib.so")
                test_path = os.path.abspath("games/strgame/tests/strtok")
                strtok_res = strtok_runner.start_strtok(lib_path, test_path)
            except OSError:
                strtok_res = (0, worker.wiki.NO_RESULT)

            data.append(strtok_res[0])
            data.append(strtok_res[1])

            print()
    elif game == "XOgame":
        pass
    elif game == "TEEN48game":
        pass
    else:
        pass

    worker.wiki.update_wiki(IU7GAMES, game, results)


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
