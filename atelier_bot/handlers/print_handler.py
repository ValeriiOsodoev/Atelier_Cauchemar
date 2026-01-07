import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

# tariff limits not used in this bot but kept for reference
from atelier_bot.db.db import (add_paper_for_user, create_artwork,
                               create_or_update_user, create_order,
                               decrement_paper)
from atelier_bot.db.db import get_artworks_for_user
from atelier_bot.db.db import get_artworks_for_user as db_get_artworks
from atelier_bot.db.db import get_paper_by_id
from atelier_bot.db.db import get_papers_for_user
from atelier_bot.db.db import get_papers_for_user as db_get_papers
from atelier_bot.db.db import get_user
from atelier_bot.keyboards.print_keyboards import (artworks_keyboard,
                                                   confirm_keyboard,
                                                   main_menu_keyboard,
                                                   papers_keyboard)
from atelier_bot.services.notify import notify_atelier
from atelier_bot.states.order_states import OrderStates

router = Router()

logger = logging.getLogger(__name__)

ATELIER_ID = 144227441


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await create_or_update_user(
        message.from_user.id, message.from_user.username
    )
    is_atelier = message.from_user.id == ATELIER_ID
    kb = main_menu_keyboard(is_atelier)
    await message.answer(
        "Добро пожаловать в Atelier Cauchemar!",
        reply_markup=kb,
    )


@router.callback_query(F.data == "print")
async def handle_print(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    if not user:
        await callback.answer("Вы не зарегистрированы. Попробуйте /start")
        return

    artworks = await get_artworks_for_user(user_id)
    if not artworks:
        await callback.message.answer(
            "У вас нет зарегистрированных работ. Добавьте их через /addart"
        )
        return

    papers = await get_papers_for_user(user_id)
    if not papers:
        await callback.message.answer(
            "У вас нет бумаги на балансе. Обратитесь в ателье для пополнения"
        )
        return

    await state.set_state(OrderStates.choosing_artwork)
    await state.update_data(artworks=artworks, papers=papers)
    kb = artworks_keyboard(artworks)
    await callback.message.answer(
        "Выберите работу для печати:", reply_markup=kb
    )


@router.callback_query(F.data.startswith("art_"))
async def choose_artwork(callback: CallbackQuery, state: FSMContext):
    # read saved state
    data = await state.get_data()
    art_id = int(callback.data.split("_")[1])
    artworks = data.get("artworks", [])
    art = next((a for a in artworks if a["id"] == art_id), None)
    if not art:
        await callback.answer("Работа не найдена или устарела")
        return
    await state.update_data(chosen_art=art)
    await state.set_state(OrderStates.choosing_paper)
    kb = papers_keyboard(data.get("papers", []))
    await callback.message.answer("Выберите бумагу:", reply_markup=kb)


@router.callback_query(F.data.startswith("paper_"))
async def choose_paper(callback: CallbackQuery, state: FSMContext):
    paper_id = int(callback.data.split("_")[1])
    paper = await get_paper_by_id(paper_id)
    if not paper:
        await callback.answer("Бумага не найдена")
        return
    await state.update_data(chosen_paper=paper)
    await state.set_state(OrderStates.entering_copies)
    await callback.message.answer(
        "Введите количество копий для печати (число):"
    )


@router.callback_query(F.data == "back_to_artworks")
async def back_to_artworks(callback: CallbackQuery, state: FSMContext):
    """Return to artwork selection during the print flow."""
    data = await state.get_data()
    artworks = data.get("artworks") or []
    if not artworks:
        await callback.answer("Нет доступных работ")
        return
    await state.set_state(OrderStates.choosing_artwork)
    kb = artworks_keyboard(artworks)
    await callback.message.answer(
        "Выберите работу:", reply_markup=kb
    )


@router.message(OrderStates.entering_copies)
async def enter_copies(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("Пожалуйста, введите корректное число")
        return
    copies = int(text)
    data = await state.get_data()
    paper = data.get("chosen_paper")
    if copies <= 0:
        await message.answer("Количество должно быть больше нуля")
        return
    if copies > paper["quantity"]:
        await message.answer(
            f"Недостаточно бумаги. Доступно: {paper['quantity']}"
        )
        return
    await state.update_data(copies=copies)
    await state.set_state(OrderStates.confirming)

    art = data.get("chosen_art")
    confirm_text = (
        f"Подтвердите заказ:\n\n"
        f"Работа: {art['artwork_name']}\n"
        f"Бумага: {paper['paper_name']}\n"
        f"Копии: {copies}\n"
        f"Списание бумаги: {copies}"
    )
    kb = confirm_keyboard()
    await message.answer(confirm_text, reply_markup=kb)


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    art = data.get("chosen_art")
    paper = data.get("chosen_paper")
    copies = data.get("copies")
    # perform DB updates
    await decrement_paper(paper["id"], copies)
    now = datetime.utcnow().isoformat()
    await create_order(
        user_id=user_id,
        artwork_name=art["artwork_name"],
        paper_name=paper["paper_name"],
        copies=copies,
        status="new",
        created_at=now,
    )
    # notify atelier
    await notify_atelier(
        user_id=user_id,
        username=callback.from_user.username,
        art_name=art["artwork_name"],
        paper_name=paper["paper_name"],
        copies=copies,
    )
    await callback.message.answer("Заказ принят и отправлен в ателье 🖨️")
    await state.clear()


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено")


@router.message(Command("addart"))
async def add_art(message: Message, state: FSMContext):
    """Quick helper to add an artwork (dev only)."""
    logger.debug("add_art called with text: %s", message.text)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Введите название работы:")
        await state.set_state(OrderStates.adding_artwork)
        return
    name = parts[1].strip()
    try:
        await create_artwork(message.from_user.id, name)
    except Exception:
        logger.exception("Failed to create artwork")
        await message.answer(
            "Произошла ошибка при добавлении работы. Попробуйте позже."
        )
        return
    await message.answer(f"Работа '{name}' добавлена")


@router.message(Command("addpaper"))
async def add_paper(message: Message, state: FSMContext):
    """Quick helper to add paper to user: /addpaper Название Кол-во"""
    logger.debug("add_paper called with text: %s", message.text)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[2].isdigit():
        await message.answer(
            "Введите название бумаги и количество через пробел:"
        )
        await state.set_state(OrderStates.adding_paper)
        return
    name = parts[1].strip()
    qty = int(parts[2])
    try:
        await add_paper_for_user(message.from_user.id, name, qty)
    except Exception:
        logger.exception("Failed to add paper")
        await message.answer(
            "Произошла ошибка при добавлении бумаги. Попробуйте позже."
        )
        return
    await message.answer(f"Добавлено: {name} ({qty})")


@router.message(Command("ping"))
async def cmd_ping(message: Message):
    await message.answer("pong")


@router.message(Command("myworks"))
async def cmd_myworks(message: Message):
    works = await db_get_artworks(message.from_user.id)
    if not works:
        await message.answer("У вас нет работ")
        return
    text = "Ваши работы:\n" + "\n".join(w["artwork_name"] for w in works)
    await message.answer(text)


@router.message(Command("mypapers"))
async def cmd_mypapers(message: Message):
    papers = await db_get_papers(message.from_user.id)
    if not papers:
        await message.answer("У вас нет бумаги")
        return
    text = "Баланс бумаги:\n" + "\n".join(
        f"{p['paper_name']}: {p['quantity']}" for p in papers
    )
    await message.answer(text)


@router.message(OrderStates.adding_artwork)
@router.message(OrderStates.adding_paper)
async def handle_adding_states(message: Message, state: FSMContext):
    st = await state.get_state()
    logger.debug("handle_adding_states state=%s text=%s", st, message.text)
    if st == OrderStates.adding_artwork:
        name = message.text.strip()
        if not name:
            await message.answer(
                "Название не может быть пустым. Попробуйте снова:"
            )
            return
        try:
            await create_artwork(message.from_user.id, name)
        except Exception:
            logger.exception("Failed to create artwork in state handler")
            await message.answer(
                "Произошла ошибка при добавлении работы. Попробуйте позже."
            )
            await state.clear()
            return
        await message.answer(f"Работа '{name}' добавлена")
        await state.clear()
        return
    if st == OrderStates.adding_paper:
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) < 2 or not parts[1].isdigit():
            await message.answer(
                "Неверный формат. Введите: Название Кол-во "
                "(например: Canson 5)"
            )
            return
        name = parts[0].strip()
        qty = int(parts[1])
        try:
            await add_paper_for_user(message.from_user.id, name, qty)
        except Exception:
            logger.exception("Failed to add paper in state handler")
            await message.answer(
                "Произошла ошибка при добавлении бумаги. Попробуйте позже."
            )
            await state.clear()
            return
        await message.answer(f"Добавлено: {name} ({qty})")
        await state.clear()
        return
