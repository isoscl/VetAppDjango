from django.db import models
from VetApp.translate import g_count_type_list

class ALV():
    class0 = 0
    class1 = 24
    class2 = 10
    class3 = 14

class SpecieDescription(models.Model):
    specie = models.ForeignKey('Specie', on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True)
    stock_price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    barcode = models.CharField(max_length=100, blank=True)
    count_type = models.CharField(max_length=10, choices=g_count_type_list, default='pcs')


    archive = models.BooleanField(default=False)

    specie_description =  models.ManyToManyField(SpecieDescription)

    def __str__(self):
        return "%s" % (self.name)

    def getALV(self):
        return self.price * self.getALVPercent/100.

    def getALVTuple(self):
        return (self.getALVPercent, self.getALV())

    def getALVPercent(self=None):
        return ALV.class1

    def getALVPrice(self):
        return self.price * (100 + self.getALVPercent)/100.

class Medicine(Item):
    def getALVPercent(self = None):
        return ALV.class2

class Vaccine(Medicine):
    duration = models.DurationField()

class Feed(Item):
    def getALVPercent(self = None):
        return ALV.class3

class DrugUsage(models.Model):
    drug = models.ForeignKey('Drug', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    time = models.DateField(auto_now=False)

class Drug(Medicine):
    pass
