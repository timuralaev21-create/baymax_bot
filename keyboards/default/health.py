from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def health_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📊 Мой профиль"))
    kb.row(KeyboardButton("⚖️ Изменить вес"), KeyboardButton("💧 Выпил воду"))
    kb.row(KeyboardButton("🚶 Добавить шаги"), KeyboardButton("🔄 Сбросить воду"))
    kb.row(KeyboardButton("🔙 Назад"))
    return kb
