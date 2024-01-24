from rest_framework.views import APIView
from rest_framework.response import Response
from .models import TravelAgency, Tour
from .serializers import TravelAgencySerializer, TourSerializer
from rest_framework import status

class GetTravelAgencies(APIView):
    def get(self, request):
        agencies = TravelAgency.objects.all()
        serializer = TravelAgencySerializer(agencies, many=True)
        return Response(serializer.data)

class AddTravelAgency(APIView):
    def post(self, request):
        serializer = TravelAgencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetTours(APIView):
    def get(self, request):
        tours = Tour.objects.all()
        serializer = TourSerializer(tours, many=True)
        return Response(serializer.data)
    
class AddTour(APIView):
    def post(self, request):
        serializer = TourSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)