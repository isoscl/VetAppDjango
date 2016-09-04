from django.db import models
from django.contrib.auth.models import User
from VetApp.translate import g_count_type_list
import VetApp
from datetime import datetime

__all__ = ['Vet', 'PostOffice', 'Animal', 'Operation', 'VisitAnimal', 'Visit',
'VisitItems', 'Owner', 'Bill', 'Color', 'Sex', 'Specie', 'Race',
'Item', 'ItemBase', 'SpecieDescription']

g_avl_dict = {'Item':24,'Medicine':10,'Vaccine':10,'Feed':14,'Drug':10}


class SpecieDescription(models.Model):
    specie = models.ForeignKey('Specie', on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)

def get_item_alv(item):
    return g_avl_dict[item.item_type]

class ItemBase(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True)
    stock_price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    barcode = models.CharField(max_length=100, blank=True)
    count_type = models.CharField(max_length=10, choices=g_count_type_list, default='pcs')
    archive = models.BooleanField(default=False)
    specie_description = models.ManyToManyField(SpecieDescription)
    item_type = models.CharField(max_length=20, default='Item')


class Item(models.Model):
     base = models.ForeignKey('ItemBase', on_delete=models.CASCADE)
     count = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)

     def table_header_string_list(self=None):
         return ['pk', 'name', 'count']

def clean_str(_str):
    return '' if _str is None else str(_str)

def model_to_dict(model):
    return_dict = {}
    for key in model.table_header_string_list():
        return_dict[key] = clean_str(getattr(model, key))
    return_dict['type'] = model.__class__.__name__
    return return_dict




class Vet(models.Model):
    #user = models.OneToOneField(User, on_delete=models.CASCADE)
    vet_number = models.CharField(max_length=25)

    def __str__(self):
        return str(self.vet_number)

    def getText(self=None):
        return 'vet'
    def __str__(self):
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
    def __str__(self):
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

    def table_header_string_list(self=None):
        return ['pk', 'name','specie','race','sex','birthday']


class Operation(models.Model):
    pass #name = models.CharField(max_length=255)

class VisitAnimal(models.Model):
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)
    operations = models.ManyToManyField(Operation, blank=True)
    items = models.ManyToManyField(Item, blank=True)

    anamnesis = models.CharField(max_length=1000, blank=True)
    status = models.CharField(max_length=1000, blank=True)
    diagnosis = models.CharField(max_length=1000, blank=True)
    treatment = models.CharField(max_length=1000, blank=True)

    def table_header_string_list(self=None):
        return ['pk', 'animal']

class Visit(models.Model):
    visit_reason = models.CharField(max_length=1000, blank=True)
    start_time =  models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(auto_now=False, blank=True, null=True)

    vet = models.ForeignKey('Vet', on_delete=models.CASCADE)
    owner = models.ForeignKey('Owner', on_delete=models.CASCADE)

    visitanimals = models.ManyToManyField(VisitAnimal, blank=True)
    items = models.ManyToManyField(Item, through="VisitItems", blank=True)

    archive = models.BooleanField(default=False)
    def getText(self=None):
        return 'visit'

class VisitItems(models.Model):
    Item = models.ForeignKey(Item)
    visit = models.ForeignKey(Visit)
    count = models.IntegerField(default=1)

class Owner(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=True)
    post_office = models.ForeignKey('PostOffice',  on_delete=models.CASCADE, blank=True, null=True)
    phonenumber = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    other_info = models.TextField(max_length=500, blank=True)
    archive = models.BooleanField(default=False)

    animals = models.ManyToManyField(Animal, blank=True)

    def getText(self=None):
        return 'owner'
    def __str__(self):
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
    def __str__(self):
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
    def __str__(self):
        return self.name

class Specie(models.Model):
    name = models.CharField(max_length=50)#, unique=True) #TODO: Make unique
    def getText(self=None):
        return 'specie'
    def __str__(self):
        return self.name

class Race(models.Model):
    specie = models.ForeignKey('Specie', on_delete=models.CASCADE,)
    name = models.CharField(max_length=50)#, unique=True) #TODO: Make unique
    def getText(self=None):
        return 'race'
    def __str__(self):
        return self.name
