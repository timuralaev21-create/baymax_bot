from aiogram.dispatcher.filters.state import State, StatesGroup


class AddReminder(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()


class UpdateWeight(StatesGroup):
    waiting_for_weight = State()


class AddSteps(StatesGroup):
    waiting_for_steps = State()


class StudyAssistant(StatesGroup):
    waiting_for_question = State()
