# -*- coding: utf-8 -*-

import requests
import json
import re

CRYVEN_API_KEY = "@meskatov:XR7ecB9K"
CRYVEN_BASE_URL = "https://cryven.info/api"


def search_cryven_all(query):
    """Поиск по номеру телефона (method=all)"""
    try:
        phone_clean = re.sub(r'[\s\-\(\)\+]', '', query)
        if not phone_clean.isdigit() or len(phone_clean) < 10:
            return None

        if len(phone_clean) == 11 and phone_clean.startswith('8'):
            phone_clean = '7' + phone_clean[1:]
        elif len(phone_clean) == 10:
            phone_clean = '7' + phone_clean
        elif len(phone_clean) == 11 and phone_clean.startswith('7'):
            phone_clean = phone_clean

        url = f"{CRYVEN_BASE_URL}/search"
        params = {
            "key": CRYVEN_API_KEY,
            "search": phone_clean,
            "method": "all"
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    "name": "Cryven_All",
                    "raw_json": data,
                    "status": "success",
                    "full_result": json.dumps(data, ensure_ascii=False)[:1000]
                }
        return None
    except Exception as e:
        print(f"Ошибка в search_cryven_all: {e}")
        return None


def search_cryven_telegram(query):
    """Поиск по Telegram username"""
    try:
        username = query.strip()
        if not username.startswith('@'):
            username = '@' + username

        url = f"{CRYVEN_BASE_URL}/telegram/search"
        params = {
            "key": CRYVEN_API_KEY,
            "search": username
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    "name": "Cryven_Telegram",
                    "raw_json": data,
                    "status": "success",
                    "full_result": json.dumps(data, ensure_ascii=False)[:1000]
                }
        return None
    except Exception as e:
        print(f"Ошибка в search_cryven_telegram: {e}")
        return None


def search_cryven_email(query):
    """Поиск по email"""
    try:
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', query):
            return None

        url = f"{CRYVEN_BASE_URL}/search"
        params = {
            "key": CRYVEN_API_KEY,
            "search": query,
            "method": "email"
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    "name": "Cryven_Email",
                    "raw_json": data,
                    "status": "success",
                    "full_result": json.dumps(data, ensure_ascii=False)[:1000]
                }
        return None
    except Exception as e:
        print(f"Ошибка в search_cryven_email: {e}")
        return None


def search_cryven_fio(query):
    """Поиск по ФИО"""
    try:
        if not re.match(r'^[А-Яа-я\s]{4,}$', query):
            return None

        url = f"{CRYVEN_BASE_URL}/search"
        params = {
            "key": CRYVEN_API_KEY,
            "search": query,
            "method": "fio"
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    "name": "Cryven_FIO",
                    "raw_json": data,
                    "status": "success",
                    "full_result": json.dumps(data, ensure_ascii=False)[:1000]
                }
        return None
    except Exception as e:
        print(f"Ошибка в search_cryven_fio: {e}")
        return None


def search_cryven_nick(query):
    """Поиск по нику"""
    try:
        if len(query) < 3:
            return None

        url = f"{CRYVEN_BASE_URL}/search"
        params = {
            "key": CRYVEN_API_KEY,
            "search": query,
            "method": "nick"
        }

        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {
                    "name": "Cryven_Nick",
                    "raw_json": data,
                    "status": "success",
                    "full_result": json.dumps(data, ensure_ascii=False)[:1000]
                }
        return None
    except Exception as e:
        print(f"Ошибка в search_cryven_nick: {e}")
        return None