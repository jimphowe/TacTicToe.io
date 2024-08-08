import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #import ipdb; ipdb.set_trace()
        self.game_code = self.scope['url_route']['kwargs']['game_code']
        self.game_group_name = f'game_{self.game_code}'

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
        user = self.scope["user"]
        winner_name = None if winner == None else user.username
        elo_change = data['elo_change']
        turn = data['turn']

        # Send the new game state to all players in the game group
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'send_game_update',
                'game_state': game_state,
                'winner': winner,
                'winner_name': winner_name,
                'elo_change': elo_change,
                'turn': turn
            }
        )

    async def send_game_update(self, event):
        # Send message to WebSocket
        elo_change = None
        winner = event['winner']
        user = self.scope['user']
        winner_name = event['winner_name']
        turn = event['turn']
        if winner:
            is_winner = str(user.id) == str(winner)
            elo_change = event['elo_change'] if is_winner else -1 * int(event['elo_change'])

        await self.send(text_data=json.dumps({
            'game_state': event['game_state'],
            'winner': winner,
            'winner_name': winner_name,
            'elo_change': elo_change,
            'turn': turn
        }))


class SetupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'setup_room'

        # Join the setup room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the setup room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Optionally handle incoming data if necessary

    async def send_game_ready(self, event):
        # Send message to WebSocket to update the client
        await self.send(text_data=json.dumps({
            'status': 'success',
            'game_code': event['game_code']
        }))

