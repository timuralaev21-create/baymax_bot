from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def health_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("📊 Мой профиль"), KeyboardButton("🧮 Рассчитать норму"))
    kb.row(KeyboardButton("💧 Выпил воду"), KeyboardButton("🔄 Сбросить воду"))
    kb.row(KeyboardButton("🚶 Добавить шаги"), KeyboardButton("🧠 Ментальное"))
    kb.row(KeyboardButton("🩺 Физическое"), KeyboardButton("📍 Ближайшие аптеки", request_location=True))
    kb.row(KeyboardButton("🔙 Назад"))
    return kb
