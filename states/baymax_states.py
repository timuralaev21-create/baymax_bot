from aiogram.dispatcher.filters.state import State, StatesGroup


class AddReminder(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()


class HealthSetup(StatesGroup):
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_body_type = State()


class UpdateWeight(StatesGroup):
    waiting_for_weight = State()


class AddSteps(StatesGroup):
    waiting_for_steps = State()


class AddDayPlan(StatesGroup):
    waiting_for_text = State()


class AddGoal(StatesGroup):
    waiting_for_text = State()


class RemoveGoal(StatesGroup):
    waiting_for_id = State()


class DailyPulse(StatesGroup):
    waiting_for_energy = State()
    waiting_for_mood = State()
    waiting_for_sleep = State()


class StudyExplain(StatesGroup):
    waiting_for_topic = State()


class StudyTimer(StatesGroup):
    waiting_for_topic = State()
    waiting_for_minutes = State()


class MentalChat(StatesGroup):
    waiting_for_message = State()


class PhysicalHealth(StatesGroup):
    waiting_for_symptoms = State()
