from aiogram import types

from loader import dp
from keyboards.default import main_menu_keyboard


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(
        'Я не совсем понял запрос 😅\n\nВыбери один из разделов меню или нажми /help.',
        reply_markup=main_menu_keyboard()
    )
