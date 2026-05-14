# -*- coding: utf-8 -*-

from database.users_db import users_db
from database.balance_db import user_balance

def ensure_user(user_id, username=None, first_name=None, last_name=None):
    """Добавляет пользователя в базу если его нет"""
    users_db.add_user(user_id, username, first_name, last_name)
    user_balance.ensure_user(user_id, username, first_name, last_name)