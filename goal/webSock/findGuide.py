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
        # This method is called when the server receives a message from the WebSocket.
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')

        if message_type == 'send_tour_details':
            # Handle the 'send_tour_details' message type
            tour_data = text_data_json.get('tour_data', {})
            # Perform any necessary processing or broadcasting here
            await self.send_tour_details(tour_data)
        else:
            print(f"Unhandled message type: {message_type}")

    async def send_tour_details(self, tour_data):
        # Handle the 'send_tour_details' message type
        # Perform any necessary processing or broadcasting here
        await self.send(text_data=json.dumps({'type': 'tour_details_received', 'message': 'Tour details received'}))

    async def guide_request(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': event['message']}))
