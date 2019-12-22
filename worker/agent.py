"""
    Агент для запуска соревнований IU7Games Project.
"""

import os
import argparse
import pickle

import gitlab
import worker.wiki
import worker.repo
from games.strgame import split_runner, strtok_runner
from games.xogame import xo_runner


GIT_INST = gitlab.Gitlab.from_config("gitiu7", ["cfg/api_config.cfg"])
GIT_INST.auth()

IU7GAMES_ID = 2546
IU7GAMES = GIT_INST.projects.get(IU7GAMES_ID)


def run_strgame(results):
    """
        Старт STRgame.
    """

    print("STRGAME RESULTS\n")
    for rec in results:
        print(f"{rec[0]}:")

        lib_path = os.path.abspath(f"{rec[1][1:]}_split_lib.so")
        test_path = os.path.abspath("games/strgame/tests/split")

        if os.path.exists(lib_path) and os.path.exists(test_path):
            split_res = split_runner.start_split(lib_path, test_path)
            sign = worker.wiki.STRG_RESULT[0]
            if split_res[0] != 0:
                sign = worker.wiki.STRG_RESULT[1]
            rec.extend(
                [
                    sign,
                    f"{split_res[1]:.7f}±{split_res[2]:.7f}"
                ]
            )
        else:
            rec.extend(
                [
                    worker.wiki.STRG_RESULT[1],
                    str(worker.wiki.NO_RESULT)[1:]
                ]
            )

        lib_path = os.path.abspath(f"{rec[1][1:]}_strtok_lib.so")
        test_path = os.path.abspath("games/strgame/tests/strtok")

        if os.path.exists(lib_path) and os.path.exists(test_path):
            strtok_res = strtok_runner.start_strtok(lib_path, test_path)
            sign = worker.wiki.STRG_RESULT[0]
            if strtok_res[0] != 0:
                sign = worker.wiki.STRG_RESULT[1]
            rec.extend(
                [
                    sign,
                    f"{strtok_res[1]:.7f}±{strtok_res[2]:.7f}"
                ]
            )
        else:
            rec.extend(
                [
                    worker.wiki.STRG_RESULT[1],
                    str(worker.wiki.NO_RESULT)[1:]
                ]
            )

        print()


def run_xogame(results):
    """
        Старт XOgame.
    """

    libs_3x3 = []
    libs_5x5 = []

    results_3x3_old = []
    results_5x5_old = []

    if os.path.exists("tbdump_xogame_3x3.obj"):
        results_3x3_dump = open("tbdump_xogame_3x3.obj", "rb")
        results_3x3_old = pickle.load(results_3x3_dump)
    if os.path.exists("tbdump_xogame_5x5.obj"):
        results_5x5_dump = open("tbdump_xogame_5x5.obj", "rb")
        results_5x5_old = pickle.load(results_5x5_dump)

    for rec in results:
        rating_3x3 = 1000
        rating_5x5 = 1000

        for rec_old in results_3x3_old:
            if rec[0] == rec_old[0]:
                rating_3x3 = rec_old[2]

        for rec_old in results_5x5_old:
            if rec[0] == rec_old[0]:
                rating_5x5 = rec_old[2]

        lib_path = os.path.abspath(f"{rec[1][1:]}_xo_lib.so")

        if os.path.exists(lib_path):
            libs_3x3.append((lib_path, rating_3x3))
            libs_5x5.append((lib_path, rating_5x5))
        else:
            libs_3x3.append(("NULL", rating_3x3))
            libs_5x5.append(("NULL", rating_5x5))

    print("XOGAME RESULTS\n")
    print("\n3X3 DIV\n")
    results_3x3 = xo_runner.start_xogame_competition(libs_3x3, 3)
    print("\n5X5 DIV\n")
    results_5x5 = xo_runner.start_xogame_competition(libs_5x5, 5)

    i = 0
    for rec in results:
        rec.extend([results_3x3[i], results_5x5[i]])
        i += 1


def start_competition(instance, game, group_name, stage):
    """
        Старт соревнования с собранными стратегиями.
    """

    results = worker.repo.get_group_artifacts(instance, game, group_name)

    deploy_job = worker.repo.get_deploy_job(IU7GAMES, game.lower(), "develop")
    if deploy_job is not None:
        worker.repo.get_artifacts(IU7GAMES, deploy_job)

    if game == "STRgame":
        run_strgame(results)
    elif game == "XOgame":
        run_xogame(results)
    elif game == "TEEN48game":
        pass
    else:
        pass

    if stage == "release":
        worker.wiki.update_wiki(IU7GAMES, game, results)
    elif stage == "build":
        print("BUILD PASSED")


def add_args():
    """
        Добавление аргументов командной строки для агента.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("game", help="Select a game")
    parser.add_argument("group_name", help="Select a GitLab group")
    parser.add_argument("stage", help="Select a stage for run")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    ARGS = add_args()

    start_competition(GIT_INST, ARGS.game, ARGS.group_name, ARGS.stage)
