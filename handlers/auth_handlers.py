from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from utils.helpers import generate_verification_code

from database.models import Player, Judge
from utils.states import MainStates


async def enter_nickname_for_registration(message: Message, bot: Bot, state: FSMContext):
    existing_player = await Player.get_or_none(nickname=message.text)
    existing_judge = await Judge.get_or_none(judge_name=message.text)
    if existing_player is not None:
        if existing_player.verify_code is not None:
            await state.set_data({"nickname": existing_player.nickname})
            await message.answer("Игрок с таким ником уже есть в боте, если это вы, отправьте верификационный код")
            await state.set_state(MainStates.enter_verify_code_player)
        else:
            verify_code = await generate_verification_code()
            await message.answer(f"Вот ваш верификационный код - {verify_code} \n"
                                 "Запомните его для последующей авторизации и никому не показывайте \n \n"
                                 "Ваш аккаунт уcпешно привязан, больше ничего делать не нужно \n"
                                 "Код действует 1 турнир")
            existing_player.verify_code = verify_code
            existing_player.tg_chat_id = message.chat.id
            await existing_player.save()
            await state.set_state(MainStates.blank)
    elif existing_judge is not None:
        if existing_judge.verify_code is not None:
            await state.set_data({"nickname": existing_judge.judge_name})
            await message.answer("Судья с таким ником уже есть в боте, если это вы, отправьте верификационный код")
            await state.set_state(MainStates.enter_verify_code_judge)
        else:
            verify_code = await generate_verification_code()
            await message.answer(f"Вот ваш верификационный код - {verify_code} \n"
                                 "Запомните его для последующей авторизации и никому не показывайте \n \n"
                                 "Ваш аккаунт уcпешно привязан, можете вбивать игры \n"
                                 "Код действует 1 турнир")
            existing_judge.verify_code = verify_code
            existing_judge.tg_chat_id = message.chat.id
            await existing_judge.save()
            await state.set_state(MainStates.blank)
    else:
        await message.answer("Игрок/судья не найден, попробуйте еще или обратитесь к организатору")


async def enter_verify_code_for_authentication_player(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    nickname = data["nickname"]
    await state.update_data({})
    existing_player_with_code = await Player.get_or_none(nickname=nickname, verify_code=message.text)
    if existing_player_with_code:
        await message.answer(f"Вы успешно авторизованы. Ждите уведомлений")
        await state.set_state(MainStates.blank)
    else:
        await message.answer(f"Неверный код")


async def enter_verify_code_for_authentication_judge(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    nickname = data["nickname"]
    await state.set_data({})
    existing_judge_with_code = await Judge.get_or_none(judge_name=nickname, verify_code=message.text)
    if existing_judge_with_code:
        await message.answer(f"Вы успешно авторизованы и можете отправлять результаты игр, "
                             f"инструкцию расскажет организатор или введите команду /help")
        await state.set_state(MainStates.blank)
    else:
        await message.answer(f"Неверный код")


async def blank_handler(message: Message, bot: Bot, state: FSMContext):
    return
