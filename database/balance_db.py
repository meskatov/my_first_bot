# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

BASE_USER_FOLDER = "base_user"
USERS_FILE = os.path.join(BASE_USER_FOLDER, "users_balance.json")

class UserBalance:
    def __init__(self):
        self.balances = {}
        self.load_balances()

    def load_balances(self):
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    self.balances = json.load(f)
            except:
                self.balances = {}
        else:
            self.save_balances()

    def save_balances(self):
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.balances, f, ensure_ascii=False, indent=2)
        except:
            pass

    def ensure_user(self, user_id, username=None, first_name=None, last_name=None):
        user_id_str = str(user_id)
        if user_id_str not in self.balances:
            self.balances[user_id_str] = {
                'user_id': user_id,
                'username': username,
                'requests': 3,
                'total_used': 0,
                'total_received': 3,
                'last_active': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.save_balances()
            return True
        elif username and not self.balances[user_id_str].get('username'):
            self.balances[user_id_str]['username'] = username
            self.save_balances()
        return False

    def get_balance(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.balances:
            return 3
        return self.balances[user_id_str].get('requests', 3)

    def get_full_user_data(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.balances:
            return {
                'user_id': user_id,
                'username': None,
                'requests': 3,
                'total_used': 0,
                'total_received': 3,
                'last_active': None
            }
        return self.balances[user_id_str]

    def add_requests(self, user_id, username, amount, admin_id=None, admin_username=None):
        user_id_str = str(user_id)
        balance_before = self.get_balance(user_id)

        if user_id_str not in self.balances:
            self.balances[user_id_str] = {
                'user_id': user_id,
                'username': username,
                'requests': 0,
                'total_used': 0,
                'total_received': 0,
                'last_active': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        self.balances[user_id_str]['requests'] += amount
        self.balances[user_id_str]['total_received'] += amount
        if username:
            self.balances[user_id_str]['username'] = username
        self.save_balances()
        return self.balances[user_id_str]['requests']

    def use_request(self, user_id):
        user_id_str = str(user_id)
        if user_id_str not in self.balances:
            return False
        if self.balances[user_id_str]['requests'] > 0:
            self.balances[user_id_str]['requests'] -= 1
            self.balances[user_id_str]['total_used'] += 1
            self.balances[user_id_str]['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_balances()
            return True
        return False

    def get_top_users(self, limit=15):
        users = []
        for uid, data in self.balances.items():
            users.append({
                'user_id': data['user_id'],
                'username': data.get('username', str(data['user_id'])),
                'requests_left': data.get('requests', 0),
                'total_used': data.get('total_used', 0),
                'total_received': data.get('total_received', 0)
            })
        users.sort(key=lambda x: x['total_used'], reverse=True)
        return users[:limit]

    def find_user_by_username(self, username):
        username = username.lower().replace('@', '')
        for uid, data in self.balances.items():
            if data.get('username', '').lower() == username:
                return int(uid)
        return None

user_balance = UserBalance()