import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
# from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter
from sqlalchemy.future import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.exc import IntegrityError
# from aiogram.dispatcher import FSM


from dotenv import load_dotenv, find_dotenv

from common.bot_commond import private
# from database.engine import create_db

load_dotenv(find_dotenv())

from database.engine import create_db, SessionLocal
from database.models import User, Point

bot = Bot(token=os.getenv('BOT_TOKEN'))

storage = MemoryStorage()
dp = Dispatcher(storage=storage, bot=bot)


class Form(StatesGroup):
    first_name = State()
    last_name = State()
    subject = State()
    score = State()


"""@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        '''Добро пожаловать! 👋
В этом боте ты можешь хранить свои баллы ЕГЭ.

Используйте /register для регистрации или /login для входа.
Команда /enter_scores: позволяет вводить свои баллы ЕГЭ.
Команда /view_scores: выводит твои сохраненные баллы.
        ''')"""


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выберите команду: /register для регистрации или /enter_scores для входа в аккаунт.")


@dp.message(Command('register'))
async def cmd_register(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(Form.first_name)


@dp.message(StateFilter(Form.first_name))
async def process_first_name(message: types.Message, state: FSMContext):
    data = await state.get_data()  # Получаем текущие данные состояния
    data['first_name'] = message.text  # Обновляем данные
    await state.update_data(data)  # Сохраняем обновленные данные

    await message.answer("Введите вашу фамилию:")
    await state.set_state(Form.last_name)


@dp.message(StateFilter(Form.last_name))
async def process_last_name(message: types.Message, state: FSMContext):
    data = await state.get_data()  # Получаем текущие данные состояния
    data['last_name'] = message.text  # Обновляем данные
    await state.update_data(data)  # Сохраняем обновленные данные

    first_name = data['first_name']  # Извлекаем данные
    last_name = data['last_name']

    # Сохранение пользователя в базе данных
    async with SessionLocal() as session:  # Используем асинхронный контекст
        async with session.begin():  # Начинаем транзакцию
            user = User(first_name=first_name, last_name=last_name)
            session.add(user)  # Добавляем пользователя в сессию
        await session.commit()  # Асинхронный коммит

    await message.answer("Вы успешно зарегистрированы!")
    await state.set_state(None)


@dp.message(Command('enter_scores'))
async def cmd_enter_scores(message: types.Message, state: FSMContext):
    await message.answer("Введите название предмета:")
    await state.set_state(Form.subject)


@dp.message(StateFilter(Form.subject))
async def process_subject(message: types.Message, state: FSMContext):
    # Получаем данные состояния
    data = await state.get_data()

    # Обновляем данные состояния
    await state.update_data(subject=message.text)

    await message.answer("Введите количество баллов:")
    await state.set_state(Form.score)


@dp.message(StateFilter(Form.score))
async def process_score(message: types.Message, state: FSMContext):
    # Получаем данные состояния
    data = await state.get_data()

    # Обновляем данные с новым значением score
    await state.update_data(score=message.text)

    # Извлекаем значения subject и score
    subject = data.get('subject')
    score = message.text  # Мы уже сохранили score в состоянии

    # Сохранение баллов в базе данных
    user_first_name = data.get('first_name')  # Получаем имя пользователя

    # Создаем асинхронную сессию
    async with SessionLocal() as session:
        async with session.begin():
            # Используем select для получения пользователя
            result = await session.execute(select(User).filter(User.first_name == user_first_name))
            user = result.scalars().first()  # Получаем первого пользователя из результата

            if user:
                point = Point(subject=subject, point=score, user_id=user.id)
                session.add(point)
                await session.commit()  # Асинхронный коммит
                await message.answer("Баллы успешно сохранены!")
            else:
                await message.answer("Пользователь не найден.")

    await state.set_state(None)


@dp.message(Command('view_scores'))
async def cmd_view_scores(message: types.Message):
    user_first_name = 'Введите_ваше_имя'  # Здесь вам нужно найти способ, чтобы получить имя пользователя
    async with SessionLocal() as session:
        async with session.begin():
            # Используем select для получения пользователя
            result = await session.execute(select(User).filter(User.first_name == user_first_name))
            user = result.scalars().first()  # Получаем первого пользователя из результата

            if user:
                # Получаем баллы пользователя
                scores_result = await session.execute(select(Point).filter(Point.user_id == user.id))
                scores = scores_result.scalars().all()  # Получаем все баллы

                if scores:
                    response = "\n".join([f"{score.subject}: {score.point} баллов" for score in scores])
                    await message.answer(f"Ваши баллы:\n{response}")
                else:
                    await message.answer("У вас нет сохраненных баллов.")
            else:
                await message.answer("Пользователь не найден.")


async def on_startup(bot):

    await create_db()


async def main():
    dp.startup.register(on_startup)
    await bot.set_my_commands(commands=private,
                              scope=types.BotCommandScopeAllPrivateChats())
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


asyncio.run(main())
