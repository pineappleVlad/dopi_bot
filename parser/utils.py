from urllib.parse import urlparse, parse_qs, urlencode

import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
from tortoise import Tortoise

from database.models import Player, Judge, Tournament, Game, GamePlayer
import pprint


class TournamentDbSaver:
    @staticmethod
    async def save_seating_to_db(url: str):
        url = await TournamentDbSaver.format_url(url)
        tournament_list, tournament_name = await TournamentDbSaver._parse_url(url)
        tournament = await Tournament.get_or_none(tournament_name=tournament_name)
        if tournament is None:
            tournament = await Tournament.create(tournament_name=tournament_name, url=url)
            await tournament.save()
        for current_tour in tournament_list:
            current_tour_num = 1
            for game in current_tour:
                existed_judge = await Judge.get_or_none(judge_name=game['referee'])
                if existed_judge is None:
                    existed_judge = await Judge.create(judge_name=game['referee'])
                    await existed_judge.save()
                saved_game = await Game.create(game_num=current_tour_num, judge=existed_judge,
                                               tournament=tournament)
                await saved_game.save()
                slot_counter = 1
                for player in game["players"]:
                    saved_player = await Player.get_or_none(nickname=player)
                    if saved_player is None:
                        saved_player = await Player.create(nickname=player)
                        await saved_player.save()
                    saved_game_in_between_tables = await GamePlayer.create(game=saved_game, player=saved_player,
                                                                           player_slot=slot_counter)
                    await saved_game_in_between_tables.save()
                    slot_counter += 1
            current_tour_num += 1

    @staticmethod
    async def _get_headers() -> dict:
        headers = Headers(browser='chrome', os='win')
        return headers.generate()

    @staticmethod
    async def _get_request(url: str):
        headers = await TournamentDbSaver._get_headers()
        response = requests.get(url, headers=headers)
        return response.text

    @staticmethod
    async def _parse_url(url: str):
        response = await TournamentDbSaver._get_request(url)
        soup = BeautifulSoup(response, 'html.parser')
        nicknames_list = soup.find_all('div', class_='d-flex')[1:]
        result_list = await TournamentDbSaver._format_data(nicknames_list)
        tournament_name = soup.find('div', class_='_tid__tournament__top-left-title__kWFFR').text
        return result_list, tournament_name

    @staticmethod
    async def format_url(url: str) -> str:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'tab' not in query_params:
            new_query = urlencode({**query_params, 'tab': 'games'})
            new_url = parsed_url._replace(query=new_query)
            return new_url.geturl()
        return url

    @staticmethod
    async def _format_data(nicknames: list) -> list:
        result = []
        current_tour = []
        game = {}
        players = []
        current_game_number = 1
        for nickname in nicknames:
            if 'Стол ' in nickname.text:
                table_split = nickname.text.split(', ')
                referee = table_split[-1]
                current_table = table_split[0].split(' ')[-1]
                game["table_number"] = current_table
                game["game_number"] = current_game_number

                if current_table == "1":
                    if len(current_tour) > 0:
                        result.append(current_tour)
                        current_tour = []
                        current_game_number += 1

                if players:
                    game['players'] = players

                game['referee'] = referee
            else:
                players.append(nickname.text)

            if 'referee' in game and len(players) == 10:
                game['players'] = players
                current_tour.append(game)
                game = {}
                players = []
        if current_tour:
            result.append(current_tour)

        return result

    @staticmethod
    async def clear_tables():
        await Player.all().delete()
        await Judge.all().delete()
        await Tournament.all().delete()
        await Game.all().delete()
        await GamePlayer.all().delete()

