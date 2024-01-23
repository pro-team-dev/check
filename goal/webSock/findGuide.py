# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from goal.models import User,Tour

#if you need to print colourful terminal output
# from colorama import Fore, Style
# print(f"{Fore.GREEN}{tour_id}haha{Fore.WHITE}")

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
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


class TouristConnection(AsyncWebsocketConsumer):
    async def connect(self):
        #implement auth
        # self.user = self.scope["user"]

        #temporary getting from path
        self.user = self.scope['url_route']['kwargs']['user']

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

    async def receive(self, text_data):
        location_data = json.loads(text_data)
        tour_id=location_data.get('tour_id')
        destination = await self.get_associated_user(tour_id)
        destination_group_name = f'tour_{destination}'
        await self.channel_layer.group_send(
            destination_group_name,
            {
                'type': 'send_location',
                'location_data': location_data["location_data"]
            }
        )
    
    async def send_location(self, location_data):
        await self.send(text_data=json.dumps(location_data))
        

    async def update(self,tour_data):
        await self.send(text_data=json.dumps(tour_data))
    
    @sync_to_async
    def get_associated_user(self,tour_id):
        try:

            user=User.objects.get(id=self.user)
            tour= Tour.objects.get(tour_id=tour_id)

            if tour.tourist==user:
                return tour.guide
            else:
                raise ValueError(f"Tour Mis-match")
        except Exception as e:
             return e

class GuideConnection(AsyncWebsocketConsumer):
    
    async def connect(self):
        #implement auth
        # self.user = self.scope["user"]

        #temporary getting from path
        self.user = self.scope['url_route']['kwargs']['user']

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

    async def receive(self, text_data):
        location_data = json.loads(text_data)
        tour_id=location_data.get('tour_id')
        destination = await self.get_associated_user(tour_id)

        destination_group_name = f'tour_{destination}'

        await self.channel_layer.group_send(
            destination_group_name,
            {
                'type': 'send_location',
                'location_data': location_data["location_data"]
            }
        )
    
    async def send_location(self, location_data):
        await self.send(text_data=json.dumps(location_data))
    
    @sync_to_async
    def get_associated_user(self,tour_id):
        try:
            user=User.objects.get(id=self.user)
            tour=Tour.objects.get(tour_id=tour_id)
            if tour.guide==user:
                return tour.tourist
            else:
                raise ValueError(f"Tour Mis-match")
        except Exception as e:
             return e

    async def update(self,tour_data):
        await self.send(text_data=json.dumps(tour_data))
