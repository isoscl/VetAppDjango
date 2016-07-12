from django.http import JsonResponse
import json

from VetApp import models

from django.core import serializers

#response = {"data":serializers.serialize("json", )}

#get animals and return their dicts (defined in model)

def query_models(query):
    obj_list = []
    for obj in query:
        obj_list.append(obj.to_dict())
    return obj_list

def get_animals(request):
    if(request.POST):
        if(len(request.POST['search_string'])>0):
            search_string = request.POST['search_string']
            start = int(request.POST['start'])
            _max = int(request.POST['max'])

            query_set = models.Animal.objects.filter(name__icontains=search_string) | \
            models.Animal.objects.filter(official_name__icontains=search_string)

            if _max < 0:
                return JsonResponse({'objects':query_models(query_set[start:]), 'header_list':models.Animal.table_header_string_list()})
            else:
                end = start + _max #end is start + max
                return JsonResponse({'objects':query_models(query_set[start:end]), 'header_list':models.Animal.table_header_string_list()})
        else:
            print("wtf")
            return JsonResponse({'objects':query_models(models.Animal.objects.all()), 'header_list':models.Animal.table_header_string_list()})
    else:
        return JsonResponse({'error':'Only POST is supported'})




def ajax_view(request):
    print("I got it!")
    return get_animals(request)
