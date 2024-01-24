from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import TravelAgency, Tour
from django.http import HttpResponse
from .serializers import TravelAgencySerializer
from rest_framework import viewsets



from .serializers import TravelAgencySerializer, TourSerializer

class TravelAgencyViewSet(viewsets.ModelViewSet):
            queryset = TravelAgency.objects.all()
            serializer_class = TravelAgencySerializer

class TourViewSet(viewsets.ModelViewSet):
            queryset = Tour.objects.all()
            serializer_class = TourSerializer
