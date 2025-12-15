from aiogram.fsm.state import State, StatesGroup


class BroadcastState(StatesGroup):
    waiting_for_text = State()
