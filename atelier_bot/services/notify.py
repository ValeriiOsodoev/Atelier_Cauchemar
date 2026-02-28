import base64
import os

from aiogram import Bot
from aiogram.types import (BufferedInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup)

from atelier_bot.db.db import get_artwork_by_name_and_user

# Get atelier ID from environment variable, fallback to default
ATELIER_ID = int(os.getenv("ATELIER_ID", "144227441"))


async def notify_atelier(
    user_id: int, username: str, art_name: str, paper_name: str,
    copies: int, sheets: int, order_id: int
) -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        return
    bot = Bot(token=token)

    # Get artwork icon
    artwork = await get_artwork_by_name_and_user(user_id, art_name)
    icon_data = None
    if artwork and artwork.get("image_icon"):
        icon_b64 = artwork["image_icon"]
        if icon_b64.startswith("data:image"):
            icon_b64 = icon_b64.split(",", 1)[1]
        try:
            icon_data = base64.b64decode(icon_b64)
        except Exception:
            pass

    text = (
        "🖨 Новый заказ на печать\n\n"
        f"👤 Художник: @{username}\n"
        f"🎨 Работа: {art_name}\n"
        f"📄 Бумага: {paper_name}\n"
        f"🔢 Копий: {copies}\n"
        f"📊 Листов: {sheets}\n\n"
        "Подтвердите заказ для списания бумаги:"
    )

    # Добавляем кнопку подтверждения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Подтвердить заказ",
            callback_data=f"atelier_confirm_{order_id}"
        )]
    ])

    if icon_data:
        icon_file = BufferedInputFile(
            icon_data, filename="artwork_icon.jpg"
        )
        await bot.send_photo(
            ATELIER_ID, photo=icon_file, caption=text,
            reply_markup=keyboard
        )
    else:
        await bot.send_message(ATELIER_ID, text, reply_markup=keyboard)

    await bot.session.close()
