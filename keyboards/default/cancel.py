from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def cancel_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("❌ Отмена"))
    return kb
