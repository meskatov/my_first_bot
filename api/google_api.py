# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup

def search_google(query, num_results=5):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num={num_results}"
    try:
        r = requests.get(search_url, headers=headers, timeout=15)
        if r.status_code != 200: return []
        soup = BeautifulSoup(r.text, 'html.parser')
        urls = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/url?q=' in href and 'google.com' not in href:
                match = re.search(r'/url\?q=(.*?)&', href)
                if match:
                    urls.append(match.group(1))
            elif href.startswith('http') and 'google' not in href:
                urls.append(href)
        return urls[:num_results]
    except:
        return []