from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import json

class CustomUserManager(BaseUserManager):

    def create_user(self, email, name, password=None, is_guide=False, **extra_fields):
        user = self.model(email=email, name=name, is_guide=is_guide, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, is_guide=False, **extra_fields):
        user = self.create_user(email, name, password, is_guide, **extra_fields)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    profile = models.TextField(null=True, blank=True)  # Base64-encoded profile image
    citizenship = models.CharField(max_length=200, null=True, blank=True)
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_guide = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    languages_json = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    objects = CustomUserManager()
    ongoing_tour = models.ForeignKey(
        'Tour',
        on_delete=models.SET_NULL,
        related_name='ongoing_tours',
        null=True,
        blank=True
    )
    tours = models.ManyToManyField('Tour', related_name='tours', blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']

    def __str__(self):
        return str(self.id)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def languages(self):
        return json.loads(self.languages_json) if self.languages_json else []

    @languages.setter
    def languages(self, value):
        self.languages_json = json.dumps(value)

    @property
    def is_staff(self):
        return self.is_admin

    def save_base64_profile_image(self, base64_encoded_image):
        self.profile = base64_encoded_image
        self.save()

    def get_base64_profile_image(self):
        return self.profile
    
    @classmethod
    def get_available_guides(cls, language=None, location=None):
        # Get all users with is_guide=True
        guides = cls.objects.filter(is_guide=True,location=location.lower(),ongoing_tour__isnull=True)

        guide_ids = list(guides.values_list('id', flat=True))

        return guide_ids
    
    
class Tour(models.Model):
    TOUR_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    tour_id = models.AutoField(primary_key=True)
    locations = models.JSONField(null=True)
    location = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TOUR_STATUS_CHOICES, default='pending')
    tourist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_tours')
    guide = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guided_tours', null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    duration = models.DurationField(null=True)
    no_of_people = models.IntegerField(null=True)
    travel_coverage = models.BooleanField(default=False)
    food_coverage = models.BooleanField(default=False)
    personal_request = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offer = models.ManyToManyField('Offer', related_name='tour_offers')
    
    @classmethod
    def save_tour_details(cls, locations,location, status, tourist, price=None, duration=None, no_of_people=None, travel_coverage=False, food_coverage=False, personal_request=None):
        
        console.log(duration)
        tour = cls.objects.create(
            locations=locations,
            location=location,
            status=status,
            tourist=tourist,
            guide=None,  # You might want to set the guide based on your business logic
            price=price,
            duration=duration,
            no_of_people=no_of_people,
            travel_coverage=travel_coverage,
            food_coverage=food_coverage,
            personal_request=personal_request,
        )
        return tour.tour_id

    def __str__(self):
        return f"Tour {self.tour_id} - {self.locations}"
    
class Offer(models.Model):
    id = models.AutoField(primary_key=True)
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name='offers')
    guide = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_offers')
    tourist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_offers')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField(null=True)

    def __str__(self):
        return f"Offer {self.id} - Tour {self.tour_id} - Guide {self.guide_id} - Tourist {self.tourist_id}"