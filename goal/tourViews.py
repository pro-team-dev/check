from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from goal.serializers import UserRegistrationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class SubmitTourDetailsView(APIView):
    def post(self, request, format=None):
        if request.method == 'POST':
            try:
                tour_data = json.loads(request.body.decode('utf-8'))

                # Process the received tour details (e.g., save to database)
                # ...

                # Broadcast the tour details to connected guides via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'guide_{tour_data["location"]}',  # Group name for guides
                    {
                        'type': 'send_tour_details',
                        'tour_data': tour_data,
                    },
                )

                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            except json.JSONDecodeError:
                return Response({'status': 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
