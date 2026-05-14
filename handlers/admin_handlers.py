# -*- coding: utf-8 -*-

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import json
import os

from database.balance_db import user_balance
from database.users_db import users_db
from database.archive_db import search_archive
from database.history_db import requests_history
from utils.helpers import is_admin, add_admin, remove_admin, get_admins_list, MASTER_ADMIN, SECRET_ADMIN_PASSWORD
from utils.queue_system import request_queue
from keyboards.menus import get_admin_keyboard, get_queue_keyboard

# ================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =================
def safe_username(username):
    if username is None:
        return "no_username"
    return username

def load_requests_log():
    REQUESTS_LOG_FILE = "requests_log.json"
    if os.path.exists(REQUESTS_LOG_FILE):
        try:
            with open(REQUESTS_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"requests": [], "total_count": 0}

# ================= ОСНОВНАЯ АДМИН ПАНЕЛЬ =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_username = safe_username(update.effective_user.username)
    if not is_admin(user_username):
        await update.message.reply_text("Доступ запрещен.")
        return

    log = load_requests_log()
    users_count = len(user_balance.balances)
    total_given = sum(d.get('total_received', 0) for d in user_balance.balances.values())
    total_used = sum(d.get('total_used', 0) for d in user_balance.balances.values())
    total_users_db, total_searches_db = users_db.get_stats()

    text = "АДМИН ПАНЕЛЬ\n\n"
    text += f"Всего запросов в боте: {log['total_count']}\n"
    text += f"Пользователей: {users_count}\n"
    text += f"Всего поисков: {total_searches_db}\n"
    text += f"Выдано: {total_given}\n"
    text += f"Использовано: {total_used}\n"
    text += f"Осталось: {total_given - total_used}\n"
    text += f"В очереди: {request_queue.get_queue_stats()['waiting']}\n"
    text += f"В обработке: {request_queue.get_queue_stats()['processing']}"

    await update.message.reply_text(text, reply_markup=get_admin_keyboard())

# ================= СТАТИСТИКА =================
async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    log = load_requests_log()
    users_count = len(user_balance.balances)
    total_given = sum(d.get('total_received', 0) for d in user_balance.balances.values())
    total_used = sum(d.get('total_used', 0) for d in user_balance.balances.values())
    total_users_db, total_searches_db = users_db.get_stats()

    text = f"СТАТИСТИКА БОТА\n\n"
    text += f"Запросов в боте: {log['total_count']}\n"
    text += f"Пользователей: {users_count}\n"
    text += f"Всего поисков: {total_searches_db}\n"
    text += f"Выдано: {total_given}\n"
    text += f"Использовано: {total_used}\n"
    text += f"Осталось: {total_given - total_used}\n"
    text += f"В очереди: {request_queue.get_queue_stats()['waiting']}\n"
    text += f"В обработке: {request_queue.get_queue_stats()['processing']}"

    await query.edit_message_text(text)

# ================= ИСТОРИЯ ЗАПРОСОВ =================
async def admin_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    log = load_requests_log()
    if not log['requests']:
        await query.edit_message_text("История запросов пуста")
        return

    text = "ПОСЛЕДНИЕ 20 ЗАПРОСОВ\n\n"
    for req in log['requests'][-20:]:
        text += f"@{req['username']}: {req['query']}\n{req['timestamp']}\nРезультатов: {req['results_count']}\n\n"

    if len(text) > 4000:
        text = text[:4000] + "\n... (обрезано)"
    await query.edit_message_text(text)

# ================= АРХИВ ВСЕХ ПОИСКОВ =================
async def admin_archive_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    all_searches = search_archive.get_all_searches(30)
    if not all_searches:
        await query.edit_message_text("Архив поисков пуст")
        return

    text = "АРХИВ ВСЕХ ПОИСКОВ\n\n"
    for i, s in enumerate(all_searches[:30], 1):
        text += f"{i}. @{s['username']}\n   {s['query']}\n   {s['date']}\n   {s['result_preview'][:50]}\n\n"

    if len(text) > 4000:
        text = text[:4000] + "\n... (обрезано)"
    await query.edit_message_text(text)

# ================= ВЫДАЧА ЗАПРОСОВ =================
async def admin_give_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "ВЫДАЧА ЗАПРОСОВ\n\n"
    text += "Используйте команды:\n"
    text += "/give_self <количество> - выдать себе\n"
    text += "/add_requests @username <количество> - выдать пользователю\n\n"
    text += "Примеры:\n"
    text += "/give_self 10\n"
    text += "/add_requests @user 5"

    await query.edit_message_text(text)

# ================= ИСТОРИЯ ВЫДАЧИ ЗАПРОСОВ =================
async def admin_requests_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    today_stats = requests_history.get_today_stats()
    yesterday_stats = requests_history.get_yesterday_stats()
    week_stats = requests_history.get_week_stats()

    text = "ИСТОРИЯ ВЫДАЧИ ЗАПРОСОВ\n\n"
    text += f"СЕГОДНЯ:\n"
    text += f"  Выдано: {today_stats.get('total_requests', 0)} раз\n"
    text += f"  Всего: {today_stats.get('total_amount', 0)} запросов\n\n"
    text += f"ВЧЕРА:\n"
    text += f"  Выдано: {yesterday_stats.get('total_requests', 0)} раз\n"
    text += f"  Всего: {yesterday_stats.get('total_amount', 0)} запросов\n\n"
    text += f"ЗА НЕДЕЛЮ:\n"
    text += f"  Выдано: {week_stats.get('total_requests', 0)} раз\n"
    text += f"  Всего: {week_stats.get('total_amount', 0)} запросов\n"

    await query.edit_message_text(text)

# ================= УПРАВЛЕНИЕ ОЧЕРЕДЬЮ =================
async def admin_queue_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("УПРАВЛЕНИЕ ОЧЕРЕДЬЮ", reply_markup=get_queue_keyboard())

async def admin_queue_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    stats = request_queue.get_queue_stats()
    text = f"СТАТИСТИКА ОЧЕРЕДИ\n\nВ очереди: {stats['waiting']}\nВ обработке: {stats['processing']}"
    await query.edit_message_text(text)

async def admin_queue_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    qlist = request_queue.get_queue_list(20)
    text = "ЗАПРОСЫ В ОЧЕРЕДИ\n\n" + ("\n".join(qlist) if qlist else "Очередь пуста")
    await query.edit_message_text(text)

async def admin_queue_clear_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    count = request_queue.clear_queue()
    await query.edit_message_text(f"Очищено {count} запросов из очереди")

# ================= РАССЫЛКА =================
async def admin_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("РАССЫЛКА СООБЩЕНИЙ\n\nИспользуйте команду:\n/broadcast <текст сообщения>")

async def broadcast_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Рассылка отменена")

async def broadcast_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Отмена")

# ================= УПРАВЛЕНИЕ АДМИНАМИ =================
async def admin_admins_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    admins = get_admins_list()
    text = "УПРАВЛЕНИЕ АДМИНИСТРАТОРАМИ\n\n"
    text += "Текущие администраторы:\n"
    for a in admins:
        if a.lower() == MASTER_ADMIN.lower():
            text += f"⭐ @{a} (мастер-админ)\n"
        else:
            text += f"👤 @{a}\n"

    text += "\nКОМАНДЫ:\n/add_admin @username\n/remove_admin @username\n/list_admins\n\nТолько мастер-админ может добавлять/удалять."
    await query.edit_message_text(text)

# ================= ТОП ПОЛЬЗОВАТЕЛЕЙ =================
async def admin_top_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    top_users = user_balance.get_top_users(15)
    if not top_users:
        await query.edit_message_text("Нет данных о пользователях.")
        return

    text = "ТОП-15 ПОЛЬЗОВАТЕЛЕЙ ПО ИСПОЛЬЗОВАННЫМ ЗАПРОСАМ\n\n"
    for i, u in enumerate(top_users, 1):
        if i == 1:
            medal = "🥇 "
        elif i == 2:
            medal = "🥈 "
        elif i == 3:
            medal = "🥉 "
        else:
            medal = f"{i}. "
        text += f"{medal}@{u['username']}\n   Использовано: {u['total_used']}\n   Осталось: {u['requests_left']}\n\n"
    await query.edit_message_text(text)

# ================= СПИСОК ПОЛЬЗОВАТЕЛЕЙ =================
async def admin_users_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    users = user_balance.balances
    if not users:
        await query.edit_message_text("Список пользователей пуст.")
        return

    text = "СПИСОК ПОЛЬЗОВАТЕЛЕЙ\n\n"
    for uid_str, data in list(users.items())[:30]:
        username = data.get('username', 'unknown')
        requests_left = data.get('requests', 0)
        total_used = data.get('total_used', 0)
        text += f"ID: {uid_str} | @{username}\n  Запросов: {requests_left} (использовано {total_used})\n\n"

    if len(users) > 30:
        text += f"... и еще {len(users) - 30} пользователей\n"
    await query.edit_message_text(text)

# ================= НАЗАД =================
async def admin_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await admin_panel(update, context)

# ================= АДМИН КОМАНДЫ =================
async def give_self_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_username = safe_username(update.effective_user.username)
    if not is_admin(user_username):
        await update.message.reply_text("Доступ запрещен.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /give_self <количество>")
        return

    try:
        amount = int(context.args[0])
        if amount <= 0:
            await update.message.reply_text("Количество должно быть больше 0")
            return
        user_id = update.effective_user.id
        username = safe_username(update.effective_user.username)
        new_balance = user_balance.add_requests(user_id, username, amount)
        await update.message.reply_text(f"Выдано {amount} запросов себе. Теперь доступно: {new_balance}")
    except:
        await update.message.reply_text("Ошибка")

async def add_requests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_username = safe_username(update.effective_user.username)
    if not is_admin(user_username):
        await update.message.reply_text("Доступ запрещен.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /add_requests @username <количество>")
        return

    target = context.args[0].replace("@", "")
    try:
        amount = int(context.args[1])
        if amount <= 0:
            await update.message.reply_text("Количество должно быть больше 0")
            return
    except:
        await update.message.reply_text("Ошибка")
        return

    target_id = user_balance.find_user_by_username(target)
    if not target_id:
        await update.message.reply_text(f"Пользователь @{target} не найден. Пусть напишет /start.")
        return

    new_balance = user_balance.add_requests(target_id, target, amount)
    await update.message.reply_text(f"Выдано {amount} запросов @{target}. Теперь доступно: {new_balance}")

async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_username = safe_username(update.effective_user.username)
    if user_username != MASTER_ADMIN:
        await update.message.reply_text("Только мастер-админ может добавлять админов.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /add_admin @username")
        return

    new_admin = context.args[0].replace("@", "").lower()
    if add_admin(new_admin):
        await update.message.reply_text(f"Админ @{new_admin} добавлен!")
    else:
        await update.message.reply_text("Админ уже существует")

async def remove_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_username = safe_username(update.effective_user.username)
    if user_username != MASTER_ADMIN:
        await update.message.reply_text("Только мастер-админ может удалять админов.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /remove_admin @username")
        return

    admin_to_remove = context.args[0].replace("@", "").lower()
    if remove_admin(admin_to_remove):
        await update.message.reply_text(f"Админ @{admin_to_remove} удален")
    else:
        await update.message.reply_text("Нельзя удалить главного админа")

async def list_admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = get_admins_list()
    text = "СПИСОК АДМИНИСТРАТОРОВ\n\n"
    for a in admins:
        if a.lower() == MASTER_ADMIN.lower():
            text += f"⭐ @{a} (мастер-админ)\n"
        else:
            text += f"👤 @{a}\n"
    await update.message.reply_text(text)

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_username = safe_username(update.effective_user.username)
    if not is_admin(user_username):
        await update.message.reply_text("Доступ запрещен.")
        return

    if not context.args:
        await update.message.reply_text("Использование: /broadcast <сообщение>")
        return

    message = ' '.join(context.args)
    keyboard = [
        [InlineKeyboardButton("ДА, отправить всем", callback_data="broadcast_confirm")],
        [InlineKeyboardButton("НЕТ, отмена", callback_data="broadcast_cancel")]
    ]
    await update.message.reply_text(
        f"ВНИМАНИЕ!\n\nВы собираетесь отправить сообщение ВСЕМ пользователям бота.\n\n"
        f"Текст сообщения:\n{message}\n\nКоличество пользователей: {len(user_balance.balances)}\n\n"
        f"Подтвердите отправку:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['broadcast_message'] = message

async def secret_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_username = safe_username(update.effective_user.username)
    if user_username != MASTER_ADMIN:
        await update.message.reply_text("Доступ запрещен. Только мастер-админ.")
        return

    if not context.args:
        await update.message.reply_text(
            f"СЕКРЕТНАЯ АДМИН ПАНЕЛЬ\n\n"
            f"Использование: /secret {SECRET_ADMIN_PASSWORD}\n\n"
            f"Пароль: {SECRET_ADMIN_PASSWORD}"
        )
        return

    if context.args[0] != SECRET_ADMIN_PASSWORD:
        await update.message.reply_text("Неверный пароль! Доступ запрещен.")
        return

    log = load_requests_log()
    text = "СЕКРЕТНАЯ АДМИН ПАНЕЛЬ\n\n"
    text += f"Всего запросов в боте: {log['total_count']}\n"
    text += f"Пользователей: {len(user_balance.balances)}\n"
    await update.message.reply_text(text)