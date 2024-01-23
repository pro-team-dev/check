from django.urls import path
from . import views

urlpatterns = [
   path('',views.fillData, name = "fill"),
   path('all/',views.TravelAgencyList.as_view(),name='agencies-list')  
]