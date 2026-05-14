# -*- coding: utf-8 -*-

import os

ADMINS_FILE = "admins.txt"
MASTER_ADMIN = "meskatov"
SECRET_ADMIN_PASSWORD = "meskatov2024"

def load_admins():
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
                admins = [line.strip() for line in f.readlines() if line.strip()]
                if MASTER_ADMIN not in admins:
                    admins.append(MASTER_ADMIN)
                return admins
        except:
            return [MASTER_ADMIN]
    return [MASTER_ADMIN]

def save_admins(admins):
    try:
        with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(admins))
    except:
        pass

def is_admin(username):
    if username is None or not username:
        return False
    admins = load_admins()
    return username.lower() in [a.lower() for a in admins]

def add_admin(username):
    if username is None:
        return False
    admins = load_admins()
    username_lower = username.lower()
    existing = [a.lower() for a in admins]
    if username_lower not in existing:
        admins.append(username)
        save_admins(admins)
        return True
    return False

def remove_admin(username):
    if username is None:
        return False
    if username.lower() == MASTER_ADMIN.lower():
        return False
    admins = load_admins()
    admins = [a for a in admins if a.lower() != username.lower()]
    save_admins(admins)
    return True

def get_admins_list():
    return load_admins()