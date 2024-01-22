# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from goal.models import Tour



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

    async def send_tour_details(self, tour_data):
        await self.send(text_data=json.dumps(tour_data))


class TourConnection(AsyncWebsocketConsumer):
    async def connect(self):
        #implement auth
        # self.user = self.scope["user"]

        #temporary getting from path
        self.user = self.scope['url_route']['kwargs']['user']

        print(self.user)
        self.room_group_name = f'tour_{self.user}'
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
    
    async def update(self,tour_data):
        await self.send(text_data=json.dumps(tour_data))
