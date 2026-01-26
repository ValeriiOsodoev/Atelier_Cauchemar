import asyncio
import os

#
"""Entry point for the atelier_bot package.

Run with: python -m atelier_bot.main
"""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from atelier_bot.db.db import init_db
from atelier_bot.handlers.print_handler import router as print_router

# This module is intended to be run as a module:
# python -m atelier_bot.main


logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is required")

    await init_db()

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(print_router)

    try:
        print("Bot started")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
