from django.db import models

# Create your models here.
class TravelAgency(models.Model):
    name = models.CharField(max_length = 200)
    address = models.CharField(max_length=200)
    price = models.CharField(max_length = 100)

    def __str__(self):
        return f'{self.name}-{self.price}'

class ContactNumber(models.Model):
    contact_num = models.BigIntegerField(primary_key = True)
    travelagency = models.ForeignKey('TravelAgency', on_delete=models.CASCADE)
