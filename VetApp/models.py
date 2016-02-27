from django.db import models
from django.contrib.auth.models import User

from VetApp.items import *


#class Model(models.Model):


class Vet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vet_number = models.CharField(max_length=25)

# class Marking(models.Model):
#     self.value = {'micro_number':'Mikrosiru'}

class PostOffice(models.Model):
    class Meta:
        unique_together = ('name','number')

    name = models.CharField(max_length=100)
    number = models.IntegerField()

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



class Operation(models.Model):
    pass



class VisitAnimal(models.Model):
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)
    operations = models.ManyToManyField(Operation)
    items = models.ManyToManyField(Item)

    anamnesis = models.CharField(max_length=1000, blank=True)
    status = models.CharField(max_length=1000, blank=True)
    diagnosis = models.CharField(max_length=1000, blank=True)
    treatment = models.CharField(max_length=1000, blank=True)


class Visit(models.Model):
    startTime = models.DateField(auto_now=True)
    endTime = models.DateField(auto_now=False)
    visit_reason = models.CharField(max_length=1000, blank=True)
    vet = models.ForeignKey('Vet', on_delete=models.CASCADE)
    owner = models.ForeignKey('Owner', on_delete=models.CASCADE)

    visitanimals = models.ManyToManyField(VisitAnimal)
    items = models.ManyToManyField(Item)

    archive = models.BooleanField(default=False)



class Owner(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True)

    post_office = models.ForeignKey('PostOffice',  on_delete=models.CASCADE, blank=True, null=True)

    animals = models.ManyToManyField(Animal)

    phonenumber = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    other_info = models.TextField(max_length=500, blank=True)

    archive = models.BooleanField(default=False)

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
