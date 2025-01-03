from datetime import datetime
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
import redis
import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from tactictoe.models import Game, Piece, Board
from tactictoe.elo_utils import update_elo_ratings

from django.conf import settings

class Command(BaseCommand):
    help = 'Listens for Redis Pub/Sub messages on key expirations'

    def handle(self, *args, **options):
        redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)
        
        pubsub = redis_client.pubsub()

        # Subscribe to key expiration events
        pubsub.psubscribe('__keyevent@0__:expired')

        print("Listening for events...")
        for message in pubsub.listen():
            if message['type'] == 'pmessage':
                data = message['data']
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                if 'game' in data:
                    self.process_expiration(data)

    def process_expiration(self, key):
        print(f"Processing expiration for key: {key}")
        game_code = key.split(':')[1]
        redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)

        game = get_object_or_404(Game, game_code=game_code)

        if game.completed:
            redis_client.delete(key)
            return
        
        board = Board()
        board.setState(json.loads(game.game_state))
        is_tie = board.isTie()

        winner = None
        winner_color = None

        if not is_tie:
            winner = game.player_two if game.turn == game.player_one else game.player_one
            winner_color = Piece.BLUE if game.turn == game.player_one else Piece.RED
            game.winner = winner
        
        if winner == game.player_one:
            game.player_two_time_left = '0 second'
        elif winner == game.player_two:
            game.player_one_time_left = '0 second'

        game.completed = True
        game.completed_at = datetime.now()

        game.elo_change = update_elo_ratings(game.game_type, game.player_one, game.player_two, winner)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game.game_code}',
            {
                'type': 'send_game_update',
                'game_state': game.game_state,
                'winner_id': winner.id,
                'winner_color': winner_color.value,
                'winning_run': None,
                'winner_name': winner.username,
                'is_tie': is_tie,
                'elo_change': game.elo_change,
                'turn': game.turn.id,
                'red_power': game.red_power,
                'blue_power': game.blue_power
            }
        )

        game.save()
