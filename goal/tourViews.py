from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from goal.serializers import UserRegistrationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync,sync_to_async
import json
from rest_framework.permissions import IsAuthenticated
from goal.models import Tour,User
from django.shortcuts import get_object_or_404
from datetime import timedelta

class SubmitTourDetailsView(APIView):
    permission_classes = [IsAuthenticated]
  
    def post(self, request, **kwargs):
        
        try:
            user = request.user
            if not request.data.get("price"):
                return Response({'status': 'error', 'message': 'Price is Required'}, status=status.HTTP_403_FORBIDDEN)
            if user.is_guide:
                return Response({'status': 'error', 'message': 'Only tourists can submit tour details'}, status=status.HTTP_403_FORBIDDEN)
            tour_data = request.data
            preferred_activity = request.data.get('preferred_activity')  # Assuming you have a field for preferred activity
            tour_data['preferred_activity'] = preferred_activity
            tour_id = Tour.save_tour_details(
                status='pending',  
                tourist=user,
                **tour_data
            )

            channel_layer = get_channel_layer()
            tour_data["id"]=tour_id
            async_to_sync(channel_layer.group_send)(
                f'guide_{tour_data["location"]}',  # Group name for guides
                {
                    'type': 'send_tour_details',
                    'tour_data': tour_data,
                    'tourist':user.id
                },
            )
        
            return Response({'status': 'success',
                            "tour_id":tour_id}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status': 'error', 'message': f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
   

    
    
class AcceptTourOfferViewGuide(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            tour_id = request.data.get('tour_id')
            tour = Tour.objects.get(tour_id=tour_id)
            price=request.data.get('price')

            if not user.is_guide:
                return Response({'status': 'error', 'message': 'Only guides can submit tour details.'}, status=status.HTTP_403_FORBIDDEN)

            if tour.status.lower() != "pending":
                return Response({'status': 'error', 'message': 'Tour details can only be submitted for pending tours.'}, status=status.HTTP_403_FORBIDDEN)
            if not price:
                return Response({'status': 'error', 'message': 'Invalid price'}, status=status.HTTP_400_BAD_REQUEST)
            # Assuming you have a tour ID in the request data
            time_duation= request.data.get('time_duration')
            # Update the status of the tour to 'ongoing' when accepted
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                    f'tour_{tour.tourist}',  # Group name for guides
                    {
                        'type': 'update',
                        'tour_data': {
                            'tour_id': tour.tour_id,
                            'time_duration':time_duation,
                            'price':price,
                            'tourist_id': tour.tourist.id,
                            'guide_id': user.id
                        },
                    },
                )

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Tour.DoesNotExist:
            return Response({'status': 'error', 'message': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'errorr', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AcceptTourOfferViewTourist(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            tour_id = request.data.get('tour_id')
            tour = Tour.objects.get(tour_id=tour_id)
            tour.price=request.data.get('price')
            tour.duration=timedelta(hours=int(request.data.get('duration')))
            if not tour.price or not tour.duration:
                return Response({'status': 'error', 'message': 'Price and duration are required.'}, status=status.HTTP_400_BAD_REQUEST)

            if user.is_guide:
                return Response({'status': 'error', 'message': 'Guides cannot submit tour details.'}, status=status.HTTP_403_FORBIDDEN)
        
            if tour.status.lower() != "pending":
                return Response({'status': 'error', 'message': 'non-pending tours.'}, status=status.HTTP_403_FORBIDDEN)
            
            fixed_guide_id=request.data.get('guide_id')
            # Update the status of the tour to 'ongoing' when accepted
           
            guide=get_object_or_404(User,id=fixed_guide_id)
            tour.guide=guide
            tour.status = 'ongoing'
            tour.save()
            guide.ongoing_tour=tour
            user.ongoing_tour=tour
            guide.save()
            user.save()
            channel_name=f'tour_{fixed_guide_id}'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                    channel_name,  # Group name for guides
                    {
                        'type': 'update',
                        'tour_data': {
                            'tour_id': tour.tour_id,
                            'location': tour.location,
                            'status': tour.status,
                            'tourist_id': tour.tourist.id,
                            'guide_id': tour.guide.id,
                        },
                    },
                )
            
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Tour.DoesNotExist:
            return Response({'status': 'error', 'message': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class TourComplete(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            tour_id = request.data.get('tour_id')
            tour = Tour.objects.get(tour_id=tour_id)
            if not user.is_guide:
                return Response({'status': 'error', 'message': 'Only guides can complete tours.'}, status=status.HTTP_403_FORBIDDEN)

            if tour.status.lower() != "ongoing":
                return Response({'status': 'error', 'message': 'Tour must be in ongoing status to be completed.'}, status=status.HTTP_409_CONFLICT)
            
            
            # Update the status of the tour to 'ongoing' when accepted
            tour.status = 'completed'
            tour.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                    f'tour_{tour.tourist}',  # Group name for guides
                    {
                        'type': 'update',
                        'tour_data': {
                            'tour_id': tour.tour_id,
                            'location': tour.location,
                            'status': tour.status,
                            'tourist_id': tour.tourist.id,
                            'guide_id': tour.guide.id,
                            
                        },
                    },
                )

            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        except Tour.DoesNotExist:
            return Response({'status': 'error', 'message': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class cancelTour(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user = request.user
            tour_id = request.data.get('tour_id')
            tour = Tour.objects.get(tour_id=tour_id)
            if tour.guide == user or tour.tourist == user:
                tour.status = 'cancelled'
                tour.save()
                if tour.guide==user:
                    to=tour.tourist  
                else:
                    to=tour.guide
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                        f'tour_{to}',  # Group name for guides
                        {
                            'type': 'update',
                            'tour_data': {
                                'tour_id': tour.tour_id,
                                'location': tour.location,
                                'status': tour.status,
                                'tourist_id': tour.tourist.id,
                                'guide_id': tour.guide.id,
                                
                            },
                        },
                    )

                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                 return Response({'status': 'error', 'message': 'No tour found'}, status=status.HTTP_404_NOT_FOUND)

            
        except Tour.DoesNotExist:
            return Response({'status': 'error', 'message': 'Tour not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)