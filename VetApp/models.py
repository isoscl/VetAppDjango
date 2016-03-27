from django.db import models
from django.contrib.auth.models import User

from VetApp.items import *


#class Model(models.Model):


class Vet(models.Model):
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    vet_number = models.CharField(max_length=25)

    def __str__(self):
        return str(self.vet_number)

    def getText(self=None):
        return 'vet'
    def toString(self):
        return str(self.vet_number)
# class Marking(models.Model):
#     self.value = {'micro_number':'Mikrosiru'}

class PostOffice(models.Model):
    class Meta:
        unique_together = ('name','number')

    name = models.CharField(max_length=100)
    number = models.IntegerField()

    def getText(self=None):
        return 'post_office'
    def toString(self):
        return "%s, %i" % (self.name, self.number)


class Animal(models.Model):
    name = models.CharField(max_length=50)
    official_name = models.CharField(max_length=50, blank=True)
    birthday = models.DateField(auto_now=False, blank=True, null=True)
    micro_num = models.CharField(max_length=50, blank=True)
    rec_num = models.CharField(max_length=50, blank=True)
    tattoo = models.CharField(max_length=50, blank=True)
    insurance = models.TextField(max_length=255, blank=True)
    passport = models.CharField(max_length=100, blank=True)
    other_info = models.TextField(max_length=512, blank=True)
    death_day = models.DateField(auto_now=False, blank=True, null=True)
    #flags = Column(Integer)

    archive = models.BooleanField(default=False)

    #Setup one to many links
    specie = models.ForeignKey('Specie',  on_delete=models.CASCADE, blank=True, null=True)
    sex = models.ForeignKey('Sex', on_delete=models.CASCADE, blank=True, null=True)
    race = models.ForeignKey('Race', on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, blank=True, null=True)
    def getText(self=None):
        return 'animal'

    def __str__(self):
        date = ''
        if self.birthday:
            date = self.birthday.strftime('%d.%m.%Y')
        return ("%s, %s, %s" % (self.name or '', self.official_name or '', date))


class Operation(models.Model):
    pass



class VisitAnimal(models.Model):
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)
    operations = models.ManyToManyField(Operation, blank=True)
    items = models.ManyToManyField(Item, blank=True)

    anamnesis = models.CharField(max_length=1000, blank=True)
    status = models.CharField(max_length=1000, blank=True)
    diagnosis = models.CharField(max_length=1000, blank=True)
    treatment = models.CharField(max_length=1000, blank=True)

    #readonly_fields=('animal',)

    # class Meta:
    #     ordering = ["animal"]

    def getText(self=None):
        return 'visitAnimal'

from datetime import datetime
class Visit(models.Model):
    visit_reason = models.CharField(max_length=1000, blank=True)
    start_time =  models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(auto_now=False, blank=True, null=True)

    vet = models.ForeignKey('Vet', on_delete=models.CASCADE)
    owner = models.ForeignKey('Owner', on_delete=models.CASCADE)

    visitanimals = models.ManyToManyField(VisitAnimal, blank=True, null=True)
    items = models.ManyToManyField(Item, blank=True, null=True)

    archive = models.BooleanField(default=False)
    def getText(self=None):
        return 'visit'


class Owner(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True)

    post_office = models.ForeignKey('PostOffice',  on_delete=models.CASCADE, blank=True, null=True)

    animals = models.ManyToManyField(Animal, blank=True)

    phonenumber = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    other_info = models.TextField(max_length=500, blank=True)

    archive = models.BooleanField(default=False)
    def getText(self=None):
        return 'owner'
    def toString(self):
        return self.name

    def __str__(self):
        return "%s, %s" % (self.name, self.address)


class Bill(models.Model):
    visit = models.ForeignKey('Visit', on_delete=models.CASCADE)

    #ALV1
    clinic_payment = models.DecimalField(max_digits=10, decimal_places=2)
    operations_payment = models.DecimalField(max_digits=10, decimal_places=2)
    lab_payment = models.DecimalField(max_digits=10, decimal_places=2)
    accessories_payment = models.DecimalField(max_digits=10, decimal_places=2)

    #ALV2
    medicines_payment = models.DecimalField(max_digits=10, decimal_places=2)

    #ALV3
    diet_payment = models.DecimalField(max_digits=10, decimal_places=2)

    km = models.DecimalField(max_digits=10, decimal_places=2)
    km_payment = models.DecimalField(max_digits=10, decimal_places=2)

    #TODO: cereate these fields!
    #payment_method = models.CharField(max_length=100)
    #status = Column(Integer)

    due_date =  models.DateField()
    paid_time  = models.DateField()
    paid_value = models.DecimalField(max_digits=10, decimal_places=2)

    index_number = models.IntegerField()

    other_info = models.CharField(max_length=1000)
    def getText(self=None):
        return 'bill'

'''
This class just saves space because we dont have to save color string to for all animals
-name is name of color
'''
class Color(models.Model):
    #specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)
    def getText(self=None):
        return 'color'
    def toString(self):
        return self.name
'''
    This class helps us to handle with different sex names between species
    -specie_id is specie_id
'''
class Sex(models.Model):
    #specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)
    def getText(self=None):
        return 'sex'
    def toString(self):
        return self.name

class Specie(models.Model):
    #specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)
    def getText(self=None):
        return 'specie'
    def toString(self):
        return self.name

class Race(models.Model):
    specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)
    def getText(self=None):
        return 'race'
    def toString(self):
        return self.name
