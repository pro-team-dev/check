from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import TravelAgency,ContactNumber
from django.http import HttpResponse
from travelagency.serializers import TravelAgencySerializer
from rest_framework.response import Response

# Create your views here.

class TravelAgencyList(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        agencies = TravelAgency.objects.all()
        serializer = TravelAgencySerializer(agencies,many=True)
        return Response(serializer.data)
    
def fillData(request):
        try:
            # Assuming request.POST contains data in the format "contact_num=123&travelagency_id=1"
            contact_num = request.POST.get('contact_num')
            travelagency_id = request.POST.get('travelagency_id')

            # Assuming you have a TravelAgency object with the specified ID
            agency, created = TravelAgency.objects.get(pk=travelagency_id)

            # Create ContactNumber object and save it to the database
            ContactNumber.objects.create(contact_num=contact_num, travelagency=agency)
            if created:
                  return HttpResponse('TravelAgency created and data stored in SQLite successfully')
            else:
                return HttpResponse('Data stored in SQLite successfully')
        except Exception as e:
            return HttpResponse(f'Error storing data: {str(e)}', status=500)
