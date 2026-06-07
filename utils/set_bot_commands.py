from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустить Baymax'),
            types.BotCommand('menu', 'Главное меню'),
            types.BotCommand('help', 'Описание всех кнопок'),
            types.BotCommand('profile', 'Профиль и леденцы'),
            types.BotCommand('health', 'Здоровье'),
            types.BotCommand('norm', 'Рассчитать КБЖУ и воду'),
            types.BotCommand('water', 'Добавить 250 мл воды'),
            types.BotCommand('resetwater', 'Сбросить воду'),
            types.BotCommand('steps', 'Добавить шаги'),
            types.BotCommand('mental', 'Ментальная поддержка'),
            types.BotCommand('physical', 'Физическое здоровье'),
            types.BotCommand('reminders', 'Напоминания'),
            types.BotCommand('addreminder', 'Добавить напоминание'),
            types.BotCommand('myreminders', 'Мои напоминания'),
            types.BotCommand('day', 'План дня и цели'),
            types.BotCommand('plan', 'План на сегодня'),
            types.BotCommand('goals', 'Цели'),
            types.BotCommand('pulse', 'Пульс дня'),
            types.BotCommand('study', 'Учёба'),
            types.BotCommand('explain', 'Объяснить тему'),
            types.BotCommand('timer', 'Задачи на время'),
            types.BotCommand('shop', 'Магазин статусов'),
        ]
    )
