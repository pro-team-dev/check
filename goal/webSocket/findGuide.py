# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GuideRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Retrieve location from the WebSocket path
        self.location = self.scope['url_route']['kwargs']['location']
        self.room_group_name = f'guide_{self.location}'

        # Add the consumer to the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remove the consumer from the group when disconnected
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming WebSocket messages
        data = json.loads(text_data)

        # Implement logic to send requests to guides based on the location
        # You may retrieve guides from the database and send requests to them

        # Broadcast the message to all consumers in the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'guide.request',
                'message': 'Guide request sent',
            }
        )

    async def guide_request(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': event['message']}))
