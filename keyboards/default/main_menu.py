from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("⏰ Напоминания"), KeyboardButton("💧 Здоровье"))
    kb.row(KeyboardButton("📚 Учёба"), KeyboardButton("🤝 Поддержка"))
    kb.row(KeyboardButton("ℹ️ Помощь"))
    return kb
