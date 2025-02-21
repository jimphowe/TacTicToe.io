import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
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
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        game_state = data['game_state']
        winner_id = data['winner_id']
        winner_color = data['winner_color']
        winning_run = data['winning_run']
        user = self.scope["user"]
        winner_name = None if winner_id == None else user.username
        is_tie = data['is_tie']
        elo_change = data['elo_change']
        turn = data['turn']
        red_power = data['red_power']
        blue_power = data['blue_power']
        push_info = data['push_info']

        # Send the new game state to all players in the game group
        await self.channel_layer.group_send(
            self.game_group_name,
            {
                'type': 'send_game_update',
                'game_state': game_state,
                'winner_id': winner_id,
                'winner_color': winner_color,
                'winning_run': winning_run,
                'winner_name': winner_name,
                'is_tie': is_tie,
                'elo_change': elo_change,
                'turn': turn,
                'red_power': red_power,
                'blue_power': blue_power,
                'push_info': push_info
            }
        )

    async def send_game_update(self, event):
        if event.get('status') == 'cancelled':
            await self.send(text_data=json.dumps({
                'status': 'cancelled',
                'message': event.get('message')
            }))
            return

        elo_change = None
        winner_id = event['winner_id']
        winner_color = event['winner_color']
        winning_run = event['winning_run']
        user = self.scope['user']
        winner_name = event['winner_name']
        turn = event['turn']
        is_tie = event['is_tie']
        red_power = event['red_power']
        blue_power = event['blue_power']

        if winner_id:
            is_winner = str(user.id) == str(winner_id)
            elo_change = event['elo_change'] if is_winner else -1 * int(event['elo_change'])
        else:
            elo_change = event['elo_change']

        await self.send(text_data=json.dumps({
            'game_state': event['game_state'],
            'winner_id': winner_id,
            'winner_color': winner_color,
            'winning_run': winning_run,
            'winner_name': winner_name,
            'elo_change': elo_change,
            'turn': turn,
            'is_tie': is_tie,
            'red_power': red_power,
            'blue_power': blue_power,
            'push_info': event['push_info']
        }))


class SetupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'setup_room'

        # Join the setup room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
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
            'game_code': event.get('game_code'),
            'friend_room_code': event.get('friend_room_code'),
            'message': event.get('message')
        }))

