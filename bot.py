#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.request import HTTPXRequest

from handlers.user_handlers import (
    start, search_handler, handle_search_query, profile_menu,
    profile_stats_callback, profile_history_callback, profile_balance_callback, profile_buy_callback,
    back_to_menu_callback
)
from handlers.admin_handlers import (
    admin_panel, admin_stats_callback, admin_history_callback, admin_archive_callback,
    admin_give_menu_callback, admin_queue_menu_callback, admin_queue_stats_callback,
    admin_queue_list_callback, admin_queue_clear_callback, admin_broadcast_callback,
    admin_admins_menu_callback, admin_top_callback, admin_users_list_callback,
    admin_back_callback, give_self_command, add_requests_command, add_admin_command,
    remove_admin_command, list_admins_command, broadcast_message, broadcast_confirm_callback,
    broadcast_cancel_callback, secret_admin
)

REQUEST_KWARGS = {
    "connect_timeout": 60.0,
    "read_timeout": 60.0,
    "write_timeout": 60.0,
    "pool_timeout": 60.0,
}

custom_request = HTTPXRequest(**REQUEST_KWARGS)
TELEGRAM_TOKEN = "8653236048:AAGf5myZsJA7AoexDVVtCXQ5R6eMVltRrQE"

async def post_init(app):
    from utils.queue_system import queue_processor
    asyncio.create_task(queue_processor(app))
    print("Обработчик очереди запущен")

def main():
    print("=" * 50)
    print("Бот meskatov search запускается...")
    print("=" * 50)

    try:
        app = Application.builder().token(TELEGRAM_TOKEN).request(custom_request).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("give_self", give_self_command))
        app.add_handler(CommandHandler("add_requests", add_requests_command))
        app.add_handler(CommandHandler("add_admin", add_admin_command))
        app.add_handler(CommandHandler("remove_admin", remove_admin_command))
        app.add_handler(CommandHandler("list_admins", list_admins_command))
        app.add_handler(CommandHandler("broadcast", broadcast_message))
        app.add_handler(CommandHandler("secret", secret_admin))

        app.add_handler(MessageHandler(filters.Regex("^Поиск$"), search_handler))
        app.add_handler(MessageHandler(filters.Regex("^Профиль$"), profile_menu))
        app.add_handler(MessageHandler(filters.Regex("^Админ панель$"), admin_panel))

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_query))

        app.add_handler(CallbackQueryHandler(profile_stats_callback, pattern="profile_stats"))
        app.add_handler(CallbackQueryHandler(profile_history_callback, pattern="profile_history"))
        app.add_handler(CallbackQueryHandler(profile_balance_callback, pattern="profile_balance"))
        app.add_handler(CallbackQueryHandler(profile_buy_callback, pattern="profile_buy"))
        app.add_handler(CallbackQueryHandler(admin_stats_callback, pattern="admin_stats"))
        app.add_handler(CallbackQueryHandler(admin_history_callback, pattern="admin_history"))
        app.add_handler(CallbackQueryHandler(admin_archive_callback, pattern="admin_archive"))
        app.add_handler(CallbackQueryHandler(admin_give_menu_callback, pattern="admin_give_menu"))
        app.add_handler(CallbackQueryHandler(admin_queue_menu_callback, pattern="admin_queue_menu"))
        app.add_handler(CallbackQueryHandler(admin_queue_stats_callback, pattern="admin_queue_stats"))
        app.add_handler(CallbackQueryHandler(admin_queue_list_callback, pattern="admin_queue_list"))
        app.add_handler(CallbackQueryHandler(admin_queue_clear_callback, pattern="admin_queue_clear"))
        app.add_handler(CallbackQueryHandler(admin_broadcast_callback, pattern="admin_broadcast"))
        app.add_handler(CallbackQueryHandler(admin_admins_menu_callback, pattern="admin_admins_menu"))
        app.add_handler(CallbackQueryHandler(admin_top_callback, pattern="admin_top"))
        app.add_handler(CallbackQueryHandler(admin_users_list_callback, pattern="admin_users_list"))
        app.add_handler(CallbackQueryHandler(admin_back_callback, pattern="admin_back"))
        app.add_handler(CallbackQueryHandler(broadcast_confirm_callback, pattern="broadcast_confirm"))
        app.add_handler(CallbackQueryHandler(broadcast_cancel_callback, pattern="broadcast_cancel"))
        app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="back_to_menu"))

        app.post_init = post_init

        print("Бот успешно запущен!")
        app.run_polling()

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()