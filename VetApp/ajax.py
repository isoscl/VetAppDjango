from django.http import JsonResponse
import json

from VetApp import models

from django.core import serializers

#response = {"data":serializers.serialize("json", )}

#get animals and return their dicts (defined in model)

def convert_to_dict(query):
    obj_list = []
    for obj in query:
        obj_list.append(models.model_to_dict(obj))
    return obj_list

def makeAnimalQuery(search_string):
    return models.Animal.objects.filter(name__icontains=search_string) | \
    models.Animal.objects.filter(official_name__icontains=search_string)

def search_objects(request, gen_query):
    if(request.POST):
        #parse parameters from request
        search_string = request.POST['search_string']
        start = int(request.POST['start'])
        _max = int(request.POST['max'])

        if int(request.POST['max']) < 0: #no limit
            objects = convert_to_dict(gen_query(search_string)[start:])
        else:
            objects = convert_to_dict(gen_query(search_string)[start:(start+int(request.POST['max']))])

        return JsonResponse({'objects':objects})
    else:
        return JsonResponse({'error':'Unsupported request', 'error_text':'Only POST is supported'})

def get_animals(request):
    return search_objects(request, makeAnimalQuery)

def get_header(request):
    if(request.GET):
        _type = request.GET['type']
        if _type in models.__all__:
            return JsonResponse({'header_list':eval('models.'+ _type).table_header_string_list()})
        else:
            return JsonResponse({'error':'Unsupported object type',
            'error_text':'ERROR: get_header(), Unsupported header type: '+ str(_type) +'. Supported types are:' + str(models.__all__)})

    else:
        return JsonResponse({'error':'Unsupported request', 'error_text':'Only GET is supported'})


def ajax_view(request):
    print("I got it!")
    return get_animals(request)
