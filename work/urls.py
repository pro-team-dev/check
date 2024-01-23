
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('goal.urls')),
    path('travel/', include('travelagency.urls'))
]
