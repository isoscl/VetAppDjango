from django.db import models
from django.contrib.auth.models import User

class Vet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vet_number = models.CharField(max_length=25)

# class Marking(models.Model):
#     self.value = {'micro_number':'Mikrosiru'}

class Animal(models.Model):
    name = models.CharField(max_length=50)
    official_name = models.CharField(max_length=50, blank=True)
    birthday = models.DateField(auto_now=False, blank=True)
    micro_num = models.CharField(max_length=50, blank=True)
    rec_num = models.CharField(max_length=50, blank=True)
    tattoo = models.CharField(max_length=50, blank=True)
    insurance = models.CharField(max_length=255, blank=True)
    passport = models.CharField(max_length=100, blank=True)
    other_info = models.CharField(max_length=512, blank=True)
    death_day = models.DateField(auto_now=False, blank=True)
    #flags = Column(Integer)

    archive = models.BooleanField(default=False)

    #Setup one to many links
    specie = models.ForeignKey('Specie',  on_delete=models.CASCADE, blank=True, null=True)
    sex = models.ForeignKey('Sex', on_delete=models.CASCADE, blank=True, null=True)
    race = models.ForeignKey('Race', on_delete=models.CASCADE, blank=True, null=True)
    color = models.ForeignKey('Color', on_delete=models.CASCADE, blank=True, null=True)


'''
This class just saves space because we dont have to save color string to for all animals
-name is name of color
'''
class Color(models.Model):
    #specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)

'''
    This class helps us to handle with different sex names between species
    -specie_id is specie_id
'''
class Sex(models.Model):
    #specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)

class Specie(models.Model):
    #specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)

class Race(models.Model):
    specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)
