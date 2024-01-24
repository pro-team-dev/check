from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import TravelAgency, Tour
from django.http import HttpResponse
from rest_framework.response import Response
from .serializers import TravelAgencySerializer
from rest_framework import viewsets
from rest_framework import status
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




from .serializers import TravelAgencySerializer, TourSerializer

class TravelAgencyViewSet(viewsets.ModelViewSet):
            queryset = TravelAgency.objects.all()
            serializer_class = TravelAgencySerializer

class TourViewSet(viewsets.ModelViewSet):
            queryset = Tour.objects.all()
            serializer_class = TourSerializer
            permission_classes = [IsAuthenticated]

            def post(self, request, **kwargs):
                user = request.user

                if user.is_guide:
                    return Response({'status': 'error', 'message': 'Only tourists can submit tour details'}, status=status.HTTP_403_FORBIDDEN)

                if request.method == 'POST':
                    try:
                        tour_data = json.loads(request.body.decode('utf-8'))

                        # Extracting values for Tour model
                        title = tour_data.get('title', '')
                        description = tour_data.get('description', '')
                        price = tour_data.get('price', 0.00)
                        duration_days = tour_data.get('duration_days', 1)
                        start_date = tour_data.get('start_date', None)
                        end_date = tour_data.get('end_date', None)
                        status = tour_data.get('status', 'pending')  # Assuming a default status

                        # Create a new tour instance
                        tour = Tour.objects.create(
                            title=title,
                            description=description,
                            price=price,
                            duration_days=duration_days,
                            start_date=start_date,
                            end_date=end_date,
                            status=status,
                            travelagency=user.travelagency,
                        )

                        # Broadcast the tour details to connected guides via WebSocket
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f'guide_{tour_data["location"]}',  # Group name for guides
                            {
                                'type': 'send_tour_details',
                                'tour_data': tour_data,
                            },
                        )

                        return Response({'status': 'success', 'tour_id': tour.id}, status=status.HTTP_200_OK)
                    except json.JSONDecodeError:
                        return Response({'status': 'error', 'message': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


        