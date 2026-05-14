# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime

from database.balance_db import user_balance
from database.archive_db import search_archive
from database.users_db import users_db


def add_request_to_log(user_id, username, query, results_count):
    import os
    REQUESTS_LOG_FILE = "requests_log.json"

    def load_requests_log():
        if os.path.exists(REQUESTS_LOG_FILE):
            try:
                with open(REQUESTS_LOG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"requests": [], "total_count": 0}

    def save_requests_log(log):
        try:
            with open(REQUESTS_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(log, f, indent=4, ensure_ascii=False)
        except:
            pass

    log = load_requests_log()
    log["requests"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "username": username,
        "query": query,
        "results_count": results_count
    })
    log["total_count"] += 1
    if len(log["requests"]) > 1000:
        log["requests"] = log["requests"][-1000:]
    save_requests_log(log)


async def process_request(app, request):
    try:
        # Простой поиск для теста
        output = f"Результаты поиска по запросу: {request['query']}\n\n"
        output += "Данные найдены в тестовом режиме.\n"
        output += f"Пользователь: @{request['username']}\n"
        output += f"Время: {request['timestamp']}\n\n"

        remaining = user_balance.get_balance(request['user_id'])
        output += f"Осталось запросов: {remaining}"

        search_archive.add_search(request['user_id'], request['username'], request['query'], "Тестовый поиск")

        await app.bot.send_message(chat_id=request['chat_id'], text=output)
        add_request_to_log(request['user_id'], request['username'], request['query'], 1)

    except Exception as e:
        try:
            await app.bot.send_message(chat_id=request['chat_id'], text=f"Ошибка обработки: {e}")
        except:
            pass