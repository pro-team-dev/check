from django.apps import AppConfig


class GoalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'goal'

# apps.py
from django.apps import AppConfig

class YourAppNameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app_name'  # Replace with the actual name of your app

    def ready(self):
        import goal.tourViews  # Import the signals module
