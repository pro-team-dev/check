from django.urls import path
from goal.views import SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserPasswordResetView,UserProfileViewFromID
from goal.tourViews import SubmitTourDetailsView,AcceptTourOfferViewGuide,AcceptTourOfferViewTourist,TourComplete,cancelTour,GetAllOffers,PendingTourUserView,TourDetailView,ongoingTour

from goal.webSock.findGuide import TouristConnection,GuideConnection
from goal.webSock.utils import UsernameCheckConsumer

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/<int:id>/', UserProfileViewFromID.as_view(), name='profile_from_id'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),

    path('new-tour/', SubmitTourDetailsView.as_view(), name='new-tour'),
    path('accept-tour-guide/', AcceptTourOfferViewGuide.as_view(), name='guide-accept-offer'),
    path('accept-tour-tourist/', AcceptTourOfferViewTourist.as_view(), name='tourist-accept-offer'),
    path('complete-tour/', TourComplete.as_view(), name='TourComplete'),
    path('cancel-tour/', cancelTour.as_view(), name='cancelTour'),
    path('get-all-offers/', GetAllOffers.as_view(), name='get_all_offers'),
    path('pending-tours/', PendingTourUserView.as_view(), name='pending_tour_user_list'),
    path('ongoing-tours/', ongoingTour.as_view(), name='ongoing_tour'),
    path('tour/<int:tour_id>/', TourDetailView.as_view(), name='tour_detail'),

]

websocket_url=[
    path("ws/tourist-tour/<str:user>", TouristConnection.as_asgi()),
    path("ws/guide-tour/<str:user>", GuideConnection.as_asgi()),
    path('ws/check-username/',  UsernameCheckConsumer.as_asgi()),



]