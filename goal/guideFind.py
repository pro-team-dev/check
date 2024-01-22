# consumers.py

from channels.generic.websocket import WebsocketConsumer
import json

class GuideRequestConsumer(WebsocketConsumer):
    def connect(self):
        self.location = self.scope['url_route']['kwargs']['location']
        self.channel_layer.group_add(self.location, self.channel_name)
        self.accept()

        # Store the WebSocket channel name in the Guide model
        guide = self.scope['user'].guide
        guide.channel_name = self.channel_name
        guide.save()

    def disconnect(self, close_code):
        # Remove the channel from the group when disconnected
        self.channel_layer.group_discard(self.location, self.channel_name)
        # Remove the WebSocket channel name from the Guide model
        guide = self.scope['user'].guide
        guide.channel_name = None
        guide.save()

    # Other methods...
