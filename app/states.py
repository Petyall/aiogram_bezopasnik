from aiogram.fsm.state import State, StatesGroup


class PhishingPredictionStates(StatesGroup):
    ENTER_VALUE = State()


class GetMetricStates(StatesGroup):
    SELECT_CATEGORY = State()
    SELECT_METRIC = State()
