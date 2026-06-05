from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp
from keyboards.default import main_menu_keyboard


HELP_TEXT = (
    "<b>Baymax Bot — команды и разделы</b>\n\n"
    "/start — перезапустить бота\n"
    "/help — помощь\n\n"
    "<b>Разделы:</b>\n"
    "⏰ Напоминания — добавить и посмотреть напоминания\n"
    "💧 Здоровье — профиль, вода, шаги, вес\n"
    "📚 Учёба — вопрос по учёбе и план на день\n"
    "🤝 Поддержка — дружеская поддержка и советы\n\n"
    "Для времени напоминания можно писать, например: <code>18:30</code> или <code>через 20 минут</code>."
)


@dp.message_handler(CommandHelp(), state='*')
@dp.message_handler(lambda message: message.text == 'ℹ️ Помощь', state='*')
async def bot_help(message: types.Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())
