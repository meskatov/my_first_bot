# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

BASE_USER_FOLDER = "base_user"
USERS_INFO_FILE = os.path.join(BASE_USER_FOLDER, "users_info.json")

class UsersDatabase:
    def __init__(self):
        self.users = {}
        self.load_users()

    def load_users(self):
        if os.path.exists(USERS_INFO_FILE):
            try:
                with open(USERS_INFO_FILE, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except:
                self.users = {}

    def save_users(self):
        try:
            with open(USERS_INFO_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except:
            pass

    def add_user(self, user_id, username, first_name=None, last_name=None):
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            self.users[user_id_str] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'first_seen': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'last_seen': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_searches': 0,
                'searches': []
            }
            self.save_users()
            return True
        else:
            self.users[user_id_str]['last_seen'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if username:
                self.users[user_id_str]['username'] = username
            self.save_users()
        return False

    def add_search(self, user_id, query, result_preview):
        user_id_str = str(user_id)
        if user_id_str in self.users:
            self.users[user_id_str]['total_searches'] += 1
            self.users[user_id_str]['searches'].append({
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'query': query,
                'result_preview': result_preview[:100]
            })
            self.save_users()

    def get_user_info(self, user_id):
        return self.users.get(str(user_id))

    def get_user_searches(self, user_id, limit=20):
        user_id_str = str(user_id)
        if user_id_str in self.users:
            return self.users[user_id_str]['searches'][-limit:][::-1]
        return []

    def get_all_users(self):
        return self.users

    def get_stats(self):
        total_users = len(self.users)
        total_searches = sum(u.get('total_searches', 0) for u in self.users.values())
        return total_users, total_searches

users_db = UsersDatabase()