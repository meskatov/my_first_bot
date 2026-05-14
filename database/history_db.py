# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta

BASE_USER_FOLDER = "base_user"
REQUESTS_HISTORY_FILE = os.path.join(BASE_USER_FOLDER, "requests_history.json")

class RequestsHistory:
    def __init__(self):
        self.history = {}
        self.load_history()

    def load_history(self):
        if os.path.exists(REQUESTS_HISTORY_FILE):
            try:
                with open(REQUESTS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = {}

    def save_history(self):
        try:
            with open(REQUESTS_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def add_request(self, admin_id, admin_username, user_id, user_username, amount, balance_before, balance_after):
        date_str = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if date_str not in self.history:
            self.history[date_str] = {
                'date': date_str,
                'total_requests': 0,
                'total_amount': 0,
                'requests': []
            }

        self.history[date_str]['total_requests'] += 1
        self.history[date_str]['total_amount'] += amount
        self.history[date_str]['requests'].append({
            'timestamp': timestamp,
            'admin_id': admin_id,
            'admin_username': admin_username,
            'user_id': user_id,
            'user_username': user_username,
            'amount': amount,
            'balance_before': balance_before,
            'balance_after': balance_after
        })
        self.save_history()

    def get_today_stats(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        if date_str in self.history:
            return self.history[date_str]
        return {'total_requests': 0, 'total_amount': 0, 'requests': []}

    def get_yesterday_stats(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if yesterday in self.history:
            return self.history[yesterday]
        return {'total_requests': 0, 'total_amount': 0, 'requests': []}

    def get_week_stats(self):
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        total_requests = 0
        total_amount = 0
        for date_str, data in self.history.items():
            if date_str >= week_ago:
                total_requests += data.get('total_requests', 0)
                total_amount += data.get('total_amount', 0)
        return {'total_requests': total_requests, 'total_amount': total_amount}

    def get_all_history(self, limit=30):
        dates = sorted(self.history.keys(), reverse=True)
        result = []
        for date_str in dates[:limit]:
            result.append(self.history[date_str])
        return result

requests_history = RequestsHistory()