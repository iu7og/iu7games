"""
        ===== DATABASE MODELS v.1.0 =====
        Copyright (C) 2019 - 2020 IU7Games Team.

        Модуль со структурными классами БД
"""

import mongoengine as mg
from database.config import Config


class Player(mg.Document):
    """
        Класс, представляющий игрока
    """

    gitlab_id = mg.StringField(max_length=64, primary_key=True)
    name = mg.StringField(max_length=64, required=True)
    trackers = mg.DictField()
    meta = {'db_alias': Config.main_db_alias}


class Achievement(mg.Document):
    """
        Класс, представляющий достижение игрока
    """

    name = mg.StringField(max_length=32, required=True)
    description = mg.StringField(max_length=128, required=True)
    states = mg.DictField(required=True)
    meta = {'db_alias': Config.main_db_alias}


class Game(mg.Document):
    """
        Класс, представляющий игру
    """

    name = mg.StringField(required=True)
    meta = {'db_alias': Config.main_db_alias}


class GameResult(mg.Document):
    """
        Класс, представляющий результат игрока в игре
    """

    game = mg.ReferenceField(Game)
    player = mg.ReferenceField(Player)
    position = mg.IntField(min_value=0)
    error_code = mg.IntField()
    meta = {'db_alias': Config.main_db_alias}
