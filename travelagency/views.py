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
    serializer_class = TourSerializer

    def get_queryset(self):
        # Retrieve the type of tour and agency name from the query parameters
        tour_type = self.request.query_params.get('type', None)
        agency_name = self.request.query_params.get('agency', None)

        # Start with all tours
        queryset = Tour.objects.all()

        # Filter by tour type if provided
        if tour_type:
            queryset = queryset.filter(type=tour_type)

        # Filter by agency name if provided
        if agency_name:
            queryset = queryset.filter(agency__name=agency_name)

        # Order the tours, you can customize this based on your needs
        queryset = queryset.order_by('name')  # Sorting by tour name for example

        return queryset
    
class AddTour(APIView):
    def post(self, request):
        serializer = TourSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)