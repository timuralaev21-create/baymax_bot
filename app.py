import asyncio
from aiogram import executor

from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db import init_db
from utils.reminder_scheduler import start_reminder_loop


async def on_startup(dispatcher):
    await init_db()
    await set_default_commands(dispatcher)
    try:
        await on_startup_notify(dispatcher)
    except Exception:
        pass
    asyncio.create_task(start_reminder_loop(dispatcher.bot))


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
