from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.helpers import generate_verification_code
from parser.utils import TournamentDbSaver
from database.db_settings import BaseSettings
from config import ADMINS_IDS
from database.models import Player, Tournament, Judge, Game, GamePlayer
from utils.states import MainStates


async def enter_game_number_judges(message: Message, bot: Bot, state: FSMContext):
    existing_judge = await Judge.get_or_none(tg_chat_id=message.chat.id)
    if existing_judge is not None:
        await message.answer("Введите номер игры")
        await state.set_state(MainStates.enter_game_number)
    else:
        await message.answer("Вы не судья")


async def enter_game_points_judges(message: Message, bot: Bot, state: FSMContext):
    try:
        await state.set_data({"game_number": int(message.text)})
    except Exception:
        await message.answer("Неизвестная ошибка, введите число")
        return
    await message.answer("Введите дополнительные баллы по формату (инструкция по команде /help)")
    await state.set_state(MainStates.enter_game_points)


async def send_points_to_players(message: Message, bot: Bot, state: FSMContext):
    judge = await Judge.get(tg_chat_id=message.chat.id)
    data = await state.get_data()
    game_number = data["game_number"]
    score_data_list = message.text.split("\n")

    for score_data in score_data_list:
        try:
            parts = score_data.split(" - ", maxsplit=2)
            if len(parts) != 3:
                raise ValueError(f"Неверный формат данных: {score_data}")
            player_slot, score, comment = score_data.split(" - ")
            score = float(score)

            game = await Game.get(judge=judge, game_num=int(game_number)).prefetch_related("judge")
            game_player = await GamePlayer.get(game=game, player_slot=player_slot).prefetch_related("player")

            if game_player.player.tg_chat_id is None:
                continue

            await bot.send_message(chat_id=game_player.player.tg_chat_id,
                                   text=f"За игру №{game_number} ты получил {score} \n"
                                        f"Пояснение: {comment} \n \n"
                                        f"Судья: {judge.judge_name}")
        except Exception as e:
            await message.answer("Ошибка при обработке строки, возможно неверный формат")
            print(e)
            return
    await message.answer(f"Информация о доп баллах успешно отправлена игрокам")
    await state.set_state(MainStates.blank)



