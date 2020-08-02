"""
        ===== USERS ACHIEVEMENTS v.1.0 =====
        Copyright (C) 2019 - 2020 IU7Games Team.

        Модуль с функциями для обработки достижений игроков
"""

from collections import namedtuple
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

ERROR_REGEX = r'[а-яА-Я]+'
TIME_REGEX = r'\[[0-9,.e-]+,[0-9,.e-]+\]'
WRONG_RES_REGEX = r'[0-9]+'

def add_achievements_to_db():
    """
        Добавление полного списка достижений в БД
    """

    mg.connect()

    for achievement in models.Achievement.objects():
        achievement.delete()

    achievement = models.Achievement(
        name='И так сойдет...',
        description='Получить статус "Отсутствует стратегия" в лидерборде одной из игр',
        states={ACHIEVEMENTS.STRATEGY_LOST:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Но у меня работало...',
        description='Получить статус "[0]" в лидерборде одной из игр',
        states={ACHIEVEMENTS.WRONG_RES:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Завсегдатай...',
        description='Во всех играх есть рабочая стратегия',
        states={ACHIEVEMENTS.HABITUE:5}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Почти получилось',
        description='Занять 4-ое место в одной из игр',
        states={ACHIEVEMENTS.ALMOST_THERE:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Ещё не вечер',
        description='Занять 2-ое или 3-е место в одной из игр',
        states={ACHIEVEMENTS.THE_NIGHT_IS_STILL_YOUNG:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Первый среди равных',
        description='Занять 1-ое место в одной из игр',
        states={ACHIEVEMENTS.FIRST_AMONG_EQUALS:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Король автомержей',
        description='Войти в тройку во всех играх',
        states={ACHIEVEMENTS.ALMOST_THERE:5}
    )
    achievement.save()

    mg.disconnect()

def get_players_achievements(players_ids):
    """
        Получение выполненных достижений по списку
        gitlab_id игроков
    """

    result = {}

    mg.connect()

    achievements = models.Achievement.objects()

    for gitlab_id in players_ids:
        player = models.Player.objects(gitlab_id=gitlab_id).first()

        result[gitlab_id] = [achievement.name for achievement in achievements \
            if player.trackers.items() >= achievement.states.items()]

    mg.disconnect()

    return result
