"""
        ===== USERS ACHIEVEMENTS v.1.0 =====
        Copyright (C) 2019 - 2020 IU7Games Team.

        Модуль с функциями для обработки достижений игроков
"""

from collections import namedtuple
from functools import reduce
from typing import List, Dict
import re
import mongoengine as mg
import models

AchievementList = namedtuple(
    'ACHIEVEMENTS',
    [
        'STRATEGY_LOST',
        'WRONG_RES',
        'HABITUE',
        'FIRST_AMONG_EQUALS',
        'THE_NIGHT_IS_STILL_YOUNG',
        'ALMOST_THERE',
        'AUTOMERGE_KING'
    ]
)

ACHIEVEMENTS = AchievementList(
    STRATEGY_LOST='strategy_lost',
    WRONG_RES='wrong_res',
    HABITUE='habitue',
    FIRST_AMONG_EQUALS='first_among_equals',
    THE_NIGHT_IS_STILL_YOUNG='the_night_is_still_young',
    ALMOST_THERE='almost_there',
    AUTOMERGE_KING='automerge_king'
)

ErrorCodesList = namedtuple(
    'ERROR_CODES',
    [
        'DEFAULT_VALUE',
        'STRATEGY_LOST',
        'WRONG_RES'
    ]
)

ERROR_CODES = ErrorCodesList(
    DEFAULT_VALUE=0,
    STRATEGY_LOST=-1,
    WRONG_RES=-2
)

ERROR_REGEX = r'^[а-яА-Я ]+$'
WRONG_RES_REGEX = r'^\[\d\]+$'


def add_achievements_to_db() -> None:
    """
        Добавление полного списка достижений в БД
    """

    mg.connect()

    for achievement in models.Achievement.objects():
        achievement.delete()

    achievement = models.Achievement(
        name='И так сойдет...',
        description='Получить статус "Отсутствует стратегия" в лидерборде одной из игр',
        states={ACHIEVEMENTS.STRATEGY_LOST: 1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Но у меня работало...',
        description='Получить статус "[0]" в лидерборде одной из игр',
        states={ACHIEVEMENTS.WRONG_RES: 1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Завсегдатай...',
        description='Во всех играх есть рабочая стратегия',
        states={ACHIEVEMENTS.HABITUE: 5}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Почти получилось',
        description='Занять 4-ое место в одной из игр',
        states={ACHIEVEMENTS.ALMOST_THERE: 1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Ещё не вечер',
        description='Занять 2-ое или 3-е место в одной из игр',
        states={ACHIEVEMENTS.THE_NIGHT_IS_STILL_YOUNG: 1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Первый среди равных',
        description='Занять 1-ое место в одной из игр',
        states={ACHIEVEMENTS.FIRST_AMONG_EQUALS: 1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Король автомержей',
        description='Войти в тройку во всех играх',
        states={ACHIEVEMENTS.ALMOST_THERE: 5}
    )
    achievement.save()

    mg.disconnect()


def update_players_results(game_name: str, results: List[List[str]]) -> None:
    """
        Обновление результатов игр у игроков.
        Использует сырые данные прогона (до преобразования в таблицу для Wiki)
    """

    mg.connect()

    game = models.Game.objects(name=game_name).first()

    if game is None:
        game = models.Game(name=game_name)
        game.save()

    for result in results:
        player = models.Player.objects(gitlab_id=result[2]).first()

        if player is None:
            player = models.Player(gitlab_id=result[2], name=result[1])
            player.save()

        player_res = models.GameResult.objects(
            game=game, player=player).first()

        if player_res is None:
            player_res = models.GameResult(game=game, player=player)

        player_res.position = result[0]

        if re.match(ERROR_REGEX, result[4]):
            player_res.error_code = ERROR_CODES.STRATEGY_LOST
        elif re.match(WRONG_RES_REGEX, result[4]):
            player_res.error_code = ERROR_CODES.WRONG_RES
        else:
            player_res.error_code = ERROR_CODES.DEFAULT_VALUE

        player_res.save()

    mg.disconnect()


def update_players_trackers(game_name: str, users: List[List[str]]) -> None:
    """
        Обновление трекеров достижений у игроков.
        game_name - название игры
        users - list, содержащий пары [gitlab_id, name]
    """
    def update_tracker(player, tracker, value, increase=False):
        """
            Обновление конкретного трекера у игрока
        """
        if increase and tracker in player.trackers:
            player.trackers[tracker] += value
        else:
            player.trackers[tracker] = value

    def check_trackers(game, player, results):
        """
            Обновление трекеров игрока, не зависящих от других игроков
        """

        error_code = reduce(lambda x, y: x if x.game ==
                            game else y, results).error_code

        # И так сойдет
        if error_code == ERROR_CODES.STRATEGY_LOST:
            update_tracker(player, ACHIEVEMENTS.STRATEGY_LOST, 1)
        # Но у меня работало
        elif error_code == ERROR_CODES.WRONG_RES:
            update_tracker(player, ACHIEVEMENTS.WRONG_RES, 1)

        positions = {'1': 0, '1_2_3': 0, '2_3': 0, '4': 0, 'other': 0}
        for res in results:

            if res.error_code != ERROR_CODES.DEFAULT_VALUE:
                continue

            if res.position == 0:
                positions['1'] += 1

            if res.position in (0, 1, 2):
                positions['1_2_3'] += 1

            if res.position in (1, 2):
                positions['2_3'] += 1

            if res.position == 3:
                positions['4'] += 1

            positions['other'] += 1

        # Завсегдатай
        update_tracker(player, ACHIEVEMENTS.HABITUE, positions['other'])

        # Почти получилось
        update_tracker(player, ACHIEVEMENTS.ALMOST_THERE,
                       1 if positions['4'] > 0 else 0)

        # Ещё не вечер
        update_tracker(player, ACHIEVEMENTS.THE_NIGHT_IS_STILL_YOUNG,
                       1 if positions['2_3'] > 0 else 0)

        # Король автомержей
        update_tracker(player, ACHIEVEMENTS.AUTOMERGE_KING, positions['1_2_3'])

        # Первый среди равных
        update_tracker(player, ACHIEVEMENTS.FIRST_AMONG_EQUALS,
                       1 if positions['1'] > 0 else 0)

    mg.connect()

    game = models.Game.objects(name=game_name).first()

    for user in users:
        player = models.Player.objects(gitlab_id=user[0]).first()

        check_trackers(game, player, models.GameResult.objects(player=player))

        player.save()

    mg.disconnect()


def get_players_achievements(players_ids: List[str]) -> Dict[str, List[str]]:
    """
        Получение выполненных достижений по списку
        gitlab_id игроков
    """

    result = {}

    mg.connect()

    achievements = models.Achievement.objects()

    for gitlab_id in players_ids:
        player = models.Player.objects(gitlab_id=gitlab_id).first()

        result[gitlab_id] = [achievement.name for achievement in achievements
                             if player.trackers.items() >= achievement.states.items()]

    mg.disconnect()

    return result
