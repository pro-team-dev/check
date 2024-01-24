from django.db import models

# Create your models here.
class TravelAgency(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    contact_num = models.BigIntegerField(unique=True)
    website = models.URLField()

    def __str__(self):
        return f'{self.name}'

class Tour(models.Model):
    id = models.AutoField(primary_key=True)
    TOUR_TYPE_CHOICES = [
        ('hiking', 'Hiking'),
        ('trekking', 'Trekking'),
        ('nature', 'Nature Tour'),
    ]
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    tour_type = models.CharField(max_length=10, choices=TOUR_TYPE_CHOICES)
    travelagency = models.ForeignKey('TravelAgency', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'
