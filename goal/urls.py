from django.urls import path
from goal.views import SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserPasswordResetView
from goal.tourViews import SubmitTourDetailsView,AcceptTourOfferView,TourComplete,cancelTour
from goal.webSock.findGuide import GuideRequestConsumer,TourConnection
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),

    path('new-tour/', SubmitTourDetailsView.as_view(), name='new-tour'),
    path('accept-tour/', AcceptTourOfferView.as_view(), name='guide-accept-offer'),
    path('complete-tour/', TourComplete.as_view(), name='TourComplete'),
    path('cancel-tour/', cancelTour.as_view(), name='cancelTour'),

]

websocket_url=[
    path("ws/guide_requests/<str:location>", GuideRequestConsumer.as_asgi()),
    path("ws/tour/<str:user>", TourConnection.as_asgi()),

]