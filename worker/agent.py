"""
    Агент для запуска соревнований IU7Games Project.
"""

import os
import argparse
import pickle
from copy import deepcopy

import gitlab
import intervals
import worker.wiki
import worker.repo
from games.numbers import numbers_runner
from games.xogame import xo_runner
from games.strgame import split_runner, strtok_runner
from games.teen48 import teen48_runner


SIGMA_COEF = 3

GIT_INST = gitlab.Gitlab.from_config("gitiu7", ["cfg/api_config.cfg"])
GIT_INST.auth()

IU7GAMES_ID = 2546
IU7GAMES = GIT_INST.projects.get(IU7GAMES_ID)


def run_num63rsgame(results):
    """
        Старт NUM63RSgame.
    """

    data = deepcopy(results)

    print("NUM63RSGAME RESULTS\n")
    for rec in data:
        lib_path = os.path.abspath(f"{rec[2][1:]}_num63rsgame_lib.so")

        if os.path.exists(lib_path):
            res = numbers_runner.start_numbers_game(lib_path)
            sign = worker.wiki.SIGN[0]
            if res[0] != 0:
                sign = worker.wiki.SIGN[1]
            rec[3:3] = [
                sign,
                intervals.closed(
                    round(res[1] - SIGMA_COEF * res[2], 7),
                    round(res[1] + SIGMA_COEF * res[2], 7)
                )
            ]
        else:
            rec[3:3] = [
                worker.wiki.SIGN[1],
                intervals.closed(
                    abs(worker.wiki.NO_RESULT),
                    intervals.inf
                )
            ]

    return data


def run_xogame(results):
    """
        Старт XOgame.
    """

    data_3x3 = deepcopy(results)
    data_5x5 = deepcopy(results)

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

    for rec_3x3, rec_5x5 in zip(data_3x3, data_5x5):
        rating_3x3 = 1000
        rating_5x5 = 1000

        for rec_3x3_old, rec_5x5_old in zip(results_3x3_old, results_5x5_old):
            if rec_3x3[1] == rec_3x3_old[1]:
                rating_3x3 = rec_3x3_old[3]
            if rec_5x5[1] == rec_5x5_old[1]:
                rating_5x5 = rec_5x5_old[3]

        lib_path = os.path.abspath(f"{rec_3x3[2][1:]}_xo_lib.so")

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
    for rec_3x3, rec_5x5 in zip(data_3x3, data_5x5):
        rec_3x3.insert(3, results_3x3[i])
        rec_5x5.insert(3, results_5x5[i])
        i += 1

    return (data_3x3, data_5x5)


def run_strgame(results):
    """
        Старт STRgame.
    """

    data_split = deepcopy(results)
    data_strtok = deepcopy(results)

    print("STRGAME RESULTS\n")
    for rec_split, rec_strtok in zip(data_split, data_strtok):

        print(f"{rec_split[1]}:")

        lib_path = os.path.abspath(f"{rec_split[2][1:]}_split_lib.so")
        test_path = os.path.abspath("games/strgame/tests/split")

        if os.path.exists(lib_path) and os.path.exists(test_path):
            split_res = split_runner.start_split(lib_path, test_path)
            sign = worker.wiki.SIGN[0]
            if split_res[0] != 0:
                sign = worker.wiki.SIGN[1]
            rec_split[3:3] = [
                sign,
                intervals.closed(
                    round(split_res[1] - SIGMA_COEF * split_res[2], 7),
                    round(split_res[1] + SIGMA_COEF * split_res[2], 7)
                )
            ]
        else:
            rec_split[3:3] = [
                worker.wiki.SIGN[1],
                intervals.closed(
                    abs(worker.wiki.NO_RESULT),
                    intervals.inf
                )
            ]

        lib_path = os.path.abspath(f"{rec_strtok[2][1:]}_strtok_lib.so")
        test_path = os.path.abspath("games/strgame/tests/strtok")

        if os.path.exists(lib_path) and os.path.exists(test_path):
            strtok_res = strtok_runner.start_strtok(lib_path, test_path)
            sign = worker.wiki.SIGN[0]
            if strtok_res[0] != 0:
                sign = worker.wiki.SIGN[1]
            rec_strtok[3:3] = [
                sign,
                intervals.closed(
                    round(strtok_res[1] - SIGMA_COEF * strtok_res[2], 7),
                    round(strtok_res[1] + SIGMA_COEF * strtok_res[2], 7)
                )
            ]
        else:
            rec_strtok[3:3] = [
                worker.wiki.SIGN[1],
                intervals.closed(
                    abs(worker.wiki.NO_RESULT),
                    intervals.inf
                )
            ]
        print()

    return (data_split, data_strtok)


def run_teen48game(results):
    """
        Старт TEEN48game.
    """

    data_4x4 = deepcopy(results)
    data_6x6 = deepcopy(results)

    libs_4x4 = []
    libs_6x6 = []

    results_4x4_old = []
    results_6x6_old = []

    if os.path.exists("tbdump_teen48game_4x4.obj"):
        results_4x4_dump = open("tbdump_teen48game_4x4.obj", "rb")
        results_4x4_old = pickle.load(results_4x4_dump)
    if os.path.exists("tbdump_teen48game_6x6.obj"):
        results_6x6_dump = open("tbdump_teen48game_6x6.obj", "rb")
        results_6x6_old = pickle.load(results_6x6_dump)

    for rec_4x4, rec_6x6 in zip(data_4x4, data_6x6):
        rating_4x4 = 0
        rating_6x6 = 0

        for rec_4x4_old, rec_6x6_old in zip(results_4x4_old, results_6x6_old):
            if rec_4x4[1] == rec_4x4_old[1]:
                rating_4x4 = rec_4x4_old[3]
            if rec_6x6[1] == rec_6x6_old[1]:
                rating_6x6 = rec_6x6_old[3]

        lib_path = os.path.abspath(f"{rec_4x4[2][1:]}_teen48_lib.so")

        if os.path.exists(lib_path):
            libs_4x4.append((lib_path, rating_4x4))
            libs_6x6.append((lib_path, rating_6x6))
        else:
            libs_4x4.append(("NULL", rating_4x4))
            libs_6x6.append(("NULL", rating_6x6))

    print("TEEN48GAME RESULTS\n")
    print("\n4X4 DIV\n")
    results_4x4 = teen48_runner.start_teen48game_competition(libs_4x4, 4)
    print("\n6X6 DIV\n")
    results_6x6 = teen48_runner.start_teen48game_competition(libs_6x6, 6)

    i = 0
    for rec_4x4, rec_6x6 in zip(data_4x4, data_6x6):
        rec_4x4.insert(3, results_4x4[i])
        rec_6x6.insert(3, results_6x6[i])
        i += 1

    return (data_4x4, data_6x6)


def start_competition(instance, game, group_name, stage):
    """
        Старт соревнования с собранными стратегиями.
    """

    results = worker.repo.get_group_artifacts(instance, game, group_name)
    fresults = []
    sresults = []

    # deploy_job = worker.repo.get_deploy_job(IU7GAMES, game.lower(), "develop")
    # if deploy_job is not None:
    #     worker.repo.get_artifacts(IU7GAMES, deploy_job)

    if game == "NUM63RSgame":
        fresults = run_num63rsgame(results)
    elif game == "XOgame":
        fresults, sresults = run_xogame(results)
    elif game == "STRgame":
        fresults, sresults = run_strgame(results)
    elif game == "TEEN48game":
        fresults, sresults = run_teen48game(results)

    if stage == "release":
        worker.wiki.update_wiki(IU7GAMES, game, fresults, sresults)
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
