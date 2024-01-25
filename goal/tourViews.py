from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from goal.serializers import UserRegistrationSerializer,OfferSerializer,TourSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync,sync_to_async
import json
from rest_framework.permissions import IsAuthenticated
from goal.models import Tour,User,Offer
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
            guides=user.get_available_guides(location=tour_data["location"],language=tour_data["language"])
            tour_data.pop("language")
            tour_id = Tour.save_tour_details(
                status='pending',  
                tourist=user,
                **tour_data
            )
            
            channel_layer = get_channel_layer()
            tour_data["id"]=tour_id
            for guide in guides:
                async_to_sync(channel_layer.group_send)(
                    f'tour_{guide}',  # Group name for guides
                    {
                        'type': 'new_tour',
                        'tour_data': tour_data,
                        'tourist':user.id
                    },
                )
                guide=User.objects.get(id=guide)
                guide.tours.add(tour_id)
                user.tours.add(tour_id)
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
            offer = Offer.objects.create(
                tour=tour,
                guide=user,
                tourist=tour.tourist,
                price=price,
                duration=time_duation
            )
            offer.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                    f'tour_{tour.tourist}',  # Group name for guides
                    {
                        'type': 'update',
                        'tour_data': {
                            'tour_id': tour.tour_id,
                            'offer_id':offer.id,
                            'guide_id': offer.guide.id,
                            'price': str(offer.price), 
                            'duration':time_duation
                        },
                    },
                )
            tour.offer.add(offer)
            user.tours.add(tour)
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
            Offer_id=request.data.get("offer_id")
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
        
        
class GetAllOffers(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            tour_id = request.data.get("tour_id")
            tour = get_object_or_404(Tour, tour_id=tour_id)
            

            offers = tour.offers.all()
            serializer = OfferSerializer(offers, many=True)

            return Response({'status': 'success', 'offers': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class PendingTourUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        tours = user.tours.filter(status="pending")
        serializer = TourSerializer(tours, many=True)
        if user.is_guide == False:
            return Response({'status': 'success', 'pending_tours': serializer.data}, status=status.HTTP_200_OK)
        else:
            response_data = {
                'accepted': [],
                'not-accepted': []
            }
            for tour_data in serializer.data:
                print(tour_data['tour_id'],"\n\n\n")
                tour = Tour.objects.get(tour_id=tour_data['tour_id'])
                offers = tour.offers.all()  
                print(offers)
                if offers:
                    for offer in offers:
                        if offer.guide == user:
                            response_data['accepted'].append(tour_data)
                else:
                    response_data['not-accepted'].append(tour_data)

            return Response({'status': 'success', 'pending_tours': response_data}, status=status.HTTP_200_OK)

    



class TourDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, tour_id, *args, **kwargs):
        tour = get_object_or_404(Tour, tour_id=tour_id)
        serializer = TourSerializer(tour)
        return Response({'status': 'success', 'tour': serializer.data}, status=status.HTTP_200_OK)

        