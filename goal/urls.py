from django.urls import path
from goal.views import SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserPasswordResetView, GuideUserLoginView,GuideUserProfileView,GuideUserRegistrationView
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('guide/register/', GuideUserRegistrationView.as_view(), name='guide-register'),
    path('guide/login/', GuideUserLoginView.as_view(), name='guide-login'),
    path('guide/profile/', GuideUserProfileView.as_view(), name='guide-profile'),

]