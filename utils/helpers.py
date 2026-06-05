import re
from datetime import datetime, timedelta


def parse_reminder_time(text: str):
    text = text.strip().lower()
    now = datetime.now()

    hhmm_match = re.fullmatch(r'(\d{1,2}):(\d{2})', text)
    if hhmm_match:
        hour = int(hhmm_match.group(1))
        minute = int(hhmm_match.group(2))
        if hour > 23 or minute > 59:
            return None
        remind_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_at <= now:
            remind_at += timedelta(days=1)
        return remind_at

    in_minutes = re.fullmatch(r'через\s+(\d+)\s+мин(?:ут|уты|у)?', text)
    if in_minutes:
        minutes = int(in_minutes.group(1))
        if minutes <= 0:
            return None
        return now + timedelta(minutes=minutes)

    in_hours = re.fullmatch(r'через\s+(\d+)\s+час(?:а|ов)?', text)
    if in_hours:
        hours = int(in_hours.group(1))
        if hours <= 0:
            return None
        return now + timedelta(hours=hours)

    return None


def format_profile(user):
    height = user['height'] or 175
    weight = float(user['weight'] or 89)
    bmi = round(weight / ((height / 100) ** 2), 1)

    if bmi < 18.5:
        analysis = 'Недостаточный вес'
    elif bmi < 25:
        analysis = 'Норма'
    elif bmi < 30:
        analysis = 'Избыточный вес'
    else:
        analysis = 'Ожирение'

    calories = round(weight * 27)
    water_liters = round(weight * 0.033, 1)

    text = (
        f"👤 <b>{user['full_name']}</b>\n\n"
        f"📏 Рост: {height} см\n"
        f"⚖️ Вес: {weight:.0f} кг\n"
        f"💧 Выпито воды: {user['water_ml']} мл\n"
        f"🚶 Шаги: {user['steps']}\n\n"
        f"📊 <b>Анализ:</b>\n{analysis}\n\n"
        f"🔥 Норма ккал:\n~{calories} ккал\n\n"
        f"💧 Вода:\n~{water_liters} литра\n\n"
        f"🚶 Рекомендация по шагам:\n10000–12000"
    )
    return text
