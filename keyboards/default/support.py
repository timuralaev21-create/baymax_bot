from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def support_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("😊 Нормально"), KeyboardButton("😔 Грустно"))
    kb.row(KeyboardButton("😣 Тревожно"), KeyboardButton("🆘 Нужна помощь"))
    kb.row(KeyboardButton("🔙 Назад"))
    return kb
