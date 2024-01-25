import base64
from django.db import models

class TravelAgency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    contact_num = models.BigIntegerField(unique=True)
    website = models.URLField()

    # New field for profile as base64 encoded text
    profile = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'

class Tour(models.Model):
    TOUR_TYPE_CHOICES = [
        ('hiking', 'Hiking'),
        ('trekking', 'Trekking'),
        ('nature', 'Nature Tour'),
        ('beach', 'Beach Vacation'),
        ('city', 'City Exploration'),
        ('cultural', 'Cultural Experience'),
        ('wildlife', 'Wildlife Safari'),
        ('cruise', 'Cruise Adventure'),
        # Add other relevant tour types as needed
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    tour_type = models.CharField(max_length=10, choices=TOUR_TYPE_CHOICES)
    travelagency = models.ForeignKey('TravelAgency', on_delete=models.CASCADE)
    gallery = models.ManyToManyField('Gallery', related_name='tours', blank=True)

    def __str__(self):
        return f'{self.title}'


class Gallery(models.Model):
    id = models.AutoField(primary_key=True)
    # Storing image as base64 encoded text
    image = models.TextField()

    def __str__(self):
        return f'Gallery {self.id}'

    def save(self, *args, **kwargs):
        # If image is not already a base64 string, encode it
        if self.image and not self.image.startswith('data:'):
            with open(self.image, 'rb') as image_file:
                self.image = 'data:image/png;base64,' + base64.b64encode(image_file.read()).decode('utf-8')

        # If image is a base64 string, create ContentFile
        if isinstance(self.image, str):
            format, imgstr = self.image.split(';base64,')  # assuming 'data:image/png;base64,'
            ext = format.split('/')[-1]  # assuming 'image/png'
            self.image = ContentFile(base64.b64decode(imgstr), name=f'gallery_image.{ext}')

        # Ensure that the image attribute is set before saving
        if not self.image:
            raise ValueError("Image attribute cannot be None")

        super().save(*args, **kwargs)