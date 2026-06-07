from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp
from keyboards.default import main_menu_keyboard


HELP_TEXT = (
    "<b>Baymax Bot — помощь</b>\n\n"
    "<b>Главные команды:</b>\n"
    "/start — запуск\n"
    "/menu — главное меню\n"
    "/help — помощь\n"
    "/profile — профиль, КБЖУ, вода, леденцы\n\n"
    "<b>💧 Здоровье</b>\n"
    "/health — открыть раздел\n"
    "/norm — вес, рост, форма тела → КБЖУ, вода, BMI\n"
    "/water — добавить 250 мл воды\n"
    "/resetwater — сбросить воду\n"
    "/steps — добавить шаги\n"
    "/mental — ментальная поддержка\n"
    "/physical — безопасные советы по симптомам\n"
    "📍 Ближайшие аптеки — отправь геопозицию, бот даст ссылки на карты.\n\n"
    "<b>⏰ Напоминания</b>\n"
    "/reminders — открыть раздел\n"
    "/addreminder — добавить\n"
    "/myreminders — список\n"
    "Время: <code>18:30</code>, <code>через 20 минут</code>, <code>через 2 часа</code>.\n"
    "Важно: Telegram не отдаёт IP пользователя, поэтому автоопределение времени по IP невозможно.\n\n"
    "<b>📝 День и цели</b>\n"
    "/day — открыть раздел\n"
    "/plan — план на сегодня; он очищается каждый новый день\n"
    "/goals — цели; они хранятся постоянно, пока ты их не удалишь\n"
    "/pulse — пульс дня: энергия, настроение, сон\n\n"
    "<b>📚 Учёба</b>\n"
    "/study — открыть раздел\n"
    "/explain — объяснить тему\n"
    "/timer — задачи на тему + таймер\n\n"
    "<b>🍭 Леденцы</b>\n"
    "За активность 1 раз в день бот выдаёт леденец. /shop — магазин статусов."
)


@dp.message_handler(CommandHelp(), state='*')
@dp.message_handler(lambda message: message.text == 'ℹ️ Помощь', state='*')
async def bot_help(message: types.Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard(), disable_web_page_preview=True)
