import json
from channels.generic.websocket import AsyncWebsocketConsumer
from goal.models import User
from asgiref.sync import sync_to_async

class UsernameCheckConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        username = data.get('username', '')

        if username:
            username_exists = await self.check_username(username)

            response_data = {
                'type': 'username_check',
                'username': username,
                'exists': username_exists,
            }

            await self.send_response(response_data)
        else:
            response_data = {
                'type': 'username_check',
                'message': 'Invalid data received.',
            }

            await self.send_response(response_data)

    async def send_response(self, data):
        await self.send(text_data=json.dumps(data))

    @sync_to_async
    def check_username(self,username):
        return User.objects.filter(username=username).exists()