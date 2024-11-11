from aiogram.fsm.state import StatesGroup, State


class MainStates(StatesGroup):
    start = State()

    # Игроки
    enter_nickname = State()
    enter_verify_code_player = State()
    enter_verify_code_judge = State()

    # Админка
    regenerate_verify_code_for_admin = State()
    enter_nickname_for_regenerate_verify_code = State()

    enter_tournament_url = State()
    close_tournament_url = State()

    # Судьи
    enter_game_number = State()
    enter_game_points = State()

    blank = State()
