import asyncio
from datetime import datetime

from utils.db import get_due_reminders, mark_reminder_sent, users_for_morning_pulse, mark_pulse_asked
from utils.helpers import today_str


async def start_reminder_loop(bot):
    while True:
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')

        reminders = await get_due_reminders(now_str)
        for reminder in reminders:
            try:
                await bot.send_message(reminder['user_id'], f"🔔 <b>Напоминание</b>\n\n{reminder['text']}")
                await mark_reminder_sent(reminder['id'])
            except Exception:
                pass

        # Утренний пульс дня: один раз в день после 08:00.
        if now.hour == 8 and now.minute <= 5:
            users = await users_for_morning_pulse(today_str())
            for user in users:
                try:
                    await bot.send_message(
                        user['user_id'],
                        '💓 <b>Пульс дня</b>\n\nОцени через /pulse: энергия, настроение и сон от 1 до 10. Я подстрою совет под твой день.'
                    )
                    await mark_pulse_asked(user['user_id'], today_str())
                except Exception:
                    pass

        await asyncio.sleep(20)
