from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def reminders_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📋 Мои напоминания"))
    kb.row(KeyboardButton("➕ Добавить"))
    kb.row(KeyboardButton("🔙 Назад"))
    return kb
