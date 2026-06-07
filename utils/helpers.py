import re
from datetime import datetime, timedelta

BODY_TYPES = {
    'slim': 'Худой / сухой',
    'moderate': 'Умеренный',
    'overweight': 'Есть лишний жир',
    'sport': 'Спортивный',
}

STATUS_SHOP = {
    3: 'Новичок здоровья 🩺',
    7: 'Водный герой 💧',
    14: 'Железная дисциплина ⚙️',
    30: 'Baymax Prime 🤖',
}


def local_now():
    # Telegram Bot API не отдаёт IP пользователя, поэтому используем локальное время сервера/проекта.
    return datetime.now()


def today_str():
    return local_now().strftime('%Y-%m-%d')


def parse_reminder_time(text: str):
    text = text.strip().lower().replace('ё', 'е')
    now = local_now()

    hhmm_match = re.fullmatch(r'(?:в\s*)?(\d{1,2}):(\d{2})', text)
    if hhmm_match:
        hour = int(hhmm_match.group(1))
        minute = int(hhmm_match.group(2))
        if hour > 23 or minute > 59:
            return None
        remind_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_at <= now:
            remind_at += timedelta(days=1)
        return remind_at

    in_minutes = re.fullmatch(r'через\s+(\d+)\s*(мин|минута|минуты|минут|m|min)?', text)
    if in_minutes:
        minutes = int(in_minutes.group(1))
        if minutes <= 0 or minutes > 60 * 24 * 30:
            return None
        return now + timedelta(minutes=minutes)

    in_hours = re.fullmatch(r'через\s+(\d+)\s*(час|часа|часов|ч|h)?', text)
    if in_hours:
        hours = int(in_hours.group(1))
        if hours <= 0 or hours > 24 * 30:
            return None
        return now + timedelta(hours=hours)

    in_days = re.fullmatch(r'через\s+(\d+)\s*(день|дня|дней|д)?', text)
    if in_days:
        days = int(in_days.group(1))
        if days <= 0 or days > 365:
            return None
        return now + timedelta(days=days)

    return None


def normalize_body_type(text: str):
    t = text.lower().strip()
    if any(word in t for word in ['спорт', 'кач', 'атлет']):
        return 'sport'
    if any(word in t for word in ['худ', 'сух', 'skinny']):
        return 'slim'
    if any(word in t for word in ['жир', 'лишн', 'толст', 'fat']):
        return 'overweight'
    if any(word in t for word in ['умер', 'норм', 'сред']):
        return 'moderate'
    return None


def health_numbers(weight: float, height: int, body_type: str = 'moderate'):
    bmi = round(weight / ((height / 100) ** 2), 1)

    if bmi < 18.5:
        bmi_text = 'недостаточный вес'
        goal = 'аккуратно набрать качественную массу и не урезать еду'
        kcal = round(weight * 33)
        protein = round(weight * 1.6)
    elif bmi < 25:
        bmi_text = 'норма'
        goal = 'держать форму и постепенно улучшать выносливость'
        kcal = round(weight * 30)
        protein = round(weight * 1.6)
    elif bmi < 30:
        bmi_text = 'избыточный вес'
        goal = 'мягкий дефицит без жёстких диет'
        kcal = round(weight * 26)
        protein = round(weight * 1.7)
    else:
        bmi_text = 'ожирение по BMI'
        goal = 'безопасное снижение веса, лучше с врачом/родителями'
        kcal = round(weight * 24)
        protein = round(weight * 1.7)

    if body_type == 'sport':
        kcal += 150
        protein = round(weight * 1.8)
    elif body_type == 'overweight':
        kcal -= 150
    elif body_type == 'slim':
        kcal += 150

    fat = round(weight * 0.8)
    carbs = max(80, round((kcal - protein * 4 - fat * 9) / 4))
    water_liters = round(weight * 0.033, 1)

    return {
        'bmi': bmi,
        'bmi_text': bmi_text,
        'goal': goal,
        'kcal': max(kcal, 1400),
        'protein': protein,
        'fat': fat,
        'carbs': carbs,
        'water_liters': water_liters,
    }


def format_profile(user):
    height = int(user['height'] or 175)
    weight = float(user['weight'] or 89)
    body_type = user['body_type'] or 'moderate'
    nums = health_numbers(weight, height, body_type)
    body_label = BODY_TYPES.get(body_type, BODY_TYPES['moderate'])

    return (
        f"👤 <b>{user['full_name']}</b>\n\n"
        f"📏 Рост: {height} см\n"
        f"⚖️ Вес: {weight:.1f} кг\n"
        f"🏷 Форма: {body_label}\n"
        f"🍭 Леденцы: {user['candies'] or 0}\n"
        f"💧 Выпито воды сегодня: {user['water_ml'] or 0} мл\n"
        f"🚶 Шаги сегодня: {user['steps'] or 0}\n\n"
        f"📊 <b>Анализ:</b> BMI {nums['bmi']} — {nums['bmi_text']}\n"
        f"🎯 Цель: {nums['goal']}\n\n"
        f"🔥 <b>Ориентир КБЖУ:</b>\n"
        f"• Калории: ~{nums['kcal']} ккал/день\n"
        f"• Белки: ~{nums['protein']} г\n"
        f"• Жиры: ~{nums['fat']} г\n"
        f"• Углеводы: ~{nums['carbs']} г\n\n"
        f"💧 Вода: ~{nums['water_liters']} л/день\n"
        f"🚶 Шаги: 8 000–12 000 в день, без перегруза."
    )


def daily_pulse_answer(energy: int, mood: int, sleep: int):
    avg = (energy + mood + sleep) / 3
    if avg >= 7:
        return 'День выглядит сильным 💙 Сделай главный сложный пункт первым, пока энергии много.'
    if avg >= 4:
        return 'Средний ресурс. Не перегружай день: 1 главное дело, вода, нормальная еда и короткие перерывы.'
    return 'Ресурс низкий. Сегодня лучше режим восстановления: сон, спокойная прогулка, минимум перегруза и разговор с близким взрослым, если тяжело.'


def mental_support_answer(text: str):
    t = text.lower()
    if any(word in t for word in ['паник', 'тревог', 'страшно']):
        return (
            'Я рядом 💙 Попробуй сейчас: поставь ноги на пол, назови 5 предметов вокруг, сделай 5 медленных выдохов. '
            'Потом напиши одним предложением: что именно пугает? Если становится совсем плохо — обратись к взрослому рядом.'
        )
    if any(word in t for word in ['груст', 'одинок', 'плохо']):
        return (
            'Понимаю, это неприятно 💙 Сейчас не надо решать всю жизнь сразу. Сделай маленький шаг: вода, душ/умыться, 10 минут без телефона, '
            'и напиши человеку, которому доверяешь.'
        )
    return (
        'Я тебя понял 💙 Попробуй описать проблему в формате: “что случилось — что я чувствую — какой маленький шаг могу сделать”. '
        'Я помогу разложить это спокойно.'
    )


def physical_health_answer(symptoms: str):
    t = symptoms.lower()
    red_flags = ['не могу дышать', 'сильная боль', 'потерял сознание', 'кровь', 'судороги', 'очень высокая температура']
    if any(flag in t for flag in red_flags):
        return (
            '🆘 Это может быть срочно. Сразу скажи родителям/взрослому рядом и обратись за медицинской помощью. '
            'Я не могу заменить врача.'
        )

    tips = ['Отдыхай, пей воду маленькими глотками, не тренируйся через плохое самочувствие.']
    if any(w in t for w in ['насморк', 'чих', 'горло', 'кашель', 'простуд']):
        tips.append('При простуде обычно помогают сон, тёплое питьё и промывание носа физраствором.')
    if any(w in t for w in ['температура', 'жар']):
        tips.append('Измеряй температуру и скажи взрослому. Жаропонижающие и дозировки — только по инструкции и с родителями/врачом.')
    if any(w in t for w in ['живот', 'тошн', 'рвот']):
        tips.append('При боли в животе не экспериментируй с лекарствами. Если боль сильная/растёт — нужен врач.')

    return '🩺 Я не врач, но могу подсказать безопасные первые шаги:\n\n' + '\n'.join(f'• {tip}' for tip in tips)


def study_explain(topic: str):
    return (
        f"📖 <b>Тема:</b> {topic}\n\n"
        "Объяснение по схеме Baymax:\n"
        "1. Выпиши главное правило/формулу.\n"
        "2. Разбери самый простой пример.\n"
        "3. Потом решай пример на 1 шаг сложнее.\n"
        "4. В конце проверь ответ обратной подстановкой или логикой.\n\n"
        "Напиши конкретную задачу — я разберу её по шагам."
    )


def generate_tasks(topic: str):
    topic_low = topic.lower()
    if 'урав' in topic_low:
        return ['3x - 7 = 14', '5(2x - 1) = 35', '4x + 3 = 2x + 17']
    if 'многоч' in topic_low or 'разлож' in topic_low:
        return ['x² - 9', 'a² + 6a + 9', '3x² - 12x']
    if 'функц' in topic_low or 'граф' in topic_low:
        return ['Построй y = 2x - 3', 'Найди y при x = -2 для y = -x + 5', 'Определи угловой коэффициент y = 4x + 1']
    return [f'Задача 1 по теме: {topic}', f'Задача 2 по теме: {topic}', f'Задача 3 по теме: {topic}']
