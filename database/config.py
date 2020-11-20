"""
        ===== DATABASE MODELS v.1.0 =====
        Copyright (C) 2019 - 2020 IU7Games Team.

        Модуль с общими переменными для БД
"""
from os import environ
from dataclasses import dataclass


@dataclass
class Config:
    """
        Класс с названиями достижений игрока
    """
    db_name = environ['DB_NAME']
    db_user = environ['DB_USER']
    db_pass = environ['DB_PASS']
    db_ip = environ['DB_IP']
    main_db_alias = 'main_db'
