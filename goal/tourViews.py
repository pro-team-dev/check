from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from goal.serializers import UserRegistrationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync,sync_to_async
import json
from rest_framework.permissions import IsAuthenticated
from goal.models import Tour


class SubmitTourDetailsView(APIView):
    permission_classes = [IsAuthenticated]
  
    def post(self, request, **kwargs):
        user = request.user

        if user.is_guide:
            return Response({'status': 'error', 'message': 'Only tourists can submit tour details'}, status=status.HTTP_403_FORBIDDEN)
        if request.method == 'POST':
            try:
                tour_data = json.loads(request.body.decode('utf-8'))
                # Broadcast the tour details to connected guides via WebSocket
                tour_id = Tour.save_tour_details(
                    location=tour_data['location'],
                    status='pending',  # You can set the initial status
                    tourist=user,
                )
                channel_layer = get_channel_layer()
                print(tour_id)
                tour_data["id"]=tour_id
                async_to_sync(channel_layer.group_send)(
                    f'guide_{tour_data["location"]}',  # Group name for guides
                    {
                        'type': 'send_tour_details',
                        'tour_data': tour_data,
                    },
                )
               
                return Response({'status': 'success',
                                 "tour_id":tour_id}, status=status.HTTP_200_OK)
            except json.JSONDecodeError:
                return Response({'status': 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    
    
class AcceptTourOfferView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            # Assuming you have a tour ID in the request data
            tour_id = request.data.get('tour_id')
            
            # Update the status of the tour to 'ongoing' when accepted
            tour = Tour.objects.get(tour_id=tour_id)
            tour.status = 'ongoing'
            tour.save()

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Tour.DoesNotExist:
            return Response({'status': 'error', 'message': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)