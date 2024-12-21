from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, StateFilter
from sqlalchemy.future import select

from database.engine import SessionLocal
from database.models import User, Point


user_router = Router()


class Form(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_scores = State()
    waiting_for_subject = State()


@user_router.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды start."""

    await message.answer(
        "Привет!🤚\n"
        "Используйте /register для регистрации или /enter_scores для просмотра баллов.")


@user_router.message(Command('register'))
async def register_command(message: types.Message, state: FSMContext):
    """Обработчик команды регистрации."""

    await state.set_state(Form.waiting_for_first_name.state)
    await message.answer("Введите ваше имя:")


@user_router.message(StateFilter(Form.waiting_for_first_name))
async def process_first_name(message: types.Message, state: FSMContext):
    first_name = message.text
    await state.update_data(first_name=first_name)
    await state.set_state(Form.waiting_for_last_name.state)
    await message.answer("Введите вашу фамилию:")


@user_router.message(StateFilter(Form.waiting_for_last_name))
async def process_last_name(message: types.Message, state: FSMContext):
    last_name = message.text
    user_data = await state.get_data()
    first_name = user_data.get('first_name')
    telegram_user_id = message.from_user.id

    async with SessionLocal() as session:
        new_user = User(
            id=telegram_user_id,
            first_name=first_name,
            last_name=last_name)
        session.add(new_user)
        await session.commit()

    await message.answer("Вы успешно зарегистрированы!")
    await state.clear()


@user_router.message(Command('enter_scores'))
async def enter_scores_command(message: types.Message, state: FSMContext):
    """Обработчик команды ввода баллов по предметам."""

    await state.set_state(Form.waiting_for_subject.state)
    await message.answer("Введите предмет:")


@user_router.message(StateFilter(Form.waiting_for_subject))
async def process_subject(message: types.Message, state: FSMContext):
    subject = message.text
    await state.update_data(subject=subject)
    await state.set_state(Form.waiting_for_scores.state)
    await message.answer("Введите ваши баллы ЕГЭ:")


@user_router.message(StateFilter(Form.waiting_for_scores))
async def process_scores(message: types.Message, state: FSMContext):
    scores = message.text
    user_data = await state.get_data()
    subject = user_data.get('subject')

    async with SessionLocal() as session:
        user_id = message.from_user.id
        user = await session.execute(select(User).where(User.id == user_id))
        user = user.scalars().first()

        if user:
            new_point = Point(
                subject=subject,
                point=int(scores),
                user_id=user.id)
            session.add(new_point)
            await session.commit()
            await message.answer("Ваши баллы сохранены!")
        else:
            await message.answer(
                "Пользователь не найден. Пожалуйста, зарегистрируйтесь."
                )

    await state.clear()


@user_router.message(Command('view_scores'))
async def view_scores_command(message: types.Message):
    """Обработчик команды вывода баллов."""

    async with SessionLocal() as session:
        user_id = message.from_user.id
        user = await session.execute(select(User).where(User.id == user_id))
        user = user.scalars().first()

        if user:
            points = await session.execute(
                select(Point).where(Point.user_id == user.id)
                )
            points = points.scalars().all()
            if points:
                scores_message = "\n".join(
                    [f"{point.subject}: {point.point}" for point in points]
                    )
                await message.answer(f"Ваши баллы:\n{scores_message}")
            else:
                await message.answer("У вас нет сохраненных баллов.")
        else:
            await message.answer(
                "Пользователь не найден. Пожалуйста, зарегистрируйтесь."
                )
