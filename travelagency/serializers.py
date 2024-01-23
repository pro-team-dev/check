from rest_framework import serializers 
from .models import TravelAgency, ContactNumber

class TravelAgencySerializer(serializers.ModelSerializer):
    call = serializers.StringRelatedField(many=True)
    class Meta:
        model = TravelAgency
        fields = ['name','address','price','call']
        