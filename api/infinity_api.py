# -*- coding: utf-8 -*-

import requests
import re

INFINITY_API_URL = "https://infinity-check.online/find.php"
INFINITY_TOKEN = "R8fK2Lm9QWv3E7ZpD1yU4C6VtX5H0BJs"


def search_infinity(query):
    try:
        params = {"token": INFINITY_TOKEN}

        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', query):
            params["email"] = query
        elif re.match(r'^[\d\(\)\+ \-]{7,}$', query):
            phone_clean = re.sub(r'\D', '', query)
            if phone_clean.startswith('8'):
                phone_clean = '7' + phone_clean[1:]
            elif len(phone_clean) == 10:
                phone_clean = '7' + phone_clean
            params["phone"] = phone_clean
        elif re.match(r'^[А-Яа-я\s]{4,}$', query):
            params["fio"] = query
        else:
            params["nick"] = query

        response = requests.get(INFINITY_API_URL, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                return {"name": "Infinity", "raw_json": data, "status": "success", "full_result": str(data)[:1000]}
        return None
    except:
        return None