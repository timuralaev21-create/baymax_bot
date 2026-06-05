from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def study_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("❓ Задать вопрос"))
    kb.row(KeyboardButton("📝 План на день"))
    kb.row(KeyboardButton("🔙 Назад"))
    return kb
