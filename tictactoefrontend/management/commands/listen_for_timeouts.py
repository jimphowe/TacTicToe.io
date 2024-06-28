from datetime import datetime
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
import redis

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from tictactoefrontend.models import Game

class Command(BaseCommand):
    help = 'Listens for Redis Pub/Sub messages on key expirations'

    def handle(self, *args, **options):
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.config_set('notify-keyspace-events', 'Ex')
        pubsub = redis_client.pubsub()

        # Subscribe to key expiration events
        pubsub.psubscribe('__keyevent@0__:expired')

        print("Listening for events...")
        for message in pubsub.listen():
            if message['type'] == 'pmessage':
                data = message['data']
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                # Process the expiration event
                if 'game' in data:
                    self.process_expiration(data)
    
    def process_expiration(self, key):
        print(f"Processing expiration for key: {key}")
        # Your custom logic here, for example:
        game_id = key.split(':')[1]
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.delete(key)

        game = get_object_or_404(Game, pk=game_id)

        winner = game.player_two if game.turn == game.player_one else game.player_one
        loser = game.player_one if game.turn == game.player_one else game.player_two
        if loser == game.player_one:
            game.player_one_time_left = 0
        else:
            game.player_two_time_left = 0

        game.completed = True
        game.completed_at = datetime.now()
        game.winner = winner
        game.elo_change = self.update_elo_ratings(game.player_one, game.player_two, game.turn)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game.id}',  # Use the same group name as in your consumer
            {
                'type': 'send_game_update',
                'game_state': game.game_state,
                'winner': winner.id,
                'winner_name': winner.username,
                'elo_change': game.elo_change,
                'turn': game.turn.id
            }
        )

        game.save()

    def update_elo_ratings(self, player_one, player_two, winner):
        p1_profile = player_one.profile
        p2_profile = player_two.profile
        average_elo = (p2_profile.elo_rating + p1_profile.elo_rating) / 2
        k_factor = self.calculate_k_factor(average_elo)

        # Calculate expected scores
        expected_p1 = 1 / (1 + 10 ** ((p2_profile.elo_rating - p1_profile.elo_rating) / 400))
        expected_p2 = 1 - expected_p1

        # Calculate Elo changes
        elo_change_p1 = round(k_factor * (1 - expected_p1) if winner == player_one else -k_factor * expected_p1, 0)
        elo_change_p2 = round(k_factor * (1 - expected_p2) if winner == player_two else -k_factor * expected_p2, 0)

        # Update ratings
        p1_profile.elo_rating += elo_change_p1
        p2_profile.elo_rating += elo_change_p2

        # Save the updated profiles
        p1_profile.save()
        p2_profile.save()

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
