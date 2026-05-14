# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup


def search_zvonili(phone):
    try:
        phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone)
        if phone_clean.startswith('8'):
            phone_clean = '7' + phone_clean[1:]
        if not phone_clean.startswith('7'):
            phone_clean = '7' + phone_clean
        phone_for_url = phone_clean[1:] if phone_clean.startswith('7') else phone_clean
        url = f"https://zvonili.com/phone/{phone_for_url}"
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ru-RU,ru;q=0.9'}
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200: return {}
        soup = BeautifulSoup(r.text, 'html.parser')
        result = {}

        title_elem = soup.find('title')
        if title_elem:
            title_text = title_elem.text
            fio_match = re.search(r'([А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+)', title_text)
            if fio_match:
                result['full_name'] = fio_match.group(1)
                parts = result['full_name'].split()
                if len(parts) >= 2:
                    result['surname'] = parts[0]
                    result['name'] = parts[1]
                if len(parts) >= 3:
                    result['patronymic'] = parts[2]

        table = soup.find('table', class_='mb-3')
        if table:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label, value = cells[0].text.strip(), cells[1].text.strip()
                    if 'Рейтинг' in label:
                        m = re.search(r'(\d+(?:\.\d+)?)/5', value)
                        if m: result['rating'] = float(m.group(1))
                    elif 'Просмотров' in label:
                        m = re.search(r'(\d+)', value)
                        if m: result['views'] = int(m.group(1))

        main = soup.find('div', class_='col-lg-9')
        if main:
            text = main.get_text()
            m = re.search(r'оператору\s+([^в]+?)\s+в', text)
            if m: result['operator'] = m.group(1).strip().strip('"')
            m = re.search(r'регионе\s+([^\n]+)', text)
            if m: result['region'] = m.group(1).strip()
            for node in main.find_all(string=True):
                if 'Тип номера:' in node:
                    nxt = node.parent.find_next()
                    if nxt:
                        types = [s.text.strip() for s in nxt.find_all('span') if s.text.strip()]
                        if types: result['phone_types'] = types
                    break
        return result
    except:
        return {}