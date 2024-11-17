import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from tortoise import Tortoise
from config import TOKEN
# from database.connection import drop_models
from database.db_settings import TORTOISE_ORM
from handlers.admins_handlers import create_tournament_admin, enter_tournament_url, close_tournament_admin, \
    clear_tournament_from_db, regenerate_verify_code_request, regenerate_verify_code_response, help_command
from handlers.basic import *
from handlers.auth_handlers import *
from handlers.judges_handlers import *
from parser.utils import TournamentDbSaver


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    await Tortoise.init(config=TORTOISE_ORM)
    await TournamentDbSaver.clear_tables()
    await Tortoise.generate_schemas()

    dp.message.register(start, Command('start'))
    dp.message.register(create_tournament_admin, Command("create_tournament"))
    dp.message.register(close_tournament_admin, Command("close_tournament"))
    dp.message.register(regenerate_verify_code_request, Command('regenerate_verify_code'))
    dp.message.register(enter_game_number_judges, Command("enter_game_result"))
    dp.message.register(help_command, Command("help"))

    dp.message.register(regenerate_verify_code_response, MainStates.enter_nickname_for_regenerate_verify_code)
    dp.message.register(blank_handler, MainStates.blank)

    dp.message.register(enter_nickname_for_registration, MainStates.enter_nickname)
    dp.message.register(enter_verify_code_for_authentication_player, MainStates.enter_verify_code_player)
    dp.message.register(enter_verify_code_for_authentication_judge, MainStates.enter_verify_code_judge)

    dp.message.register(enter_game_points_judges, MainStates.enter_game_number)
    dp.message.register(send_points_to_players, MainStates.enter_game_points)

    dp.message.register(enter_tournament_url, MainStates.enter_tournament_url)
    dp.message.register(clear_tournament_from_db, MainStates.close_tournament_url)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
