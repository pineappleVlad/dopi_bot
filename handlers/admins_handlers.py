from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.helpers import generate_verification_code
from parser.utils import TournamentDbSaver
from database.db_settings import BaseSettings
from config import ADMINS_IDS
from database.models import Player, Tournament, Judge
from utils.states import MainStates


async def create_tournament_admin(message: Message, bot: Bot, state: FSMContext):
    if str(message.chat.id) not in ADMINS_IDS:
        return
    await state.set_state(MainStates.enter_tournament_url)
    await message.answer("Введите ссылку на турнир")


async def enter_tournament_url(message: Message, bot: Bot, state: FSMContext):
    try:
        await TournamentDbSaver.save_seating_to_db(url=message.text)
        await message.answer("Турнир успешно сохранен в базе")
        await state.set_state(MainStates.blank)
    except Exception as e:
        print(f"ERROR TEXT: {e}")
        await message.answer("Произошла ошибка, возможно ссылка не корректна")


async def close_tournament_admin(message: Message, bot: Bot, state: FSMContext):
    if str(message.chat.id) not in ADMINS_IDS:
        return
    await state.set_state(MainStates.close_tournament_url)
    await message.answer("Введите ссылку на турнир")


async def clear_tournament_from_db(message: Message, bot: Bot, state: FSMContext):
    format_url = await TournamentDbSaver.format_url(message.text)
    existed_tournament = await Tournament.filter(url=format_url)
    if not existed_tournament:
        await message.answer("Неверная ссылка")
    else:
        await TournamentDbSaver.clear_tables()
        await message.answer("Турнир успешно закрыт и удален из базы")
        await state.set_state(MainStates.blank)


async def regenerate_verify_code_request(message: Message, bot: Bot, state: FSMContext):
    if str(message.chat.id) not in ADMINS_IDS:
        return
    await state.set_state(MainStates.enter_nickname_for_regenerate_verify_code)
    await message.answer("Введите ник игрока, у которого нужно перегенирировать код")


async def regenerate_verify_code_response(message: Message, bot: Bot, state: FSMContext):
    existed_player = await Player.get_or_none(nickname=message.text)
    existed_judge = await Judge.get_or_none(judge_name=message.text)
    if existed_player is None:
        await message.answer("Игрок с таким ником не найден")
    elif existed_judge is not None:
        judge = await Judge.get(judge_name=message.text)
        new_code = await generate_verification_code()
        judge.verify_code = new_code
        await judge.save()
        await message.answer(f"Ник судьи: {message.text} \n"
                             f"Новый код {new_code}")
    else:
        player = await Player.get(nickname=message.text)
        new_code = await generate_verification_code()
        player.verification_code = new_code
        await player.save()
        await message.answer(f"Ник игрока: {message.text} \n"
                             f"Новый код: {new_code}")
    await state.set_state(MainStates.blank)


async def help_command(message: Message, bot: Bot, state: FSMContext):
    existing_judge = await Judge.get_or_none(tg_chat_id=message.chat.id)
    if existing_judge is not None:
        await message.answer("Инструкция по вбиванию дополнительных баллов в бота: \n \n"
                             "1) Вводите команду /enter_game_result \n"
                             "2) В отвеном сообщении боту отправляете номер прошедшего тура \n"
                             "3) В следующем сообщении отправляете результаты игры СТРОГО в правильном формате \n"
                             "Любой неверный символ и данные никому не придут \n"
                             "Доп баллы вводить нужно через точку (например 0.3) \n \n"
                             "Формат: \n"
                             "{слот игрока} - {допы} - {пояснение} \n"
                             "{слот игрока} - {допы} - {пояснение} \n"
                             "и т.д. \n \n"
                             "Пример: \n"
                             "1 - 0.3 - Оставил верное завещание \n"
                             "2 - 0.4 - Вписался к шерифу, в соло выиграл версию \n"
                             "и т.д.")
    else:
        return
