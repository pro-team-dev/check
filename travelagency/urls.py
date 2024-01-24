
from rest_framework.routers import DefaultRouter
from .views import TravelAgencyViewSet, TourViewSet

router = DefaultRouter()
router.register(r'agencies', TravelAgencyViewSet)
router.register(r'tours', TourViewSet)

urlpatterns = router.urls