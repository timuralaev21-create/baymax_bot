from datetime import timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from states import (
    AddReminder,
    HealthSetup,
    UpdateWeight,
    AddSteps,
    AddDayPlan,
    AddGoal,
    RemoveGoal,
    DailyPulse,
    StudyExplain,
    StudyTimer,
    MentalChat,
    PhysicalHealth,
)
from keyboards.default import (
    main_menu_keyboard,
    reminders_keyboard,
    health_keyboard,
    day_keyboard,
    study_keyboard,
    support_keyboard,
    cancel_keyboard,
)
from utils.db import (
    get_user,
    update_health_profile,
    update_weight,
    add_water,
    reset_water,
    add_steps,
    award_daily_candy,
    create_reminder,
    get_user_reminders,
    add_day_plan,
    get_day_plans,
    clear_day_plan,
    add_goal,
    get_goals,
    remove_goal,
    save_daily_pulse,
)
from utils.helpers import (
    parse_reminder_time,
    format_profile,
    normalize_body_type,
    today_str,
    local_now,
    daily_pulse_answer,
    mental_support_answer,
    physical_health_answer,
    study_explain,
    generate_tasks,
    STATUS_SHOP,
)


async def _award(message: types.Message):
    ok = await award_daily_candy(message.from_user.id, today_str())
    if ok:
        await message.answer('🍭 За активность сегодня ты получил 1 леденец!')


@dp.message_handler(lambda message: message.text == '❌ Отмена', state='*')
async def cancel_any_state(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('❌ Действие отменено.', reply_markup=main_menu_keyboard())


@dp.message_handler(commands=['menu'], state='*')
@dp.message_handler(lambda message: message.text == '🔙 Назад', state='*')
async def go_back(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Главное меню:', reply_markup=main_menu_keyboard())


@dp.message_handler(commands=['health'], state='*')
@dp.message_handler(lambda message: message.text == '💧 Здоровье', state='*')
async def open_health(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('💧 Раздел здоровья:', reply_markup=health_keyboard())
    await _award(message)


@dp.message_handler(commands=['reminders'], state='*')
@dp.message_handler(lambda message: message.text == '⏰ Напоминания', state='*')
async def open_reminders(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('⏰ Выбери действие:', reply_markup=reminders_keyboard())
    await _award(message)


@dp.message_handler(commands=['day'], state='*')
@dp.message_handler(lambda message: message.text == '📝 День и цели', state='*')
async def open_day(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('📝 План на день очищается каждый новый день, а цели остаются пока ты их не удалишь.', reply_markup=day_keyboard())
    await _award(message)


@dp.message_handler(commands=['study'], state='*')
@dp.message_handler(lambda message: message.text == '📚 Учёба', state='*')
async def open_study(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('📚 Раздел учёбы:', reply_markup=study_keyboard())
    await _award(message)


@dp.message_handler(commands=['profile'], state='*')
@dp.message_handler(lambda message: message.text in ['👤 Профиль', '📊 Мой профиль'], state='*')
async def profile_show(message: types.Message, state: FSMContext):
    await state.finish()
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer('Сначала отправь /start')
        return
    await message.answer(format_profile(user), reply_markup=health_keyboard())
    await _award(message)


# ---------- Напоминания ----------
@dp.message_handler(commands=['myreminders'], state='*')
@dp.message_handler(lambda message: message.text == '📋 Мои напоминания', state='*')
async def show_reminders(message: types.Message, state: FSMContext):
    await state.finish()
    reminders = await get_user_reminders(message.from_user.id)
    if not reminders:
        await message.answer('У тебя пока нет активных напоминаний.', reply_markup=reminders_keyboard())
        return
    lines = ['<b>Твои активные напоминания:</b>\n']
    for idx, reminder in enumerate(reminders[:10], start=1):
        lines.append(f"{idx}. {reminder['text']} — <code>{reminder['remind_at']}</code>")
    await message.answer('\n'.join(lines), reply_markup=reminders_keyboard())


@dp.message_handler(commands=['addreminder'], state='*')
@dp.message_handler(lambda message: message.text == '➕ Добавить', state='*')
async def add_reminder_start(message: types.Message, state: FSMContext):
    await state.finish()
    await AddReminder.waiting_for_text.set()
    await message.answer('📝 Напиши текст напоминания. Например: сделать математику', reply_markup=cancel_keyboard())


@dp.message_handler(state=AddReminder.waiting_for_text)
async def get_reminder_text(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 2 or len(text) > 300:
        await message.answer('Текст должен быть от 2 до 300 символов.')
        return
    await state.update_data(reminder_text=text)
    await AddReminder.next()
    await message.answer('⏰ Теперь напиши время: <code>18:30</code>, <code>через 20 минут</code>, <code>через 2 часа</code>.', reply_markup=cancel_keyboard())


@dp.message_handler(state=AddReminder.waiting_for_time)
async def get_reminder_time(message: types.Message, state: FSMContext):
    parsed = parse_reminder_time(message.text)
    if not parsed:
        await message.answer('⚠️ Не понял время. Пример: 18:30, через 20 минут, через 2 часа')
        return
    data = await state.get_data()
    await create_reminder(message.from_user.id, data['reminder_text'], parsed.strftime('%Y-%m-%d %H:%M:%S'))
    await state.finish()
    await message.answer(f"✅ Напоминание сохранено\n\n⏰ {parsed.strftime('%d.%m %H:%M')}\n📝 {data['reminder_text']}", reply_markup=reminders_keyboard())


# ---------- Здоровье ----------
@dp.message_handler(commands=['norm'], state='*')
@dp.message_handler(lambda message: message.text == '🧮 Рассчитать норму', state='*')
async def health_setup_start(message: types.Message, state: FSMContext):
    await state.finish()
    await HealthSetup.waiting_for_weight.set()
    await message.answer('⚖️ Напиши вес в кг. Например: 89 или 89.5', reply_markup=cancel_keyboard())


@dp.message_handler(state=HealthSetup.waiting_for_weight)
async def health_setup_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.').strip())
    except ValueError:
        await message.answer('Введи вес числом. Например: 89.5')
        return
    if not 20 <= weight <= 300:
        await message.answer('Введи реальный вес от 20 до 300 кг.')
        return
    await state.update_data(weight=weight)
    await HealthSetup.next()
    await message.answer('📏 Теперь рост в см. Например: 175', reply_markup=cancel_keyboard())


@dp.message_handler(state=HealthSetup.waiting_for_height)
async def health_setup_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text.strip())
    except ValueError:
        await message.answer('Введи рост числом. Например: 175')
        return
    if not 100 <= height <= 230:
        await message.answer('Введи реальный рост от 100 до 230 см.')
        return
    await state.update_data(height=height)
    await HealthSetup.next()
    await message.answer('🏷 Какая форма? Напиши: худой, умеренный, есть лишний жир, спортивный.', reply_markup=cancel_keyboard())


@dp.message_handler(state=HealthSetup.waiting_for_body_type)
async def health_setup_body_type(message: types.Message, state: FSMContext):
    body_type = normalize_body_type(message.text)
    if not body_type:
        await message.answer('Не понял форму. Напиши: худой / умеренный / есть лишний жир / спортивный.')
        return
    data = await state.get_data()
    await update_health_profile(message.from_user.id, data['weight'], data['height'], body_type)
    await state.finish()
    user = await get_user(message.from_user.id)
    await message.answer('✅ Готово. Вот твоя норма:', reply_markup=health_keyboard())
    await message.answer(format_profile(user), reply_markup=health_keyboard())


@dp.message_handler(commands=['weight'], state='*')
@dp.message_handler(lambda message: message.text == '⚖️ Изменить вес', state='*')
async def change_weight_start(message: types.Message, state: FSMContext):
    await state.finish()
    await UpdateWeight.waiting_for_weight.set()
    await message.answer('Напиши новый вес в кг. Например: 87', reply_markup=cancel_keyboard())


@dp.message_handler(state=UpdateWeight.waiting_for_weight)
async def change_weight_finish(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.').strip())
    except ValueError:
        await message.answer('⚠️ Введи вес числом. Например: 87 или 87.5')
        return
    if weight < 20 or weight > 300:
        await message.answer('⚠️ Введи реальный вес в диапазоне 20–300 кг.')
        return
    await update_weight(message.from_user.id, weight)
    await state.finish()
    user = await get_user(message.from_user.id)
    await message.answer('✅ Вес обновлён.', reply_markup=health_keyboard())
    await message.answer(format_profile(user), reply_markup=health_keyboard())


@dp.message_handler(commands=['water'], state='*')
@dp.message_handler(lambda message: message.text == '💧 Выпил воду', state='*')
async def drink_water(message: types.Message, state: FSMContext):
    await state.finish()
    await add_water(message.from_user.id, 250)
    user = await get_user(message.from_user.id)
    await message.answer(f"💧 Записал +250 мл. Всего сегодня: {user['water_ml']} мл", reply_markup=health_keyboard())
    await _award(message)


@dp.message_handler(commands=['resetwater'], state='*')
@dp.message_handler(lambda message: message.text == '🔄 Сбросить воду', state='*')
async def water_reset(message: types.Message, state: FSMContext):
    await state.finish()
    await reset_water(message.from_user.id)
    await message.answer('💧 Счётчик воды сброшен.', reply_markup=health_keyboard())


@dp.message_handler(commands=['steps'], state='*')
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


@dp.message_handler(commands=['mental'], state='*')
@dp.message_handler(lambda message: message.text == '🧠 Ментальное', state='*')
async def mental_start(message: types.Message, state: FSMContext):
    await state.finish()
    await MentalChat.waiting_for_message.set()
    await message.answer('🧠 Напиши, что чувствуешь. Я отвечу спокойно и поддерживающе.', reply_markup=cancel_keyboard())


@dp.message_handler(state=MentalChat.waiting_for_message)
async def mental_finish(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(mental_support_answer(message.text), reply_markup=health_keyboard())


@dp.message_handler(commands=['physical'], state='*')
@dp.message_handler(lambda message: message.text == '🩺 Физическое', state='*')
async def physical_start(message: types.Message, state: FSMContext):
    await state.finish()
    await PhysicalHealth.waiting_for_symptoms.set()
    await message.answer('🩺 Опиши симптомы: что болит, температура есть или нет, сколько длится.', reply_markup=cancel_keyboard())


@dp.message_handler(state=PhysicalHealth.waiting_for_symptoms)
async def physical_finish(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(physical_health_answer(message.text), reply_markup=health_keyboard())


@dp.message_handler(content_types=types.ContentType.LOCATION, state='*')
async def nearest_pharmacies(message: types.Message, state: FSMContext):
    await state.finish()
    lat = message.location.latitude
    lon = message.location.longitude
    text = (
        '📍 Я не имею встроенного доступа к базе аптек, но вот быстрые ссылки по твоей геопозиции:\n\n'
        f'1. Google Maps: https://www.google.com/maps/search/pharmacy/@{lat},{lon},15z\n'
        f'2. 2GIS: https://2gis.uz/search/аптека/geo/{lon},{lat}\n'
        f'3. Яндекс Карты: https://yandex.com/maps/?text=аптека&ll={lon},{lat}&z=15\n\n'
        'Открой любую ссылку — там будут ближайшие аптеки рядом.'
    )
    await message.answer(text, reply_markup=health_keyboard(), disable_web_page_preview=True)


# ---------- День и цели ----------
@dp.message_handler(commands=['plan'], state='*')
@dp.message_handler(lambda message: message.text == '📅 План на сегодня', state='*')
async def show_day_plan(message: types.Message, state: FSMContext):
    await state.finish()
    plans = await get_day_plans(message.from_user.id, today_str())
    if not plans:
        await message.answer('📅 План на сегодня пуст. Добавь пункт кнопкой “➕ Добавить план”.', reply_markup=day_keyboard())
        return
    lines = ['📅 <b>План на сегодня:</b>']
    for i, row in enumerate(plans, 1):
        lines.append(f'{i}. {row["text"]}')
    await message.answer('\n'.join(lines), reply_markup=day_keyboard())


@dp.message_handler(lambda message: message.text == '➕ Добавить план', state='*')
async def add_plan_start(message: types.Message, state: FSMContext):
    await state.finish()
    await AddDayPlan.waiting_for_text.set()
    await message.answer('Напиши пункт плана на сегодня.', reply_markup=cancel_keyboard())


@dp.message_handler(state=AddDayPlan.waiting_for_text)
async def add_plan_finish(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not 2 <= len(text) <= 200:
        await message.answer('Пункт должен быть от 2 до 200 символов.')
        return
    await add_day_plan(message.from_user.id, text, today_str())
    await state.finish()
    await message.answer('✅ Добавил в план на сегодня.', reply_markup=day_keyboard())


@dp.message_handler(lambda message: message.text == '🗑 Очистить план', state='*')
async def clear_plan(message: types.Message, state: FSMContext):
    await state.finish()
    await clear_day_plan(message.from_user.id)
    await message.answer('🗑 План на сегодня очищен.', reply_markup=day_keyboard())


@dp.message_handler(commands=['goals'], state='*')
@dp.message_handler(lambda message: message.text == '🎯 Цели', state='*')
async def show_goals(message: types.Message, state: FSMContext):
    await state.finish()
    goals = await get_goals(message.from_user.id)
    if not goals:
        await message.answer('🎯 Целей пока нет. Добавь первую цель.', reply_markup=day_keyboard())
        return
    lines = ['🎯 <b>Твои цели:</b>']
    for row in goals:
        lines.append(f'{row["id"]}. {row["text"]}')
    await message.answer('\n'.join(lines), reply_markup=day_keyboard())


@dp.message_handler(lambda message: message.text == '➕ Добавить цель', state='*')
async def add_goal_start(message: types.Message, state: FSMContext):
    await state.finish()
    await AddGoal.waiting_for_text.set()
    await message.answer('Напиши цель. Она будет храниться, пока ты её не удалишь.', reply_markup=cancel_keyboard())


@dp.message_handler(state=AddGoal.waiting_for_text)
async def add_goal_finish(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not 2 <= len(text) <= 200:
        await message.answer('Цель должна быть от 2 до 200 символов.')
        return
    await add_goal(message.from_user.id, text)
    await state.finish()
    await message.answer('✅ Цель добавлена.', reply_markup=day_keyboard())


@dp.message_handler(lambda message: message.text == '➖ Убрать цель', state='*')
async def remove_goal_start(message: types.Message, state: FSMContext):
    await state.finish()
    goals = await get_goals(message.from_user.id)
    if not goals:
        await message.answer('У тебя пока нет целей.', reply_markup=day_keyboard())
        return
    lines = ['Напиши номер цели, которую удалить:']
    for row in goals:
        lines.append(f'{row["id"]}. {row["text"]}')
    await RemoveGoal.waiting_for_id.set()
    await message.answer('\n'.join(lines), reply_markup=cancel_keyboard())


@dp.message_handler(state=RemoveGoal.waiting_for_id)
async def remove_goal_finish(message: types.Message, state: FSMContext):
    try:
        goal_id = int(message.text.strip())
    except ValueError:
        await message.answer('Введи номер цели числом.')
        return
    ok = await remove_goal(message.from_user.id, goal_id)
    await state.finish()
    await message.answer('✅ Цель удалена.' if ok else 'Не нашёл цель с таким номером.', reply_markup=day_keyboard())


@dp.message_handler(commands=['pulse'], state='*')
@dp.message_handler(lambda message: message.text == '💓 Пульс дня', state='*')
async def pulse_start(message: types.Message, state: FSMContext):
    await state.finish()
    await DailyPulse.waiting_for_energy.set()
    await message.answer('💓 Оцени энергию от 1 до 10.', reply_markup=cancel_keyboard())


async def _get_score(message: types.Message):
    try:
        value = int(message.text.strip())
    except ValueError:
        return None
    return value if 1 <= value <= 10 else None


@dp.message_handler(state=DailyPulse.waiting_for_energy)
async def pulse_energy(message: types.Message, state: FSMContext):
    value = await _get_score(message)
    if value is None:
        await message.answer('Введи число от 1 до 10.')
        return
    await state.update_data(energy=value)
    await DailyPulse.next()
    await message.answer('🙂 Настроение от 1 до 10?', reply_markup=cancel_keyboard())


@dp.message_handler(state=DailyPulse.waiting_for_mood)
async def pulse_mood(message: types.Message, state: FSMContext):
    value = await _get_score(message)
    if value is None:
        await message.answer('Введи число от 1 до 10.')
        return
    await state.update_data(mood=value)
    await DailyPulse.next()
    await message.answer('😴 Сон от 1 до 10?', reply_markup=cancel_keyboard())


@dp.message_handler(state=DailyPulse.waiting_for_sleep)
async def pulse_sleep(message: types.Message, state: FSMContext):
    value = await _get_score(message)
    if value is None:
        await message.answer('Введи число от 1 до 10.')
        return
    data = await state.get_data()
    await save_daily_pulse(message.from_user.id, today_str(), data['energy'], data['mood'], value)
    await state.finish()
    await message.answer(daily_pulse_answer(data['energy'], data['mood'], value), reply_markup=day_keyboard())


# ---------- Учёба ----------
@dp.message_handler(commands=['explain'], state='*')
@dp.message_handler(lambda message: message.text == '📖 Объяснить тему', state='*')
async def explain_start(message: types.Message, state: FSMContext):
    await state.finish()
    await StudyExplain.waiting_for_topic.set()
    await message.answer('📖 Напиши тему. Например: линейные уравнения, многочлены, графики функций.', reply_markup=cancel_keyboard())


@dp.message_handler(state=StudyExplain.waiting_for_topic)
async def explain_finish(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(study_explain(message.text.strip()), reply_markup=study_keyboard())


@dp.message_handler(commands=['timer'], state='*')
@dp.message_handler(lambda message: message.text == '⏱ Решить на время', state='*')
async def timer_start(message: types.Message, state: FSMContext):
    await state.finish()
    await StudyTimer.waiting_for_topic.set()
    await message.answer('⏱ Напиши тему для задач.', reply_markup=cancel_keyboard())


@dp.message_handler(state=StudyTimer.waiting_for_topic)
async def timer_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 2:
        await message.answer('Напиши тему подробнее.')
        return
    await state.update_data(topic=topic)
    await StudyTimer.next()
    await message.answer('На сколько минут поставить таймер? Например: 10', reply_markup=cancel_keyboard())


@dp.message_handler(state=StudyTimer.waiting_for_minutes)
async def timer_minutes(message: types.Message, state: FSMContext):
    try:
        minutes = int(message.text.strip())
    except ValueError:
        await message.answer('Введи минуты числом.')
        return
    if not 1 <= minutes <= 180:
        await message.answer('Поставь от 1 до 180 минут.')
        return
    data = await state.get_data()
    tasks = generate_tasks(data['topic'])
    finish_at = local_now() + timedelta(minutes=minutes)
    await create_reminder(message.from_user.id, f'Время вышло по теме: {data["topic"]}', finish_at.strftime('%Y-%m-%d %H:%M:%S'))
    await state.finish()
    await message.answer(
        f"⏱ Таймер на {minutes} мин запущен.\n\n<b>Задачи:</b>\n" + '\n'.join(f'{i}. {task}' for i, task in enumerate(tasks, 1)),
        reply_markup=study_keyboard()
    )


# ---------- Статусы ----------
@dp.message_handler(commands=['shop'], state='*')
async def status_shop(message: types.Message, state: FSMContext):
    await state.finish()
    user = await get_user(message.from_user.id)
    candies = user['candies'] or 0
    lines = [f'🍭 У тебя леденцов: {candies}\n', '<b>Магазин статусов:</b>']
    for price, name in STATUS_SHOP.items():
        mark = '✅ доступно' if candies >= price else f'нужно {price}'
        lines.append(f'• {name} — {price} 🍭 ({mark})')
    await message.answer('\n'.join(lines), reply_markup=main_menu_keyboard())
