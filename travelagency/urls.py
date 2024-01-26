from django.urls import path
from .views import GetTravelAgencies, AddTravelAgency, GetTours, AddTour,GetGallery

urlpatterns = [
    path('agencies/', GetTravelAgencies.as_view()),
    path('agencies/add/', AddTravelAgency.as_view()),
    path('tours/', GetTours.as_view()),
    path('tours/add/', AddTour.as_view()),
    path('gallery/<int:gallery_id>/', GetGallery.as_view(), name='get_gallery'),
]