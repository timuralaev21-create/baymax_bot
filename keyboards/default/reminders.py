from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def reminders_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📋 Мои напоминания"), KeyboardButton("➕ Добавить"))
    kb.row(KeyboardButton("🔙 Назад"))
    return kb
