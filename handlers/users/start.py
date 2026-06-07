from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from keyboards.default import main_menu_keyboard
from utils.db import create_or_update_user


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    await create_or_update_user(message.from_user.id, message.from_user.full_name)
    text = (
        f"Привет, <b>{message.from_user.full_name}</b>! Я Baymax 🤖\n\n"
        "Я помогу с нормой КБЖУ и воды, счётчиком воды, напоминаниями, планом дня, целями, учёбой, пульсом дня и поддержкой.\n\n"
        "Начни с <b>💧 Здоровье → 🧮 Рассчитать норму</b>."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())
