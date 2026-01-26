from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    choosing_artwork = State()
    choosing_paper = State()
    entering_copies = State()
    entering_sheets = State()
    confirming = State()
    adding_artwork = State()
    adding_paper = State()
    # New states for atelier workflow
    atelier_adding_artwork_user_id = State()
    atelier_adding_artwork_name = State()
    atelier_adding_artwork_image = State()
    atelier_adding_paper_user_id = State()
    atelier_adding_paper_name = State()
    atelier_adding_paper_quantity = State()
