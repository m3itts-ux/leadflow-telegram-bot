import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

import config
from handlers import router


async def main() -> None:
    bot = Bot(token=config.require_bot_token())
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
