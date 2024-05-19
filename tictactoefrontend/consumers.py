import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Game
from asgiref.sync import sync_to_async

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'

        # Join game group
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave game group
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        position = data['position']
        player_id = data['player_id']

        # Process the move (this should be done synchronously in the database)
        response = await self.process_move(position, player_id)

        # Send the new game state to all players in the game group
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'send_game_update',
                'game_state': response['game_state'],
                'winner': response['winner']
            }
        )

    async def send_game_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'game_state': event['game_state'],
            'winner': event['winner']
        }))

    @sync_to_async
    def process_move(self, position, player_id):
        # Retrieve the game and update its state
        game = Game.objects.get(pk=self.game_id)
        # Assuming there's a method to handle the move and determine if there's a winner
        game_state, winner = game.make_move(position, player_id)
        game.save()
        return {'game_state': game_state, 'winner': winner}
