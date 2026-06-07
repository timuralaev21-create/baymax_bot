from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from loader import dp
from utils.db import get_all_users


def _is_admin(user_id: int) -> bool:
    return str(user_id) in [str(admin) for admin in ADMINS]


@dp.message_handler(commands=['admin'], state='*')
async def admin_panel(message: types.Message, state: FSMContext):
    await state.finish()
    if not _is_admin(message.from_user.id):
        return
    users = await get_all_users()
    text = (
        '<b>Админ-панель Baymax</b>\n\n'
        f'👥 Пользователей: {len(users)}\n\n'
        '<b>Команды:</b>\n'
        '/admin — статистика\n'
        '/broadcast текст — рассылка всем пользователям\n\n'
        'Пример: <code>/broadcast Привет! Сегодня не забудь выпить воду 💧</code>'
    )
    await message.answer(text)


@dp.message_handler(commands=['broadcast'], state='*')
async def admin_broadcast(message: types.Message, state: FSMContext):
    await state.finish()
    if not _is_admin(message.from_user.id):
        return
    text = message.get_args().strip()
    if not text:
        await message.answer('Напиши текст после команды: <code>/broadcast текст</code>')
        return
    users = await get_all_users()
    sent = 0
    failed = 0
    for user in users:
        try:
            await dp.bot.send_message(user['user_id'], text)
            sent += 1
        except Exception:
            failed += 1
    await message.answer(f'✅ Рассылка завершена. Отправлено: {sent}, ошибок: {failed}')
