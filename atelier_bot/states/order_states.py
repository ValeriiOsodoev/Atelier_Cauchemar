from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    choosing_artwork = State()
    choosing_paper = State()
    entering_copies = State()
    confirming = State()
    adding_artwork = State()
    adding_paper = State()
