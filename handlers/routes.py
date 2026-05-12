from aiogram import Router, F, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from students.database import create_user, user_exists, get_user, change_group
from handlers.parser import check_all_days, normalize_group

class Registration(StatesGroup):
    usergroup = State()
    waiting_for_group = State()

router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if not await user_exists(tg_id):
        await message.answer(f"Привет, {message.from_user.full_name}!", parse_mode="Markdown")
        await state.set_state(Registration.usergroup)
    else:
        await message.answer("Ты уже зарегистрирован.")

@router.message(Registration.usergroup, F.text)
async def process_group(message: Message, state: FSMContext):
    group = message.text.strip().upper()
    if len(group) < 2:
        await message.answer("Группа слишком короткая, попробуй ещё раз")
        return
    tg_id = message.from_user.id
    name = message.from_user.full_name
    await create_user(tg_id, name, group)
    await message.answer(f"Отлично, ты в группе {group}")
    await state.clear()

@router.message(Command("anket"))
async def anket(message: Message):
    tg_id = message.from_user.id
    if not await user_exists(tg_id):
        await message.answer("Ты ещё не зарегистрирован. Напиши /start")
        return
    user_data = await get_user(tg_id)
    await message.answer(f"Ваша группа: {user_data['group']}")

@router.message(Command("change"))
async def changes(message: Message):
    tg_id = message.from_user.id
    if not await user_exists(tg_id):
        await message.answer("Сначала зарегистрируйся через /start")
        return
    user_data = await get_user(tg_id)
    group = user_data["group"]
    btn1 = InlineKeyboardButton(text="Да", callback_data="changegroup")
    btn2 = InlineKeyboardButton(text="Нет", callback_data="nochangegroup")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[btn1], [btn2]])
    await message.answer(f"Ваша группа: {group}. Желаете изменить?", reply_markup=keyboard)

@router.callback_query(F.data == "changegroup")
async def change_user_group(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите новую группу", parse_mode="Markdown")
    await state.set_state(Registration.waiting_for_group)

@router.message(Registration.waiting_for_group, F.text)
async def changegroup(message: Message, state: FSMContext):
    group = message.text.strip().upper()
    if len(group) < 2:
        await message.answer("Группа слишком короткая, попробуй ещё раз")
        return
    tg_id = message.from_user.id
    await change_group(tg_id, group)
    await message.answer(f"Группа изменена на {group}")
    await state.clear()

@router.callback_query(F.data == "nochangegroup")
async def no_change(callback: CallbackQuery):
    await callback.answer("Ок, группа не изменена")

@router.message(Command("replacements"))
async def show_replacements(message: Message):
    tg_id = message.from_user.id
    if not await user_exists(tg_id):
        await message.answer("Сначала зарегистрируйся через /start")
        return
    user_data = await get_user(tg_id)
    group = user_data["group"]
    msg = await message.answer("🔍 Ищу замены...")
    all_replacements = await check_all_days()
    my_replacements = [r for r in all_replacements if normalize_group(r["group"]) == normalize_group(group)]
    if not my_replacements:
        await msg.edit_text(f"✅ Замен для группы {group} не найдено.")
        return
    lines = [f"📋 <b>Замены для группы {group}:</b>\n"]
    for r in my_replacements:
        day_ru = {"monday": "Пн", "tuesday": "Вт", "wednesday": "Ср", "thursday": "Чт", "friday": "Пт"}.get(r["day"], r["day"])
        lines.append(f"▫️ <b>{day_ru}</b>, пара {r['pair']}\n   {r['replaced']} → {r['new']}\n   Преподаватель: {r['teacher']} | Кабинет: {r['room']}")
    await msg.edit_text("\n".join(lines), parse_mode="HTML")

@router.message(Command("help"))
async def helpage(message: Message):
    await message.answer("Бот для получения переносов колледжа")

@router.message(Command("menu"))
async def menu(message: Message):
    await message.answer("Меню пока пустое")
