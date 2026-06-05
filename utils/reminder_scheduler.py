import asyncio
from datetime import datetime

from utils.db import get_due_reminders, mark_reminder_sent


async def start_reminder_loop(bot):
    while True:
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        reminders = await get_due_reminders(now_str)
        for reminder in reminders:
            try:
                await bot.send_message(
                    reminder['user_id'],
                    f"🔔 <b>Напоминание</b>\n\n{reminder['text']} 📚"
                )
                await mark_reminder_sent(reminder['id'])
            except Exception:
                pass
        await asyncio.sleep(20)
