# -*- coding: utf-8 -*-

import requests
import re

EYECON_URL = "https://api.eyecon-app.com/app/getnames.jsp"
EYECON_AUTH = "d9889e1c-521c-4ded-9b15-f64bb069148b"


def search_eyecon(phone):
    try:
        clean_phone = re.sub(r'[^\d]', '', phone)
        if clean_phone.startswith('7') and len(clean_phone) == 11:
            formatted_phone = clean_phone
        elif clean_phone.startswith('8') and len(clean_phone) == 11:
            formatted_phone = f"7{clean_phone[1:]}"
        elif len(clean_phone) == 10:
            formatted_phone = f"7{clean_phone}"
        else:
            formatted_phone = clean_phone

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept": "application/json",
            "e-auth-v": "e1",
            "e-auth": EYECON_AUTH,
            "e-auth-c": "46",
            "e-auth-k": "PgdtSBeR0MumR7fO",
            "content-type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        params = {"cli": formatted_phone, "lang": "ru", "is_callerid": "true", "is_ic": "true",
                  "cv": "vc_742_vn_4.2026.02.24.1801_a", "requestApi": "URLconnection", "source": "MenifaFragment"}

        r = requests.get(EYECON_URL, headers=headers, params=params, timeout=10)
        if r.status_code != 200: return {}
        data = r.json()
        result = {}
        if isinstance(data, dict):
            if data.get('name'):
                result['fio'] = data['name']
                result['name'] = data['name']
            if data.get('company'):
                result['company'] = data['company']
        return result
    except:
        return {}