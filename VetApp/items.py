from django.db import models
from VetApp.translate import g_count_type

class ALV(models.Model):
    class_type = models.IntegerField()
    value = models.IntegerField()

class SpecieDescription(models.Model):
    specie = models.ForeignKey('Specie', on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)

class Item(models.Model):
    name = models.TextField(max_length=100)
    description = models.TextField(max_length=1000, blank=True)
    stock_price = models.IntegerField()
    price = models.IntegerField()
    barcode = models.TextField(max_length=100, blank=True)
    count_type = models.TextField(max_length=10, default=g_count_type['default'])
    archive = models.BooleanField(default=False)
    alv =  models.ForeignKey('ALV', on_delete=models.CASCADE)

    specie_description =  models.ManyToManyField(SpecieDescription)

class Medicine(Item):
    pass

class Vaccine(Medicine):
    pass

class Drug(Medicine):
    pass

class Feed(Item):
    pass
