from django.db import models

# Create your models here.

from django.db import models

# Create your models here.
class TravelAgency(models.Model):
    name = models.CharField(max_length = 200)
    address = models.CharField(max_length=200)
    contact_num = models.BigIntegerField(primary_key = True)
    website = models.URLField()

    def __str__(self):
        return f'{self.name}'

class Tour(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    travelagency = models.ForeignKey('TravelAgency', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'

