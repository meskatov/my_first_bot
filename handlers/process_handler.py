# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime

from database.balance_db import user_balance
from database.archive_db import search_archive
from utils.formatter import format_dossier, print_dossier
from api.infinity_api import search_infinity
from api.depsearch_api import search_depsearch
from api.bigbase_api import search_bigbase
from api.eyecon_api import search_eyecon
from api.zvonili_api import search_zvonili
from api.google_api import search_google


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
        all_data = []
        full_results = []

        # Infinity API
        result = search_infinity(request['query'])
        if result:
            data = result["raw_json"]
            if data.get("results"):
                all_data.extend(data["results"])

        # DepSearch API
        result = search_depsearch(request['query'])
        if result:
            data = result["raw_json"]
            if isinstance(data, list):
                all_data.extend(data)
            elif isinstance(data, dict) and data.get("results"):
                all_data.extend(data["results"])
            elif isinstance(data, dict):
                all_data.append(data)

        # BigBase API
        result = search_bigbase(request['query'])
        if result:
            data = result["raw_json"]
            if isinstance(data, list):
                all_data.extend(data)
            elif isinstance(data, dict) and data.get("results"):
                all_data.extend(data["results"])
            elif isinstance(data, dict):
                all_data.append(data)

        # Eyecon API (для телефонов)
        if re.search(r'[\d\(\)\+ \-]{7,}', request['query']):
            eyecon_result = search_eyecon(request['query'])
            if eyecon_result:
                all_data.append(eyecon_result)

            zvonili_result = search_zvonili(request['query'])
            if zvonili_result:
                all_data.append(zvonili_result)

        # Google Search
        google_results = search_google(request['query'], 5)
        if google_results:
            all_data.append({'google_links': google_results})

        if all_data:
            dossier = format_dossier(all_data, request['query'])
            output = print_dossier(dossier, request['query'])
            if dossier.get('📛 ФИО') and dossier['📛 ФИО']:
                result_preview = f"Найдено: {', '.join(dossier['📛 ФИО'][:2])}"
            else:
                result_preview = "Найдены данные"
        else:
            output = "Ничего не найдено"
            result_preview = "Ничего не найдено"

        # Google ссылки
        if 'google_links' in str(all_data):
            for item in all_data:
                if isinstance(item, dict) and 'google_links' in item:
                    output += "\n\n🔗 Google Search:\n"
                    for i, url in enumerate(item['google_links'][:5], 1):
                        output += f"{i}. {url}\n"

        remaining = user_balance.get_balance(request['user_id'])
        output += f"\n\nОсталось запросов: {remaining}"

        search_archive.add_search(request['user_id'], request['username'], request['query'], result_preview)

        await app.bot.send_message(chat_id=request['chat_id'], text=output)
        add_request_to_log(request['user_id'], request['username'], request['query'], len(all_data))

    except Exception as e:
        try:
            await app.bot.send_message(chat_id=request['chat_id'], text=f"Ошибка: {e}")
        except:
            pass