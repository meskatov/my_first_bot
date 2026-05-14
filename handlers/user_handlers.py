# -*- coding: utf-8 -*-

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from database.balance_db import user_balance
from database.users_db import users_db
from utils.helpers import is_admin
from utils.queue_system import request_queue
from keyboards.menus import get_main_menu, get_profile_keyboard

def safe_username(username):
    """Безопасное получение username"""
    if username is None:
        return "no_username"
    return username

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = safe_username(update.effective_user.username)
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name

    users_db.add_user(user_id, username, first_name, last_name)
    user_balance.ensure_user(user_id, username, first_name, last_name)
    balance = user_balance.get_balance(user_id)

    text = f"Бот meskatov search\n\n"
    text += f"Добро пожаловать, @{username}!\n"
    text += f"Осталось запросов: {balance}\n\n"
    text += "Используйте кнопки меню для навигации.\n"
    text += "Отправьте номер телефона, ФИО или Email для поиска."

    reply_markup = get_main_menu(username)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите запрос для поиска:\n\n"
        "Примеры:\n"
        "Номер: 79149381129\n"
        "ФИО: Иванов Иван\n"
        "Email: test@mail.ru"
    )

async def handle_search_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if query.startswith('/'):
        return
    if query in ["Поиск", "Профиль", "Админ панель"]:
        return

    user_id = update.effective_user.id
    username = safe_username(update.effective_user.username)
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name
    chat_id = update.effective_chat.id

    users_db.add_user(user_id, username, first_name, last_name)
    user_balance.ensure_user(user_id, username, first_name, last_name)

    balance = user_balance.get_balance(user_id)
    if balance <= 0:
        await update.message.reply_text("У вас закончились запросы. Обратитесь к администратору.")
        return

    req_id, msg = request_queue.add_request(user_id, username, query, chat_id)
    await update.message.reply_text(msg if req_id else f"Ошибка: {msg}")

async def profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = safe_username(update.effective_user.username)

    data = user_balance.get_full_user_data(user_id)
    user_info = users_db.get_user_info(user_id)

    text = f"ПРОФИЛЬ\n\n"
    text += f"ID: {user_id}\n"
    text += f"Username: @{username}\n"
    if user_info:
        text += f"Впервые в боте: {user_info.get('first_seen', 'Неизвестно')}\n"
        text += f"Всего поисков: {user_info.get('total_searches', 0)}\n"
    text += f"Доступно запросов: {data.get('requests', 0)}\n"
    text += f"Всего получено: {data.get('total_received', 0)}\n"
    text += f"Всего использовано: {data.get('total_used', 0)}\n"

    reply_markup = get_profile_keyboard()
    await update.message.reply_text(text, reply_markup=reply_markup)

async def profile_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = user_balance.get_full_user_data(user_id)
    user_info = users_db.get_user_info(user_id)

    text = f"СТАТИСТИКА\n\n"
    text += f"Всего поисков: {user_info.get('total_searches', 0) if user_info else 0}\n"
    text += f"Доступно запросов: {data.get('requests', 0)}\n"
    text += f"Всего получено: {data.get('total_received', 0)}\n"
    text += f"Всего использовано: {data.get('total_used', 0)}"

    await query.edit_message_text(text)

async def profile_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    searches = users_db.get_user_searches(user_id, 10)

    if not searches:
        await query.edit_message_text("У вас пока нет истории поисков.")
        return

    text = "ИСТОРИЯ ПОИСКОВ\n\n"
    for i, s in enumerate(searches[:10], 1):
        text += f"{i}. {s['query']}\n   {s['date']}\n   {s['result_preview'][:50]}\n\n"

    if len(text) > 4000:
        text = text[:4000] + "\n... (обрезано)"
    await query.edit_message_text(text)

async def profile_balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    balance = user_balance.get_balance(user_id)

    text = f"ОСТАТОК ЗАПРОСОВ\n\nУ вас осталось: {balance} запросов\n\nЗапросы можно пополнить у @meskatov"
    await query.edit_message_text(text)

async def profile_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "ПОКУПКА ЗАПРОСОВ\n\n"
    text += "Купить запросы можно у @meskatov\n\n"
    text += "Прайс-лист:\n"
    text += "50 запросов = 15 звезд\n"
    text += "100 запросов = 25 звезд\n"
    text += "250 запросов = 50 звезд\n"
    text += "500 запросов = 90 звезд\n\n"
    text += "Звезды - внутренняя валюта VK Coin"
    await query.edit_message_text(text)

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.delete_message()

    user_id = query.from_user.id
    username = safe_username(query.from_user.username)
    balance = user_balance.get_balance(user_id)

    text = f"Бот meskatov search\n\nДобро пожаловать, @{username}!\nОсталось запросов: {balance}\n\nИспользуйте кнопки меню."
    reply_markup = get_main_menu(username)
    await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=reply_markup)