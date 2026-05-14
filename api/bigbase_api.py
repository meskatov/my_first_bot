# -*- coding: utf-8 -*-

import requests

BIGBASE_URL = "https://bigbase.top/api/search"
BIGBASE_TOKEN = "BOqMzQ63vPTPKs7gfUDrJru62SX2JaqC"

def search_bigbase(query):
    try:
        headers = {"Authorization": BIGBASE_TOKEN, "Content-Type": "application/json"}
        payload = {"search": query}
        response = requests.post(BIGBASE_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {"name": "BigBase", "raw_json": data, "status": "success", "full_result": str(data)[:1000]}
        return None
    except:
        return None