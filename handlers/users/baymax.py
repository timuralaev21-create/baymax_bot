from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from states import AddReminder, UpdateWeight, AddSteps, StudyAssistant
from keyboards.default import (
    main_menu_keyboard,
    reminders_keyboard,
    health_keyboard,
    study_keyboard,
    support_keyboard,
    cancel_keyboard,
)
from utils.db import (
    get_user,
    update_weight,
    add_water,
    reset_water,
    add_steps,
    create_reminder,
    get_user_reminders,
)
from utils.helpers import parse_reminder_time, format_profile


# Универсальная отмена
@dp.message_handler(lambda message: message.text == '❌ Отмена', state='*')
async def cancel_any_state(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('❌ Действие отменено.', reply_markup=main_menu_keyboard())


# Главное меню -> разделы
@dp.message_handler(lambda message: message.text == '⏰ Напоминания', state='*')
async def open_reminders(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Выбери действие в разделе напоминаний:', reply_markup=reminders_keyboard())


@dp.message_handler(lambda message: message.text == '💧 Здоровье', state='*')
async def open_health(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Раздел здоровья открыт:', reply_markup=health_keyboard())


@dp.message_handler(lambda message: message.text == '📚 Учёба', state='*')
async def open_study(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Раздел учёбы открыт:', reply_markup=study_keyboard())


@dp.message_handler(lambda message: message.text == '🤝 Поддержка', state='*')
async def open_support(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Я рядом. Выбери своё состояние:', reply_markup=support_keyboard())


@dp.message_handler(lambda message: message.text == '🔙 Назад', state='*')
async def go_back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Главное меню:', reply_markup=main_menu_keyboard())


# Напоминания
@dp.message_handler(lambda message: message.text == '📋 Мои напоминания', state='*')
async def show_reminders(message: types.Message, state: FSMContext):
    await state.finish()
    reminders = await get_user_reminders(message.from_user.id)
    if not reminders:
        await message.answer('У тебя пока нет активных напоминаний.', reply_markup=reminders_keyboard())
        return

    lines = ['<b>Твои активные напоминания:</b>\n']
    for idx, reminder in enumerate(reminders[:10], start=1):
        remind_at = datetime.strptime(reminder['remind_at'], '%Y-%m-%d %H:%M:%S')
        lines.append(f"{idx}. {reminder['text']} — <code>{remind_at.strftime('%d.%m %H:%M')}</code>")
    await message.answer('\n'.join(lines), reply_markup=reminders_keyboard())


@dp.message_handler(lambda message: message.text == '➕ Добавить', state='*')
async def add_reminder_start(message: types.Message, state: FSMContext):
    await state.finish()
    await AddReminder.waiting_for_text.set()
    await message.answer('📝 Напиши текст напоминания.', reply_markup=cancel_keyboard())


@dp.message_handler(state=AddReminder.waiting_for_text)
async def get_reminder_text(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 2:
        await message.answer('Текст слишком короткий. Напиши напоминание подробнее.')
        return
    await state.update_data(reminder_text=text)
    await AddReminder.next()
    await message.answer('⏰ Теперь напиши время. Например: 18:30 или через 20 минут', reply_markup=cancel_keyboard())


@dp.message_handler(state=AddReminder.waiting_for_time)
async def get_reminder_time(message: types.Message, state: FSMContext):
    parsed = parse_reminder_time(message.text)
    if not parsed:
        await message.answer('⚠️ Не понял время. Напиши, например: 18:30 или через 20 минут')
        return

    data = await state.get_data()
    await create_reminder(
        user_id=message.from_user.id,
        text=data['reminder_text'],
        remind_at=parsed.strftime('%Y-%m-%d %H:%M:%S')
    )
    await state.finish()
    await message.answer(
        f"✅ Напоминание сохранено\n\n⏰ {parsed.strftime('%H:%M')}\n📝 {data['reminder_text']}",
        reply_markup=reminders_keyboard()
    )


# Здоровье
@dp.message_handler(lambda message: message.text == '📊 Мой профиль', state='*')
async def profile_show(message: types.Message, state: FSMContext):
    await state.finish()
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer('Сначала отправь /start')
        return
    await message.answer(format_profile(user), reply_markup=health_keyboard())


@dp.message_handler(lambda message: message.text == '⚖️ Изменить вес', state='*')
async def change_weight_start(message: types.Message, state: FSMContext):
    await state.finish()
    await UpdateWeight.waiting_for_weight.set()
    await message.answer('Напиши новый вес в кг. Например: 87', reply_markup=cancel_keyboard())


@dp.message_handler(state=UpdateWeight.waiting_for_weight)
async def change_weight_finish(message: types.Message, state: FSMContext):
    raw = message.text.replace(',', '.').strip()
    try:
        weight = float(raw)
    except ValueError:
        await message.answer('⚠️ Введи вес числом. Например: 87 или 87.5')
        return
    if weight < 20 or weight > 300:
        await message.answer('⚠️ Введи реальный вес в диапазоне 20–300 кг.')
        return
    await update_weight(message.from_user.id, weight)
    await state.finish()
    user = await get_user(message.from_user.id)
    await message.answer('✅ Вес обновлён. Вот твой новый профиль:', reply_markup=health_keyboard())
    await message.answer(format_profile(user), reply_markup=health_keyboard())


@dp.message_handler(lambda message: message.text == '💧 Выпил воду', state='*')
async def drink_water(message: types.Message, state: FSMContext):
    await state.finish()
    await add_water(message.from_user.id, 250)
    user = await get_user(message.from_user.id)
    await message.answer(f"💧 Записал +250 мл. Всего за сегодня: {user['water_ml']} мл", reply_markup=health_keyboard())


@dp.message_handler(lambda message: message.text == '🔄 Сбросить воду', state='*')
async def water_reset(message: types.Message, state: FSMContext):
    await state.finish()
    await reset_water(message.from_user.id)
    await message.answer('💧 Счётчик воды сброшен.', reply_markup=health_keyboard())


@dp.message_handler(lambda message: message.text == '🚶 Добавить шаги', state='*')
async def add_steps_start(message: types.Message, state: FSMContext):
    await state.finish()
    await AddSteps.waiting_for_steps.set()
    await message.answer('Напиши, сколько шагов добавить. Например: 1500', reply_markup=cancel_keyboard())


@dp.message_handler(state=AddSteps.waiting_for_steps)
async def add_steps_finish(message: types.Message, state: FSMContext):
    try:
        steps = int(message.text.strip())
    except ValueError:
        await message.answer('⚠️ Введи шаги числом. Например: 1500')
        return
    if steps <= 0 or steps > 100000:
        await message.answer('⚠️ Введи число шагов от 1 до 100000.')
        return
    await add_steps(message.from_user.id, steps)
    await state.finish()
    user = await get_user(message.from_user.id)
    await message.answer(f"🚶 Добавил {steps} шагов. Теперь всего: {user['steps']}", reply_markup=health_keyboard())


# Учёба
@dp.message_handler(lambda message: message.text == '❓ Задать вопрос', state='*')
async def study_question_start(message: types.Message, state: FSMContext):
    await state.finish()
    await StudyAssistant.waiting_for_question.set()
    await message.answer(
        'Напиши вопрос по учёбе.\n\n'
        'Сейчас в шаблоне стоит простая заготовка ответа. Позже сюда можно подключить OpenAI.',
        reply_markup=cancel_keyboard(),
    )


@dp.message_handler(state=StudyAssistant.waiting_for_question)
async def study_question_finish(message: types.Message, state: FSMContext):
    question = message.text.strip()
    await state.finish()
    answer = (
        f"📚 <b>Твой вопрос:</b> {question}\n\n"
        "<b>Baymax советует:</b>\n"
        "1. Разбей задачу на маленькие части.\n"
        "2. Выпиши главное правило или формулу.\n"
        "3. Реши 1 простой пример.\n"
        "4. Потом переходи к сложному.\n\n"
        "Если хочешь, я могу дальше переделать этот раздел и подключить сюда ИИ-ответы через OpenAI API."
    )
    await message.answer(answer, reply_markup=study_keyboard())


@dp.message_handler(lambda message: message.text == '📝 План на день', state='*')
async def study_plan(message: types.Message, state: FSMContext):
    await state.finish()
    text = (
        "📝 <b>Пример плана на день</b>\n\n"
        "1. 45 минут — учёба\n"
        "2. 10 минут — перерыв\n"
        "3. 45 минут — домашка\n"
        "4. 20 минут — повторение\n"
        "5. 30 минут — отдых\n\n"
        "Совет: сначала сделай самый трудный предмет."
    )
    await message.answer(text, reply_markup=study_keyboard())


# Поддержка
@dp.message_handler(lambda message: message.text == '😊 Нормально', state='*')
async def mood_ok(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Отлично 💙 Продолжай в своём темпе. Не забывай про воду, отдых и сон.', reply_markup=support_keyboard())


@dp.message_handler(lambda message: message.text == '😔 Грустно', state='*')
async def mood_sad(message: types.Message, state: FSMContext):
    await state.finish()
    text = (
        'Мне жаль, что тебе грустно 💙\n\n'
        'Попробуй:\n'
        '• немного пройтись\n'
        '• выпить воды\n'
        '• написать близкому человеку\n'
        '• сделать 3 медленных вдоха и выдоха\n\n'
        'Если хочешь, напиши кому из близких ты можешь сейчас написать.'
    )
    await message.answer(text, reply_markup=support_keyboard())


@dp.message_handler(lambda message: message.text == '😣 Тревожно', state='*')
async def mood_anxious(message: types.Message, state: FSMContext):
    await state.finish()
    text = (
        'Давай немного успокоимся 💙\n\n'
        'Сделай упражнение 4–4–4:\n'
        '1. Вдох 4 секунды\n'
        '2. Задержка 4 секунды\n'
        '3. Выдох 4 секунды\n'
        'Повтори 4 раза.\n\n'
        'Если тревога не проходит, обязательно обратись к взрослому, которому доверяешь.'
    )
    await message.answer(text, reply_markup=support_keyboard())


@dp.message_handler(lambda message: message.text == '🆘 Нужна помощь', state='*')
async def urgent_help(message: types.Message, state: FSMContext):
    await state.finish()
    text = (
        'Если тебе <b>небезопасно</b> или очень тяжело, пожалуйста, сразу обратись к:\n'
        '• родителю\n'
        '• родственнику\n'
        '• школьному психологу\n'
        '• учителю\n\n'
        'Если есть риск для жизни или здоровья — звони в экстренные службы своей страны <b>прямо сейчас</b>.'
    )
    await message.answer(text, reply_markup=support_keyboard())
