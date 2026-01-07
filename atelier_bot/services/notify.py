import os

from aiogram import Bot

ATELIER_ID = 144227441


async def notify_atelier(
    user_id: int, username: str, art_name: str, paper_name: str, copies: int
) -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        return
    bot = Bot(token=token)
    text = (
        "🖨 Новый заказ на печать\n\n"
        f"👤 Художник: @{username}\n"
        f"🎨 Работа: {art_name}\n"
        f"📄 Бумага: {paper_name}\n"
        f"🔢 Количество: {copies}"
    )
    await bot.send_message(ATELIER_ID, text)
    await bot.session.close()
