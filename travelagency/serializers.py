from rest_framework import serializers 
from .models import TravelAgency, Tour

class TravelAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelAgency
        fields = ['name', 'address', 'contact_num', 'website']

class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['title', 'description', 'price', 'duration_days', 'start_date', 'end_date', 'travelagency']
        