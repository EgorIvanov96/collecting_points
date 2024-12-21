import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv, find_dotenv

from common.bot_commond import private

load_dotenv(find_dotenv())

from database.engine import create_db
from handlers.users import user_router


logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('BOT_TOKEN'))

storage = MemoryStorage()
dp = Dispatcher(storage=storage, bot=bot)

dp.include_router(user_router)


async def on_startup(bot):

    await create_db()


async def main():
    dp.startup.register(on_startup)
    await bot.set_my_commands(commands=private,
                              scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


asyncio.run(main())
