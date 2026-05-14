# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import is_admin

def get_main_menu(username):
    if username is None:
        username = "no_username"
    keyboard = [
        [KeyboardButton("Поиск")],
        [KeyboardButton("Профиль")],
    ]
    if is_admin(username):
        keyboard.append([KeyboardButton("Админ панель")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_profile_keyboard():
    keyboard = [
        [InlineKeyboardButton("Моя статистика", callback_data="profile_stats")],
        [InlineKeyboardButton("История поисков", callback_data="profile_history")],
        [InlineKeyboardButton("Остаток запросов", callback_data="profile_balance")],
        [InlineKeyboardButton("Покупка запросов", callback_data="profile_buy")],
        [InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("История запросов", callback_data="admin_history")],
        [InlineKeyboardButton("Архив всех поисков", callback_data="admin_archive")],
        [InlineKeyboardButton("Выдать запросы", callback_data="admin_give_menu")],
        [InlineKeyboardButton("Управление очередью", callback_data="admin_queue_menu")],
        [InlineKeyboardButton("Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("Управление админами", callback_data="admin_admins_menu")],
        [InlineKeyboardButton("Топ пользователей", callback_data="admin_top")],
        [InlineKeyboardButton("Список пользователей", callback_data="admin_users_list")],
        [InlineKeyboardButton("Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_queue_keyboard():
    keyboard = [
        [InlineKeyboardButton("Статистика очереди", callback_data="admin_queue_stats")],
        [InlineKeyboardButton("Список очереди", callback_data="admin_queue_list")],
        [InlineKeyboardButton("Очистить очередь", callback_data="admin_queue_clear")],
        [InlineKeyboardButton("Назад", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)