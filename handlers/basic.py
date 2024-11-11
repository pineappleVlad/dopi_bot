from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.models import Player, Judge
from utils.states import MainStates


async def start(message: Message, bot: Bot, state: FSMContext):
    register_player = await Player.get_or_none(tg_chat_id=message.chat.id)
    register_judge = await Judge.get_or_none(tg_chat_id=message.chat.id)
    if register_player is not None:
        await message.answer(
            "Вы уже зарегистрированы, введите четырехзначный верификационный код для авторизации"
        )
        await state.set_data({"nickname": register_player.nickname})
        await state.set_state(MainStates.enter_verify_code_player)
    elif register_judge is not None:
        await message.answer(
            "Вы уже зарегистрированы, введите четырехзначный верификационный код для авторизации"
        )
        await state.set_data({"nickname": register_judge.judge_name})
        await state.set_state(MainStates.enter_verify_code_judge)
    else:
        await message.answer(
            "В этом боте вы будете узнавать свои доп. баллы и пояснения к ним после игры. \n \n"
            "Этот тг-аккаунт еще не зарегистрирован в боте, введите свой ник ФСМ (с учетом регистра и цифр в нике).\n\n"
            " Если обычная версия ника не ищется, проверьте как он записан на mafbase.ru или уточните у организатора"
        )
        await state.set_state(MainStates.enter_nickname)


