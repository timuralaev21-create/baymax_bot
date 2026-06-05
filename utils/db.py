import sqlite3
from datetime import datetime

from data import config

DB_PATH = 'baymax.db'


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


async def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            height INTEGER DEFAULT 175,
            weight REAL DEFAULT 89,
            water_ml INTEGER DEFAULT 0,
            steps INTEGER DEFAULT 0,
            created_at TEXT
        )
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            sent INTEGER DEFAULT 0
        )
        '''
    )
    conn.commit()
    conn.close()


async def create_or_update_user(user_id: int, full_name: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    exists = cur.fetchone()
    if exists:
        cur.execute('UPDATE users SET full_name = ? WHERE user_id = ?', (full_name, user_id))
    else:
        cur.execute(
            '''
            INSERT INTO users (user_id, full_name, height, weight, water_ml, steps, created_at)
            VALUES (?, ?, ?, ?, 0, 0, ?)
            ''',
            (
                user_id,
                full_name,
                config.DEFAULT_HEIGHT,
                config.DEFAULT_WEIGHT,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )
    conn.commit()
    conn.close()


async def get_user(user_id: int):
    conn = _connect()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


async def update_weight(user_id: int, weight: float):
    conn = _connect()
    cur = conn.cursor()
    cur.execute('UPDATE users SET weight = ? WHERE user_id = ?', (weight, user_id))
    conn.commit()
    conn.close()


async def add_water(user_id: int, ml: int = 250):
    conn = _connect()
    cur = conn.cursor()
    cur.execute('UPDATE users SET water_ml = water_ml + ? WHERE user_id = ?', (ml, user_id))
    conn.commit()
    conn.close()


async def reset_water(user_id: int):
    conn = _connect()
    cur = conn.cursor()
    cur.execute('UPDATE users SET water_ml = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()


async def add_steps(user_id: int, steps: int):
    conn = _connect()
    cur = conn.cursor()
    cur.execute('UPDATE users SET steps = steps + ? WHERE user_id = ?', (steps, user_id))
    conn.commit()
    conn.close()


async def create_reminder(user_id: int, text: str, remind_at: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO reminders (user_id, text, remind_at, sent) VALUES (?, ?, ?, 0)',
        (user_id, text, remind_at)
    )
    conn.commit()
    conn.close()


async def get_user_reminders(user_id: int, only_active: bool = True):
    conn = _connect()
    cur = conn.cursor()
    if only_active:
        cur.execute(
            'SELECT * FROM reminders WHERE user_id = ? AND sent = 0 ORDER BY remind_at ASC',
            (user_id,)
        )
    else:
        cur.execute('SELECT * FROM reminders WHERE user_id = ? ORDER BY remind_at DESC', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


async def get_due_reminders(now_str: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        'SELECT * FROM reminders WHERE sent = 0 AND remind_at <= ? ORDER BY remind_at ASC',
        (now_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


async def mark_reminder_sent(reminder_id: int):
    conn = _connect()
    cur = conn.cursor()
    cur.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()
