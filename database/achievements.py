"""
        ===== USERS ACHIEVEMENTS v.1.0 =====
        Copyright (C) 2019 - 2020 IU7Games Team.

        Модуль с функциями для обработки достижений игроков
"""

from collections import namedtuple
import mongoengine as mg
import models

AchievemtsList = namedtuple(
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

Achievements = AchievemtsList(
    STRATEGY_LOST='strategy_lost',
    WRONG_RES='wrong_res',
    HABITUE='habitue',
    FIRST_AMONG_EQUALS='first_among_equals',
    THE_NIGHT_IS_STILL_YOUNG='the_night_is_still_young',
    ALMOST_THERE='almost_there',
    AUTOMERGE_KING='automerge_king'
)

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
        states={Achievements.STRATEGY_LOST:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Но у меня работало...',
        description='Получить статус "[0]" в лидерборде одной из игр',
        states={Achievements.WRONG_RES:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Завсегдатай...',
        description='Во всех играх есть рабочая стратегия',
        states={Achievements.HABITUE:5}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Почти получилось',
        description='Занять 4-ое место в одной из игр',
        states={Achievements.ALMOST_THERE:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Ещё не вечер',
        description='Занять 2-ое или 3-е место в одной из игр',
        states={Achievements.THE_NIGHT_IS_STILL_YOUNG:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Первый среди равных',
        description='Занять 1-ое место в одной из игр',
        states={Achievements.FIRST_AMONG_EQUALS:1}
    )
    achievement.save()

    achievement = models.Achievement(
        name='Король автомержей',
        description='Войти в тройку во всех играх',
        states={Achievements.ALMOST_THERE:5}
    )
    achievement.save()

    mg.disconnect()
