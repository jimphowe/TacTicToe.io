from datetime import datetime
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
import redis

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from tactictoe.models import EloRating, Game, Piece

from django.db import transaction
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

        winner = game.player_two if game.turn == game.player_one else game.player_one
        loser = game.player_one if game.turn == game.player_one else game.player_two
        winner_color = Piece.BLUE if game.turn == game.player_one else Piece.RED
        if loser == game.player_one:
            game.player_one_time_left = '0 second'
        else:
            game.player_two_time_left = '0 second'

        game.completed = True
        game.completed_at = datetime.now()
        game.winner = winner
        game.elo_change = self.update_elo_ratings(game.game_type, game.player_one, game.player_two, game.turn)

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
                'elo_change': game.elo_change,
                'turn': game.turn.id
            }
        )

        game.save()

    def update_elo_ratings(self, game_type, player_one, player_two, winner):
        p1_profile = player_one.profile
        p2_profile = player_two.profile

        # Get or create EloRating objects for both players
        p1_elo, _ = EloRating.objects.get_or_create(user_profile=p1_profile, game_type=game_type)
        p2_elo, _ = EloRating.objects.get_or_create(user_profile=p2_profile, game_type=game_type)

        average_elo = (p1_elo.rating + p2_elo.rating) / 2
        k_factor = self.calculate_k_factor(average_elo)

        # Calculate expected scores
        expected_p1 = 1 / (1 + 10 ** ((p2_elo.rating - p1_elo.rating) / 400))
        expected_p2 = 1 - expected_p1

        # Calculate Elo changes
        elo_change_p1 = round(k_factor * (1 - expected_p1) if winner == player_one else -k_factor * expected_p1, 0)
        elo_change_p2 = round(k_factor * (1 - expected_p2) if winner == player_two else -k_factor * expected_p2, 0)

        # Update ratings
        with transaction.atomic():
            p1_elo.rating += elo_change_p1
            p2_elo.rating += elo_change_p2
            p1_elo.save()
            p2_elo.save()

        return elo_change_p1 if winner == player_one else elo_change_p2
    
    def calculate_k_factor(self, average_elo):
        if average_elo <= 1500:
            return 40
        elif average_elo <= 1800:
            return 30
        elif average_elo <= 2100:
            return 20
        else:
            return 15
