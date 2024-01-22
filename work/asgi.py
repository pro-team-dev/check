# work/routing.py

import os 
  
from channels.auth import AuthMiddlewareStack 
from channels.routing import ProtocolTypeRouter, URLRouter 
from django.core.asgi import get_asgi_application 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "work.settings") 
import goal.urls

application = ProtocolTypeRouter({
    "http": get_asgi_application(), 
    "websocket": URLRouter(goal.urls.websocket_url),
})
