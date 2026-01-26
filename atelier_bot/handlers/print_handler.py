import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

# tariff limits not used in this bot but kept for reference
from atelier_bot.db.db import (add_paper_for_user, create_artwork,
                               create_or_update_user, create_order,
                               decrement_paper, search_users)
from atelier_bot.db.db import get_artworks_for_user
from atelier_bot.db.db import get_artworks_for_user as db_get_artworks
from atelier_bot.db.db import get_paper_by_id
from atelier_bot.db.db import get_papers_for_user
from atelier_bot.db.db import get_papers_for_user as db_get_papers
from atelier_bot.db.db import get_user
from atelier_bot.keyboards.print_keyboards import (artworks_keyboard,
                                                   confirm_keyboard,
                                                   main_menu_keyboard,
                                                   main_reply_keyboard,
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
    reply_kb = main_reply_keyboard(is_atelier)
    if is_atelier:
        text = (
            "Добро пожаловать в Atelier Cauchemar (Ателье)!\n\n"
            "Вы можете:\n"
            "➕ Добавить работу - добавить работу художнику\n"
            "➕ Добавить бумагу - пополнить баланс бумаги художнику\n\n"
            "Вы будете получать уведомления о новых заказах на печать."
        )
    else:
        text = (
            "Добро пожаловать в Atelier Cauchemar!\n\n"
            "🖨 Печать - заказать печать работы\n\n"
            "Если у вас нет доступных работ или бумаги, обратитесь в ателье."
        )
    await message.answer(text, reply_markup=reply_kb)
    await message.answer("Выберите действие:", reply_markup=kb)


@router.message(F.text == "🖨 Печать")
async def handle_print_text(message: Message, state: FSMContext):
    """Handle print command from reply keyboard."""
    user_id = message.from_user.id
    if user_id == ATELIER_ID:
        await message.answer("Эта функция только для художников")
        return

    user = await get_user(user_id)
    if not user:
        await message.answer("Вы не зарегистрированы. Попробуйте /start")
        return

    artworks = await get_artworks_for_user(user_id)
    if not artworks:
        await message.answer(
            "У вас нет доступных работ для печати. Обращайтесь в ателье."
        )
        return

    papers = await get_papers_for_user(user_id)
    if not papers:
        await message.answer(
            "У вас нет бумаги на балансе. Обращайтесь в ателье."
        )
        return

    await state.set_state(OrderStates.choosing_artwork)
    await state.update_data(artworks=artworks, papers=papers)
    kb = artworks_keyboard(artworks)
    await message.answer("Выберите работу для печати:", reply_markup=kb)


@router.message(F.text == "➕ Добавить работу")
async def handle_add_art_text(message: Message, state: FSMContext):
    """Handle add artwork command from reply keyboard."""
    if message.from_user.id != ATELIER_ID:
        await message.answer("Эта функция только для ателье")
        return

    await state.set_state(OrderStates.atelier_adding_artwork_user_id)
    await state.update_data(action="add_art")
    await message.answer(
        "Введите username или user_id пользователя для добавления работы:\n\n"
        "Примеры:\n"
        "• @username\n"
        "• 123456789"
    )


@router.message(F.text == "➕ Добавить бумагу")
async def handle_add_paper_text(message: Message, state: FSMContext):
    """Handle add paper command from reply keyboard."""
    if message.from_user.id != ATELIER_ID:
        await message.answer("Эта функция только для ателье")
        return

    await state.set_state(OrderStates.atelier_adding_paper_user_id)
    await state.update_data(action="add_paper")
    await message.answer(
        "Введите username или user_id пользователя для добавления бумаги:\n\n"
        "Примеры:\n"
        "• @username\n"
        "• 123456789"
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
            "У вас нет доступных работ для печати. Обращайтесь в ателье."
        )
        return

    papers = await get_papers_for_user(user_id)
    if not papers:
        await callback.message.answer(
            "У вас нет бумаги на балансе. Обращайтесь в ателье."
        )
        return

    await state.set_state(OrderStates.choosing_artwork)
    await state.update_data(artworks=artworks, papers=papers)
    kb = artworks_keyboard(artworks)
    await callback.message.answer(
        "Выберите работу для печати:", reply_markup=kb
    )


@router.callback_query(F.data == "add_paper")
async def handle_add_paper(callback: CallbackQuery, state: FSMContext):
    print(f"DEBUG: add_paper callback from user {callback.from_user.id}")
    if callback.from_user.id != ATELIER_ID:
        await callback.answer("Эта функция только для ателье")
        return

    await state.set_state(OrderStates.atelier_adding_paper_user_id)
    await state.update_data(action="add_paper")
    await callback.message.answer(
        "Введите username или user_id пользователя для добавления бумаги:\n\n"
        "Примеры:\n"
        "• @username\n"
        "• 123456789"
    )


@router.callback_query(F.data == "add_art")
async def handle_add_art(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ATELIER_ID:
        await callback.answer("Эта функция только для ателье")
        return

    await state.set_state(OrderStates.atelier_adding_artwork_user_id)
    await state.update_data(action="add_art")
    await callback.message.answer(
        "Введите username или user_id пользователя для добавления работы:\n\n"
        "Примеры:\n"
        "• @username\n"
        "• 123456789"
    )


@router.callback_query(F.data.startswith("art_"))
async def choose_artwork(callback: CallbackQuery, state: FSMContext):
    print(f"DEBUG: choose_artwork called with {callback.data}")
    # read saved state
    data = await state.get_data()
    art_id = int(callback.data.split("_")[1])
    artworks = data.get("artworks", [])
    art = next((a for a in artworks if a["id"] == art_id), None)
    if not art:
        await callback.answer("Работа не найдена или устарела")
        return

    print(f"DEBUG: Found artwork {art['artwork_name']}, "
          f"has icon: {bool(art.get('image_icon'))}")

    # Show artwork icon if available
    if art.get("image_icon"):
        import base64
        from aiogram.types import BufferedInputFile

        try:
            # Remove data URL prefix if present
            icon_b64 = art["image_icon"]
            if icon_b64.startswith("data:image"):
                icon_b64 = icon_b64.split(",", 1)[1]

            icon_data = base64.b64decode(icon_b64)
            icon_file = BufferedInputFile(icon_data, filename="icon.jpg")
            print(f"DEBUG: Sending photo with {len(icon_data)} bytes")
            await callback.message.answer_photo(
                photo=icon_file,
                caption=f"Выбрана работа: {art['artwork_name']}"
            )
            print("DEBUG: Photo sent successfully")
        except Exception as e:
            print(f"DEBUG: Error sending artwork icon: {e}")
            logger.error("Error sending artwork icon: %s", e)
            await callback.message.answer(
                f"Выбрана работа: {art['artwork_name']} (иконка недоступна)")
    else:
        print("DEBUG: No icon, sending text only")
        await callback.message.answer(f"Выбрана работа: {art['artwork_name']}")

    await state.update_data(chosen_art=art)
    await state.set_state(OrderStates.choosing_paper)
    kb = papers_keyboard(data.get("papers", []))
    await callback.message.answer("Выберите бумагу:", reply_markup=kb)


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action and return to main menu."""
    await state.clear()
    is_atelier = callback.from_user.id == ATELIER_ID
    kb = main_menu_keyboard(is_atelier)
    reply_kb = main_reply_keyboard(is_atelier)
    await callback.message.answer("Действие отменено.", reply_markup=reply_kb)
    await callback.message.answer("Выберите действие:", reply_markup=kb)


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
    if not message.text:
        await message.answer("Пожалуйста, введите количество копий")
        return
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


# Atelier workflow handlers
@router.message(OrderStates.atelier_adding_artwork_user_id)
async def atelier_enter_artwork_user(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, введите username или user_id")
        return
    text = message.text.strip()

    # Remove @ from the beginning if present
    if text.startswith('@'):
        text = text[1:]

    # Direct input - try to find user by username or user_id
    users = await search_users(text)
    if not users:
        await message.answer(
            f"Пользователь '{message.text.strip()}' не найден.\n"
            "Проверьте правильность username или user_id и попробуйте снова."
        )
        return
    elif len(users) == 1:
        user_id = users[0]['user_id']
    else:
        await message.answer(
            f"Найдено несколько пользователей по запросу "
            f"'{message.text.strip()}'.\n"
            "Пожалуйста, введите более точный username или "
            "используйте user_id."
        )
        return

    await state.update_data(atelier_artwork_user_id=user_id)
    await state.set_state(OrderStates.atelier_adding_artwork_name)
    await message.answer("Введите название работы:")


@router.message(OrderStates.atelier_adding_paper_user_id)
async def atelier_enter_paper_user(message: Message, state: FSMContext):
    print(f"DEBUG: Received message in atelier_adding_paper_user_id: "
          f"{message.text}")
    if not message.text:
        await message.answer("Пожалуйста, введите username или user_id")
        return
    text = message.text.strip()

    # Remove @ from the beginning if present
    if text.startswith('@'):
        text = text[1:]

    # Direct input - try to find user by username or user_id
    users = await search_users(text)
    if not users:
        await message.answer(
            f"Пользователь '{message.text.strip()}' не найден.\n"
            "Проверьте правильность username или user_id и попробуйте снова."
        )
        return
    elif len(users) == 1:
        user_id = users[0]['user_id']
    else:
        await message.answer(
            f"Найдено несколько пользователей по запросу "
            f"'{message.text.strip()}'.\n"
            "Пожалуйста, введите более точный username или "
            "используйте user_id."
        )
        return

    await state.update_data(atelier_paper_user_id=user_id)
    await state.set_state(OrderStates.atelier_adding_paper_name)
    await message.answer("Введите название бумаги:")


@router.message(OrderStates.atelier_adding_paper_name)
async def atelier_enter_paper_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, введите название бумаги")
        return
    paper_name = message.text.strip()
    if not paper_name:
        await message.answer(
            "Название бумаги не может быть пустым. Попробуйте снова:")
        return

    await state.update_data(atelier_paper_name=paper_name)
    await state.set_state(OrderStates.atelier_adding_paper_quantity)
    await message.answer("Введите количество бумаги (число):")


@router.message(OrderStates.atelier_adding_artwork_name)
async def atelier_enter_artwork_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, введите название работы")
        return
    artwork_name = message.text.strip()
    if not artwork_name:
        await message.answer(
            "Название работы не может быть пустым. Попробуйте снова:")
        return

    await state.update_data(atelier_artwork_name=artwork_name)
    await state.set_state(OrderStates.atelier_adding_artwork_image)
    await message.answer(
        "📸 Отправьте фото работы для создания иконки\n"
        "(или отправьте /skip чтобы пропустить):"
    )


@router.message(OrderStates.atelier_adding_artwork_image, F.photo)
async def atelier_receive_artwork_image(message: Message, state: FSMContext):
    """Handle artwork image upload and create icon."""
    from atelier_bot.db.db import create_artwork_icon

    # Get the largest photo size
    photo = message.photo[-1]

    # Download the photo
    photo_file = await message.bot.download(photo.file_id)
    photo_data = photo_file.read()

    # Create icon
    icon_base64 = create_artwork_icon(photo_data)

    if icon_base64:
        await message.answer("✅ Иконка создана! Добавляю работу...")
    else:
        await message.answer(
            "⚠️ Не удалось создать иконку, но работа будет "
            "добавлена без иконки.")
        icon_base64 = None

    # Get data and create artwork
    data = await state.get_data()
    user_id = data.get("atelier_artwork_user_id")
    artwork_name = data.get("atelier_artwork_name")

    try:
        await create_artwork(user_id, artwork_name, icon_base64)
        await message.answer(
            f"✅ Работа '{artwork_name}' добавлена для пользователя "
            f"ID: {user_id}")
    except Exception as e:
        logger.error("Error adding artwork: %s", e)
        await message.answer("❌ Ошибка при добавлении работы")

    await state.clear()


@router.message(OrderStates.atelier_adding_artwork_image, F.text == "/skip")
async def atelier_skip_artwork_image(message: Message, state: FSMContext):
    """Skip image upload for artwork."""
    # Get data and create artwork without icon
    data = await state.get_data()
    user_id = data.get("atelier_artwork_user_id")
    artwork_name = data.get("atelier_artwork_name")

    try:
        await create_artwork(user_id, artwork_name)
        await message.answer(
            f"✅ Работа '{artwork_name}' добавлена для пользователя "
            f"ID: {user_id} (без иконки)")
    except Exception as e:
        logger.error("Error adding artwork: %s", e)
        await message.answer("❌ Ошибка при добавлении работы")

    await state.clear()


@router.message(OrderStates.atelier_adding_paper_quantity)
async def atelier_enter_paper_quantity(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, введите количество бумаги")
        return
    text = message.text.strip()
    try:
        quantity = int(text)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            "Количество должно быть положительным числом. Попробуйте снова:")
        return

    # Get data and add paper
    data = await state.get_data()
    user_id = data.get("atelier_paper_user_id")
    paper_name = data.get("atelier_paper_name")

    try:
        await add_paper_for_user(user_id, paper_name, quantity)
        await message.answer(
            f"Добавлено {quantity} '{paper_name}' для пользователя "
            f"ID: {user_id}")
    except Exception as e:
        logger.error("Error adding paper: %s", e)
        await message.answer("❌ Ошибка при добавлении бумаги")

    await state.clear()


@router.message(Command("addart"))
async def add_art(message: Message, state: FSMContext):
    """Add artwork for a user (atelier only)."""
    if message.from_user.id != ATELIER_ID:
        await message.answer("Эта команда только для ателье")
        return

    if not message.text:
        await message.answer("Пожалуйста, введите команду корректно")
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) != 3:
        await message.answer(
            "Формат: /addart <user_id> <artwork_name>\n"
            "Пример: /addart 123456789 Моя_работа"
        )
        return

    try:
        user_id = int(parts[1])
        artwork_name = parts[2].strip()
    except ValueError:
        await message.answer(
            "Некорректный user_id. Должен быть числом.")
        return

    try:
        # Create user if doesn't exist
        await create_or_update_user(user_id, f"user_{user_id}")
        await create_artwork(user_id, artwork_name)
        await message.answer(f"Работа '{artwork_name}' добавлена для "
                             f"пользователя ID: {user_id}")
    except Exception as e:
        logger.error("Error adding artwork: %s", e)
        await message.answer("Ошибка при добавлении работы")


@router.message(Command("addpaper"))
async def add_paper(message: Message, state: FSMContext):
    """Add paper for a user (atelier only)."""
    if message.from_user.id != ATELIER_ID:
        await message.answer("Эта команда только для ателье")
        return

    parts = message.text.split()
    if len(parts) != 4:
        await message.answer(
            "Формат: /addpaper <user_id> <paper_name> <quantity>\n"
            "Пример: /addpaper 123456789 Бумага_А4 100"
        )
        return

    try:
        user_id = int(parts[1])
        paper_name = parts[2]
        quantity = int(parts[3])
        if quantity <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            "Некорректные параметры. user_id и quantity должны быть "
            "числами > 0")
        return

    try:
        # Create user if doesn't exist
        await create_or_update_user(user_id, f"user_{user_id}")
        await add_paper_for_user(user_id, paper_name, quantity)
        await message.answer(
            f"Добавлено {quantity} '{paper_name}' для пользователя "
            f"ID: {user_id}")
    except Exception as e:
        logger.error("Error adding paper: %s", e)
        await message.answer("Ошибка при добавлении бумаги")


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


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("Действие отменено")
    else:
        await message.answer("Нет активных действий для отмены")


# Inline query handler for user search
