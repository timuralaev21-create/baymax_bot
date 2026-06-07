from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def study_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📖 Объяснить тему"), KeyboardButton("⏱ Решить на время"))
    kb.row(KeyboardButton("🔙 Назад"))
    return kb
