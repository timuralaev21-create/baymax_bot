from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("💧 Здоровье"), KeyboardButton("⏰ Напоминания"))
    kb.row(KeyboardButton("📝 День и цели"), KeyboardButton("📚 Учёба"))
    kb.row(KeyboardButton("👤 Профиль"), KeyboardButton("ℹ️ Помощь"))
    return kb
