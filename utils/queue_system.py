# -*- coding: utf-8 -*-

import asyncio
import json
import os
from collections import deque
from datetime import datetime

from database.balance_db import user_balance

QUEUE_FILE = "queue_data.json"
MAX_CONCURRENT_REQUESTS = 3
MAX_QUEUE_SIZE = 50


class RequestQueue:
    def __init__(self):
        self.queue = deque()
        self.processing = {}
        self.request_id_counter = 0
        self.load_queue_state()

    def load_queue_state(self):
        if os.path.exists(QUEUE_FILE):
            try:
                with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.queue = deque(data.get('queue', []))
                    self.request_id_counter = data.get('request_id_counter', 0)
            except:
                pass

    def save_queue_state(self):
        try:
            data = {
                'queue': list(self.queue),
                'request_id_counter': self.request_id_counter
            }
            with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def add_request(self, user_id, username, query, chat_id, message_id=None):
        if len(self.queue) >= MAX_QUEUE_SIZE:
            return None, "Очередь переполнена. Попробуйте позже."
        balance = user_balance.get_balance(user_id)
        if balance <= 0:
            return None, "У вас закончились запросы. Обратитесь к администратору."
        self.request_id_counter += 1
        request = {
            'id': self.request_id_counter,
            'user_id': user_id,
            'username': username,
            'query': query,
            'chat_id': chat_id,
            'message_id': message_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'waiting'
        }
        self.queue.append(request)
        self.save_queue_state()
        return request['id'], f"Запрос добавлен в очередь. Позиция: {len(self.queue)}\nОсталось запросов: {balance - 1}"

    def get_next_request(self):
        if self.queue:
            request = self.queue.popleft()
            request['status'] = 'processing'
            self.processing[request['id']] = request
            self.save_queue_state()
            return request
        return None

    def complete_request(self, request_id):
        if request_id in self.processing:
            del self.processing[request_id]
            self.save_queue_state()
            return True
        return False

    def get_queue_position(self, user_id):
        for i, req in enumerate(self.queue):
            if req['user_id'] == user_id:
                return i + 1
        return None

    def get_queue_stats(self):
        return {'waiting': len(self.queue), 'processing': len(self.processing)}

    def clear_queue(self):
        count = len(self.queue)
        self.queue.clear()
        self.save_queue_state()
        return count

    def get_queue_list(self, limit=20):
        result = []
        for i, req in enumerate(self.queue[:limit], 1):
            result.append(f"{i}. @{req['username']}: {req['query'][:50]}...")
        return result


request_queue = RequestQueue()


async def queue_processor(app):
    from handlers.process_handler import process_request

    while True:
        try:
            if len(request_queue.processing) < MAX_CONCURRENT_REQUESTS:
                request = request_queue.get_next_request()
                if request:
                    if user_balance.use_request(request['user_id']):
                        await process_request(app, request)
                    else:
                        try:
                            await app.bot.send_message(
                                chat_id=request['chat_id'],
                                text="У вас недостаточно запросов. Обратитесь к администратору."
                            )
                        except:
                            pass
                        request_queue.complete_request(request['id'])
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Ошибка в очереди: {e}")
            await asyncio.sleep(5)