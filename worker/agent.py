"""
    Агент для запуска соревнований IU7Games Project.
"""

from typing import List
import os
import argparse
import pickle
from copy import deepcopy
from dataclasses import dataclass

import gitlab
import intervals
import worker.wiki
import worker.repo
from database import achievements
from games.utils import utils
from games.numbers import numbers_runner
from games.sequence import sequence_runner
from games.xogame import xo_runner
from games.strgame import split_runner, strtok_runner
from games.teen48 import teen48_runner
from games.travelgame import travel_runner
from games.tetrisgame import tetris_runner
from games.reagent import reagent_runner
from games.woodcutter import woodcutter_runner


@dataclass
class Agent:
    """
        Константы agent.
    """
    sigma_coef = 3

    git_inst = gitlab.Gitlab.from_config("gitiu7", ["cfg/api_config.cfg"])
    git_inst.auth()

    iu7games_id = 2546
    iu7games = git_inst.projects.get(iu7games_id)


def choose_name(rec, mode):
    """
        Проверка режима игры для формирования имени файла.
    """

    name = None

    if mode == "practice":
        name = rec[1].lower()
    else:
        name = rec[2][1:]

    return name


def run_num63rsgame(results, mode):
    """
        Старт NUM63RSgame.
    """

    data = deepcopy(results)

    libs = []

    for rec in data:
        lib_path = os.path.abspath(f"{choose_name(rec, mode)}_num63rs_lib.so")

        if os.path.exists(lib_path):
            libs.append(lib_path)
        else:
            libs.append("NULL")

    print("NUM63RSGAME RESULTS\n")
    results_def = numbers_runner.start_numbers_game(libs)

    for i, rec in enumerate(data):
        sign = worker.wiki.Wiki.sign[1]
        if results_def[i][0] == worker.wiki.Wiki.no_result:
            rec[3:3] = [
                sign,
                intervals.closed(
                    abs(worker.wiki.Wiki.no_result),
                    intervals.inf
                )
            ]
        else:
            sign = worker.wiki.Wiki.sign[results_def[i][0] != 0]
            rec[3:3] = [
                sign,
                intervals.closed(
                    round(results_def[i][1] - Agent.sigma_coef *
                          results_def[i][2], 7),
                    round(results_def[i][1] + Agent.sigma_coef *
                          results_def[i][2], 7)
                )
            ]

    return data


def run_7equeencegame(results, mode):
    """
        Старт 7EQUEENCEgame.
    """

    data = deepcopy(results)

    libs = []

    for rec in data:
        lib_path = os.path.abspath(
            f"{choose_name(rec, mode)}_7equeence_lib.so")

        if os.path.exists(lib_path):
            libs.append(lib_path)
        else:
            libs.append("NULL")

    print("7EQUEENCEGAME RESULTS\n")
    results_def = sequence_runner.start_sequence_game(libs)

    for i, rec in enumerate(data):
        sign = worker.wiki.Wiki.sign[1]
        if results_def[i][0] == worker.wiki.Wiki.no_result:
            rec[3:3] = [
                sign,
                intervals.closed(
                    abs(worker.wiki.Wiki.no_result),
                    intervals.inf
                )
            ]
        else:
            sign = worker.wiki.Wiki.sign[results_def[i][0] != 0]
            rec[3:3] = [
                sign,
                intervals.closed(
                    round(results_def[i][1] - Agent.sigma_coef *
                          results_def[i][2], 7),
                    round(results_def[i][1] + Agent.sigma_coef *
                          results_def[i][2], 7)
                )
            ]

    return data


def run_xogame(results, mode):
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

        lib_path = os.path.abspath(f"{choose_name(rec_3x3, mode)}_xo_lib.so")

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


def run_strgame(results, mode):
    """
        Старт STRgame.
    """

    data_split = deepcopy(results)
    data_strtok = deepcopy(results)

    print("STRGAME RESULTS\n")
    for rec_split, rec_strtok in zip(data_split, data_strtok):

        print(f"{rec_split[1]}:")

        lib_path = os.path.abspath(
            f"{choose_name(rec_split, mode)}_split_lib.so")
        test_path = os.path.abspath("games/strgame/tests/split")

        if os.path.exists(lib_path) and os.path.exists(test_path):
            split_res = split_runner.start_split(lib_path, test_path)
            sign = worker.wiki.Wiki.sign[0]
            if split_res[0] != 0:
                sign = worker.wiki.Wiki.sign[1]
            rec_split[3:3] = [
                sign,
                intervals.closed(
                    round(split_res[1] - Agent.sigma_coef * split_res[2], 7),
                    round(split_res[1] + Agent.sigma_coef * split_res[2], 7)
                )
            ]
        else:
            rec_split[3:3] = [
                worker.wiki.Wiki.sign[1],
                intervals.closed(
                    abs(worker.wiki.Wiki.no_result),
                    intervals.inf
                )
            ]

        lib_path = os.path.abspath(
            f"{choose_name(rec_strtok, mode)}_strtok_lib.so")
        test_path = os.path.abspath("games/strgame/tests/strtok")

        if os.path.exists(lib_path) and os.path.exists(test_path):
            strtok_res = strtok_runner.start_strtok(lib_path, test_path)
            sign = worker.wiki.Wiki.sign[0]
            if strtok_res[0] != 0:
                sign = worker.wiki.Wiki.sign[1]
            rec_strtok[3:3] = [
                sign,
                intervals.closed(
                    round(strtok_res[1] - Agent.sigma_coef * strtok_res[2], 7),
                    round(strtok_res[1] + Agent.sigma_coef * strtok_res[2], 7)
                )
            ]
        else:
            rec_strtok[3:3] = [
                worker.wiki.Wiki.sign[1],
                intervals.closed(
                    abs(worker.wiki.Wiki.no_result),
                    intervals.inf
                )
            ]
        print()

    return (data_split, data_strtok)


def run_teen48game(results, mode):
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

        lib_path = os.path.abspath(
            f"{choose_name(rec_4x4, mode)}_teen48_lib.so")

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


def run_tr4v31game(results, mode):
    """
        Старт TR4V31game
    """

    data = deepcopy(results)

    libs = []

    for rec in data:
        lib_path = os.path.abspath(f"{choose_name(rec, mode)}_tr4v31_lib.so")

        if os.path.exists(lib_path):
            libs.append(lib_path)
        else:
            libs.append("NULL")

    print("TR4V31GAME RESULTS\n")

    test_path = os.path.abspath("games/travelgame/tests")
    results_def = travel_runner.start_travel_game(libs, test_path)

    for i, rec in enumerate(data):
        sign = worker.wiki.Wiki.sign[1]
        if results_def[i][0] == worker.wiki.Wiki.no_result:
            rec[3:3] = [
                sign,
                intervals.closed(
                    abs(worker.wiki.Wiki.no_result),
                    intervals.inf
                )
            ]
        else:
            sign = worker.wiki.Wiki.sign[results_def[i][0] != 0]
            rec[3:3] = [
                sign,
                intervals.closed(
                    round(results_def[i][1] - Agent.sigma_coef *
                          results_def[i][2], 7),
                    round(results_def[i][1] + Agent.sigma_coef *
                          results_def[i][2], 7)
                )
            ]

    return data


def run_t3tr15game(results, mode):
    """
        Старт T3RT15game.
    """

    data = deepcopy(results)

    libs = []

    results_old = []

    if os.path.exists("tbdump_t3tr15game.obj"):
        with open("tbdump_t3tr15game.obj", "rb") as results_dump:
            results_old = pickle.load(results_dump)

    for rec in data:
        rating = 0

        for rec_old in results_old:
            if rec[1] == rec_old[1]:
                rating = rec_old[3]

        lib_path = os.path.abspath(
            f"{choose_name(rec, mode)}_t3tr15_lib.so")

        if os.path.exists(lib_path):
            libs.append((lib_path, rating))
        else:
            libs.append(("NULL", rating))

    print("T3TR15 RESULTS\n")
    results = tetris_runner.start_tetris_competition(libs)

    for i, rec in enumerate(data):
        rec.insert(3, results[i])

    return data


def run_r3463ntgame(results, mode):
    """
        Старт R3463NTgame.
    """

    data_10x10 = deepcopy(results)
    data_20x20 = deepcopy(results)

    libs_10x10 = []
    libs_20x20 = []

    results_10x10_old = []
    results_20x20_old = []

    if os.path.exists("tbdump_r3463ntgame_10x10.obj"):
        results_10x10_dump = open("tbdump_r3463ntgame_10x10.obj", "rb")
        results_10x10_old = pickle.load(results_10x10_dump)
    if os.path.exists("tbdump_r3463ntgame_20x20.obj"):
        results_20x20_dump = open("tbdump_r3463ntgame_20x20.obj", "rb")
        results_20x20_old = pickle.load(results_20x20_dump)

    for rec_10x10, rec_20x20 in zip(data_10x10, data_20x20):
        rating_10x10 = 0
        rating_20x20 = 0

        for rec_10x10_old, rec_20x20_old in zip(results_10x10_old, results_20x20_old):
            if rec_10x10[1] == rec_10x10_old[1]:
                rating_10x10 = rec_10x10_old[3]
            if rec_20x20[1] == rec_20x20_old[1]:
                rating_20x20 = rec_20x20_old[3]

        lib_path = os.path.abspath(
            f"{choose_name(rec_10x10, mode)}_r3463nt_lib.so")

        if os.path.exists(lib_path):
            libs_10x10.append((lib_path, rating_10x10))
            libs_20x20.append((lib_path, rating_20x20))
        else:
            libs_10x10.append(("NULL", rating_10x10))
            libs_20x20.append(("NULL", rating_20x20))

    print("R3463NTGAME RESULTS\n")
    print("\n10X10 DIV\n")
    results_10x10 = reagent_runner.start_reagent_competition(libs_10x10, 10)
    print("\n20X20 DIV\n")
    results_20x20 = reagent_runner.start_reagent_competition(libs_20x20, 20)

    i = 0
    for rec_10x10, rec_20x20 in zip(data_10x10, data_20x20):
        rec_10x10.insert(3, results_10x10[i])
        rec_20x20.insert(3, results_20x20[i])
        i += 1

    return (data_10x10, data_20x20)


def run_w00dcutt3rgame(results, mode):
    """
        Старт W00DCUTT3Rgame.
    """

    data = deepcopy(results)

    libs = []

    results_old = []

    if os.path.exists("tbdump_w00dcutt3rgame.obj"):
        with open("tbdump_w00dcutt3rgame.obj", "rb") as results_dump:
            results_old = pickle.load(results_dump)

    for rec in data:
        rating = 1000

        for rec_old in results_old:
            if rec[1] == rec_old[1]:
                rating = rec_old[3]

        lib_path = os.path.abspath(f"{choose_name(rec, mode)}_w00dcutt3r_lib.so")

        if os.path.exists(lib_path):
            libs.append((lib_path, rating))
        else:
            libs.append(("NULL", rating))

    print("W00DCUTT3R RESULTS\n")
    results = woodcutter_runner.start_woodcutter_competition(libs)

    for i, rec in enumerate(data):
        rec.insert(3, results[i])

    return data


def update_results(game_name: str, results: List[achievements.PlayerResult]) -> None:
    """
        Обновление достижение у игрока
    """
    try:
        achievements.update_players_results(game_name, results)
    except Exception as err:
        print("Во время обработки достижений что-то пошло не так")
        print(err)

def start_competition(instance, game, group_name, stage, is_practice):
    """
        Старт соревнования с собранными стратегиями.
    """

    results = worker.repo.get_group_artifacts(instance, game, group_name)
    fresults = []
    sresults = []

    if is_practice == "practice":
        game += "_practice"

    if stage == "release":
        print(f"SEARCHING FOR {game.upper()}"
              " DEPLOY JOB TO COMPARE NEW RESULTS WITH PREVIOUS ONES")
        deploy_job = worker.repo.get_deploy_job(
            Agent.iu7games, game.lower(), "master")
        if deploy_job is not None:
            print(f"{game.upper()} DEPLOY JOB FOUND."
                  " NEW RESULTS WILL BE AFFECTED BY PREVIOUS ONES\n")
            worker.repo.get_artifacts(Agent.iu7games, deploy_job)
        else:
            print(f"{game.upper()} DEPLOY JOB NOT FOUND. FRESH START\n")
    elif stage == "build":
        print(f"START BUILD FOR {game.upper()}\n")

    if game.startswith("NUM63RSgame"):
        fresults = run_num63rsgame(results, is_practice)
    elif game.startswith("7EQUEENCEgame"):
        fresults = run_7equeencegame(results, is_practice)
    elif game.startswith("XOgame"):
        fresults, sresults = run_xogame(results, is_practice)
    elif game.startswith("STRgame"):
        fresults, sresults = run_strgame(results, is_practice)
    elif game.startswith("TEEN48game"):
        fresults, sresults = run_teen48game(results, is_practice)
    elif game.startswith("TR4V31game"):
        fresults = run_tr4v31game(results, is_practice)
    elif game.startswith("T3TR15game"):
        fresults = run_t3tr15game(results, is_practice)
        update_results(
            "T3TR15game",
            [
                achievements.PlayerResult(
                    i[0],
                    i[2],
                    i[1],
                    utils.GameResult.no_result == i[3],
                    i[3] == 0
                )
                for i in fresults
            ]
        )
    elif game.startswith("R3463NTgame"):
        fresults, sresults = run_r3463ntgame(results, is_practice)
        update_results(
            "R3463NTgame10x10",
            [
                achievements.PlayerResult(
                    i[0],
                    i[2],
                    i[1],
                    False,
                    False
                )
                for i in fresults
            ]
        )
        update_results(
            "R3463NTgame20x20",
            [
                achievements.PlayerResult(
                    i[0],
                    i[2],
                    i[1],
                    False,
                    False
                )
                for i in sresults
            ]
        )
    elif game.startswith("W00DCUTT3Rgame"):
        fresults = run_w00dcutt3rgame(results, is_practice)
        update_results(
            "W00DCUTT3Rgame",
            [
                achievements.PlayerResult(
                    i[0],
                    i[2],
                    i[1],
                    utils.GameResult.no_result == i[3],
                    i[3] == 0
                )
                for i in fresults
            ]
        )

    if stage == "release":
        worker.wiki.update_wiki(Agent.iu7games, game, fresults, sresults)
        print(f"\nWIKI PAGE FOR {game.upper()} UPDATED SUCCESSFULLY")
    elif stage == "build":
        print("\nBUILD PASSED")


def add_args():
    """
        Добавление аргументов командной строки для агента.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("game", help="Select a game")
    parser.add_argument("group_name", help="Select a GitLab group")
    parser.add_argument("stage", help="Select a stage for run")
    parser.add_argument("is_practice", help="Is it is practice group")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    ARGS = add_args()

    start_competition(Agent.git_inst, ARGS.game, ARGS.group_name,
                      ARGS.stage, ARGS.is_practice)
