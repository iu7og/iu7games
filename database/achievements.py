"""
        ===== USERS ACHIEVEMENTS v.1.0 =====
        Copyright (C) 2019 - 2020 IU7Games Team.

        Модуль с функциями для обработки достижений игроков
"""

from dataclasses import dataclass
from typing import List
import mongoengine as mg
import database.models as models
from database.config import Config


@dataclass
class Achievement:
    """
        Класс с названиями достижений игрока
    """
    strategy_lost = "strategy_lost"
    wrong_res = "wrong_res"
    habitue = "habitue"
    first_among_equals = "first_among_equals"
    the_night_is_still_young = "the_night_is_still_young"
    almost_there = "almost_there"
    automerge_king = "automerge_king"


@dataclass
class Error:
    """
        Класс с видами ошибочных результатов игрока
    """
    default_value = 0
    strategy_lost = -1
    wrong_res = -2


@dataclass
class PlayerInfo:
    """
        Представление информации об игроке
    """
    name: str
    gitlab_id: str

    def __init__(self, name: str, gitlab_id: str):
        self.name = name
        self.gitlab_id = gitlab_id


@dataclass
class PlayerResult:
    """
        Представление результата игрока
    """
    place: int
    gitlab_id: str
    name: str
    corrupted_strategy: bool
    wrong_result: bool

    def __init__(self, place: int, gitlab_id: str, name: str,
                 corrupted_strategy: bool, wrong_result: bool):
        self.place = place
        self.gitlab_id = gitlab_id
        self.name = name
        self.corrupted_strategy = corrupted_strategy
        self.wrong_result = wrong_result


@dataclass
class PlayerAchievemts:
    """
        Представление списка достижений игрока
    """
    gitlab_id: str
    achievements: List[str]

    def __init__(self, gitlab_id: str, achievements: List[str]):
        self.gitlab_id = gitlab_id
        self.achievements = achievements


def add_achievements_to_db() -> None:
    """
        Добавление полного списка достижений в БД
    """

    mg.connect(
        db=Config.db_name,
        username=Config.db_user,
        password=Config.db_pass,
        host=Config.db_ip,
        alias=Config.main_db_alias
    )

    models.Achievement.objects().delete()

    models.Achievement.objects.insert(
        [
            models.Achievement(
                name="И так сойдет...",
                description="Получить статус 'Отсутствует стратегия' в лидерборде одной из игр",
                states={Achievement.strategy_lost: 1}
            ),
            models.Achievement(
                name="Но у меня работало...",
                description="Получить статус '[0]' в лидерборде одной из игр",
                states={Achievement.wrong_res: 1}
            ),
            models.Achievement(
                name="Завсегдатай...",
                description="Во всех играх есть рабочая стратегия",
                states={Achievement.habitue: 5}
            ),
            models.Achievement(
                name="Почти получилось",
                description="Занять 4-ое место в одной из игр",
                states={Achievement.almost_there: 1}
            ),
            models.Achievement(
                name="Ещё не вечер",
                description="Занять 2-ое или 3-е место в одной из игр",
                states={Achievement.the_night_is_still_young: 1}
            ),
            models.Achievement(
                name="Первый среди равных",
                description="Занять 1-ое место в одной из игр",
                states={Achievement.first_among_equals: 1}
            ),
            models.Achievement(
                name="Король автомержей",
                description="Войти в тройку во всех играх",
                states={Achievement.automerge_king: 5}
            )
        ]
    )

    mg.disconnect(alias=Config.main_db_alias)


def update_tracker(player: models.Player, tracker: str, value: int, increase=False):
    """
        Обновление конкретного трекера у игрока
    """
    if increase and tracker in player.trackers:
        player.trackers[tracker] += value
    else:
        player.trackers[tracker] = value


def check_trackers(player: models.Player, result: models.GameResult):
    """
        Обновление трекеров игрока, не зависящих от других игроков
    """

    if result.error_code == Error.strategy_lost:
        update_tracker(player, Achievement.strategy_lost, 1)
    elif result.error_code == Error.wrong_res:
        update_tracker(player, Achievement.wrong_res, 1)

    positions = {"1": 0, "1_2_3": 0, "2_3": 0, "4": 0, "other": 0}
    for res in result:
        if res.error_code != Error.default_value:
            continue

        if res.position == 0:
            positions["1"] += 1

        if res.position in (0, 1, 2):
            positions["1_2_3"] += 1

        if res.position in (1, 2):
            positions["2_3"] += 1

        if res.position == 3:
            positions["4"] += 1

        positions["other"] += 1

    update_tracker(player, Achievement.habitue, positions["other"])
    update_tracker(player, Achievement.almost_there,
                   1 if positions["4"] > 0 else 0)
    update_tracker(player, Achievement.the_night_is_still_young,
                   1 if positions["2_3"] > 0 else 0)
    update_tracker(player, Achievement.automerge_king, positions["1_2_3"])
    update_tracker(player, Achievement.first_among_equals,
                   1 if positions["1"] > 0 else 0)

    return player


def update_players_trackers(game_name: str, users: List[PlayerInfo]) -> None:
    """
        Обновление трекеров достижений у игроков
    """

    mg.connect(
        db=Config.db_name,
        username=Config.db_user,
        password=Config.db_pass,
        host=Config.db_ip,
        alias=Config.main_db_alias
    )

    game = models.Game.objects(name=game_name).first()

    players = models.Player.objects(gitlab_id__in=[u.gitlab_id for u in users])

    results = models.GameResult.objects(game=game, player__in=players)

    for player in players:
        check_trackers(
            player,
            next(
                (i for i in range(results) if i.player == player),
                None
            )
        ).save()

    mg.disconnect(alias=Config.main_db_alias)


def update_players_results(game_name: str, results: List[PlayerResult]) -> None:
    """
        Обновление результатов игр у игроков
    """

    mg.connect(
        db=Config.db_name,
        username=Config.db_user,
        password=Config.db_pass,
        host=Config.db_ip,
        alias=Config.main_db_alias
    )

    game = models.Game.objects(name=game_name).first()

    if game is None:
        game = models.Game(name=game_name)
        game.save()

    players = models.Player.objects(
        gitlab_id__in=[i.gitlab_id for i in results]
    )

    new_players = [
        models.Player(
            gitlab_id=res.gitlab_id,
            name=res.name
        )
        for res in [i for i in results if i.gitlab_id not in [
            j.gitlab_id for j in players]
        ]
    ]
    models.Player.objects.insert(new_players)

    players += new_players

    found_res = models.GameResult.objects(game=game, player__in=players)
    new_res = [
        models.GameResult(game=game, player=i)
        for i in [j for j in players if j not in [
            k.player for k in found_res]
        ]
    ]
    models.GameResult.objects.insert(new_res)

    found_res += new_res

    for result in results:
        player = next(
            (
                x for x in players if x.gitlab_id == result.gitlab_id
            )
        )
        player_res = next(
            (
                x for x in found_res if x.game ==
                game and x.player == player
            )
        )

        player_res.position = result.place

        if result.corrupted_strategy:
            player_res.error_code = Error.strategy_lost
        elif result.wrong_result:
            player_res.error_code = Error.wrong_res
        else:
            player_res.error_code = Error.default_value

        player_res.save()

    mg.disconnect(alias=Config.main_db_alias)

    update_players_trackers(
        game_name, [PlayerInfo(i.name, i.gitlab_id) for i in results])


def get_players_achievements(players_ids: List[str]) -> List[PlayerAchievemts]:
    """
        Получение выполненных достижений по списку
        gitlab_id игроков
    """

    result = []

    mg.connect(
        db=Config.db_name,
        username=Config.db_user,
        password=Config.db_pass,
        host=Config.db_ip,
        alias=Config.main_db_alias
    )

    achievements = models.Achievement.objects()

    players = models.Player.objects(gitlab_id__in=players_ids)

    mg.disconnect(alias=Config.main_db_alias)

    for player in players:
        result.append(
            PlayerAchievemts(
                player.gitlab_id,
                [
                    achievement.name for achievement in achievements
                    if player.trackers.items() >= achievement.states.items()
                ]
            )
        )

    return result
