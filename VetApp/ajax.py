from django.http import JsonResponse
import json

from VetApp import models

from django.core import serializers



def ajax_view(request):
    print("I got it!")

    response = {"data":serializers.serialize("json", models.Animal.objects.all())}

    #Here you have to enter code here
    #to receive the data (datastring) you send here by POST
    #Do the operations you need with the form information
    #Add the data you need to send back to a list/dictionary like response
    #And return it to the JQuery function `enter code here`(simplejson.dumps is to convert to JSON)
    return JsonResponse(response)
