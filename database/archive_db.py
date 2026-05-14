# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

BASE_USER_FOLDER = "base_user"
ARCHIVE_FILE = os.path.join(BASE_USER_FOLDER, "search_archive.json")

class SearchArchive:
    def __init__(self):
        self.archives = {}
        self.load_archive()

    def load_archive(self):
        if os.path.exists(ARCHIVE_FILE):
            try:
                with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
                    self.archives = json.load(f)
            except:
                self.archives = {}

    def save_archive(self):
        try:
            with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.archives, f, ensure_ascii=False, indent=2)
        except:
            pass

    def add_search(self, user_id, username, query, result_preview, full_result=''):
        user_id_str = str(user_id)
        if user_id_str not in self.archives:
            self.archives[user_id_str] = []
        self.archives[user_id_str].append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'username': username,
            'query': query,
            'result_preview': result_preview[:200],
            'full_result': full_result[:1000] if full_result else ''
        })
        self.save_archive()

    def get_all_searches(self, limit=50):
        all_searches = []
        for user_id_str, searches in self.archives.items():
            for search in searches:
                all_searches.append({
                    'user_id': user_id_str,
                    'username': search.get('username', 'unknown'),
                    'date': search['date'],
                    'query': search['query'],
                    'result_preview': search.get('result_preview', '')
                })
        all_searches.sort(key=lambda x: x['date'], reverse=True)
        return all_searches[:limit]

search_archive = SearchArchive()