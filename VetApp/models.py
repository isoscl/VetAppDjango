from django.db import models

# Create your models here.


class Vet(models.User):
    vet_number = models.CharField(max_length=20)


    class Meta:
        ordering = ('name',)