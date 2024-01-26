from rest_framework.views import APIView
from rest_framework.response import Response
from .models import TravelAgency, Tour, Gallery
from .serializers import TravelAgencySerializer, TourSerializer,GallerySerializer
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
    serializer_class = TourSerializer

    def get(self, request):
        tours = self.get_queryset()
        serializer = TourSerializer(tours, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        # Retrieve the type of tour, agency name, and tour id from the query parameters
        tour_type = self.request.query_params.get('type', None)
        agency_name = self.request.query_params.get('agency', None)
        tour_id = self.request.query_params.get('id', None)

        # Start with all tours
        queryset = Tour.objects.all()

        # Filter by tour type if provided
        if tour_type:
            queryset = queryset.filter(tour_type=tour_type)

        # Filter by agency name if provided
        if agency_name:
            queryset = queryset.filter(travelagency__name=agency_name)

        # Filter by tour id if provided
        if tour_id:
            queryset = queryset.filter(id=tour_id)

        # Order the tours, you can customize this based on your needs
        queryset = queryset.order_by('title')

        return queryset

class AddTour(APIView):
    def post(self, request):
        serializer = TourSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetGallery(APIView):
    def get(self, request, gallery_id):
        try:
            gallery = Gallery.objects.get(pk=gallery_id)
        except Gallery.DoesNotExist:
            return Response({'error': 'Gallery not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = GallerySerializer(gallery)
        return Response(serializer.data)
