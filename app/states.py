from aiogram.fsm.state import State, StatesGroup


class PhishingPredictionStates(StatesGroup):
    ENTER_VALUE = State()
