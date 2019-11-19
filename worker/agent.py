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


def start_competition(instance, game, group_name):
    """ Start competition with collected strategies. """

    if game == "STRgame":
        results = worker.repo.get_group_artifacts(instance, game, group_name)

        print("STRGAME RESULTS\n")
        for data in results:
            print(f"{data[0]}:")

            try:
                lib_path = os.path.abspath(f"{data[1][1:]}_split_lib.so")
                test_path = os.path.abspath("games/strgame/tests/split")
                split_res = split_runner.start_split(lib_path, test_path)
            except OSError:
                split_res = (0, worker.wiki.NO_RESULT)

            data.append(split_res[0])
            data.append(split_res[1])

            try:
                lib_path = os.path.abspath(f"{data[1][1:]}_strtok_lib.so")
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

    start_competition(GIT_INST, ARGS.game, ARGS.group_name)
