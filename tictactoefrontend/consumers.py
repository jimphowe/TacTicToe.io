import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #import ipdb; ipdb.set_trace()
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
        #import ipdb; ipdb.set_trace()
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        #import ipdb; ipdb.set_trace()
        data = json.loads(text_data)
        game_state = data['game_state']
        winner = data['winner']

        # Send the new game state to all players in the game group
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'send_game_update',
                'game_state': game_state,
                'winner': winner
            }
        )

    async def send_game_update(self, event):
        #import ipdb; ipdb.set_trace()
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'game_state': event['game_state'],
            'winner': event['winner']
        }))
