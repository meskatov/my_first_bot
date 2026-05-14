# -*- coding: utf-8 -*-

import requests

DEPSEARCH_TOKEN = "WDTHx2vqZGE38gchBe7oAewzB9ZPNpxU"
DEPSEARCH_BASE_URL = "https://api.depsearch.sbs/"

def search_depsearch(query):
    try:
        url = f"{DEPSEARCH_BASE_URL}quest={query}&token={DEPSEARCH_TOKEN}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {"name": "DepSearch", "raw_json": data, "status": "success", "full_result": str(data)[:1000]}
        return None
    except:
        return None