from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def day_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📅 План на сегодня"), KeyboardButton("➕ Добавить план"))
    kb.row(KeyboardButton("🎯 Цели"), KeyboardButton("➕ Добавить цель"))
    kb.row(KeyboardButton("➖ Убрать цель"), KeyboardButton("🗑 Очистить план"))
    kb.row(KeyboardButton("💓 Пульс дня"))
    kb.row(KeyboardButton("🔙 Назад"))
    return kb
