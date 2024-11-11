from tortoise.models import Model
from tortoise import fields


class Player(Model):
    id = fields.BigIntField(pk=True)
    verify_code = fields.CharField(max_length=4, null=True)
    tg_chat_id = fields.BigIntField(null=True)
    nickname = fields.CharField(max_length=85, unique=True)

    class Meta:
        table = 'players'


class Judge(Model):
    id = fields.BigIntField(pk=True)
    tg_chat_id = fields.BigIntField(null=True)
    judge_name = fields.CharField(max_length=85, unique=True)
    verify_code = fields.CharField(max_length=4, null=True)
    games = fields.ReverseRelation['Game']

    class Meta:
        table = 'judges'


class Tournament(Model):
    id = fields.BigIntField(pk=True)
    tournament_name = fields.CharField(max_length=255)
    url = fields.CharField(max_length=255)
    games = fields.ReverseRelation['Game']

    class Meta:
        table = 'tournaments'


class Game(Model):
    id = fields.BigIntField(pk=True)
    game_num = fields.IntField()
    judge = fields.ForeignKeyField('models.Judge', related_name='games')
    tournament = fields.ForeignKeyField('models.Tournament', related_name='games')

    class Meta:
        table = 'games'


class GamePlayer(Model):
    game = fields.ForeignKeyField('models.Game', related_name='game_players')
    player = fields.ForeignKeyField('models.Player', related_name='game_players')
    player_slot = fields.IntField()

    class Meta:
        table = 'games_players'
