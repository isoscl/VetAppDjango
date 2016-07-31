from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from VetApp.translate import g_save_tests
from VetApp.forms import *
from VetApp.models import *

from VetApp import models

import json
from django.http import HttpResponse

# class SpecieView(BaseView):
#     def _get(self):
#         self.context['specie_form'] = SpecieForm()
#         return render(self.request, 'specie.html', self.context)
#
# class RaceView(BaseView):
#     def _get(self):
#         form=RaceForm(specie=request.specie_name)
#         self.context['race_form'] = form
#         return render(self.request, 'race.html', self.context)
#     def post(self, request):
#         form=RaceForm(request.POST, specie=request.specie_name)

def search_base(request, model_class):
        if request.is_ajax():
            q = request.GET.get('term', '')
            objs = model_class.objects.filter(name__icontains = q )[:20]
            results = []
            for obj in objs:
                obj_json = {}
                obj_json['id'] = obj.pk
                obj_json['label'] = obj.name
                obj_json['value'] = obj.name
                results.append(obj_json)
            data = json.dumps(results)
        else:
            data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

def operations_search(request):
    pass #return search_base(request, Operation)

def items_search(request):
    return search_base(request, Item)

def getFormNameAndPath(form):
    form_name = form.__name__[:-4].lower() + '_form' # XXXFORM -> xxx_form
    html_path = form.__name__[:-4].lower() + '.html'
    return (form_name, html_path)

def generate_error_sting(_dict):
    print("asd", _dict)
    return str(_dict)

class BaseView(View):
    def get(self, request):
        self.request = request
        self.initView()
        return self._get()

    def post(self, request):
        self.request = request
        self.initView()
        return self._post()

    def initView(self):
        if self.request.user and self.request.user.is_authenticated:
            self.context = {'auth_form':AuthForm()}
        else:
            self.context = {'auth_form':''}

        if self.request.session.__contains__('init'):
            self.request.session.__setitem__('init', True)

    def Alert(self, message):
        if not 'alert_message' in self.context:
            self.context['alert_message'] = message
        else: #if there is many alerts combine them
            self.context['alert_message'] += ", " + message

    def _get(self):
        print("Error")
        raise Http404("BaseView used! Even it should not")

    def _post(self):
        print("Error")
        raise Http404("BaseView used! Even it should not")

    #initForm and return render or 404
    def initFormAndRender(self, form, form_name=None, html_path=None):

        form_name, html_path = getFormNameAndPath(form)

        print('GET: ', self.request.GET)

        self.context[form_name] = form(self.request.GET)

        return render(self.request, html_path, self.context)

    def saveFormAndRender(self, form, form_name=None, html_path=None):
        form_name, html_path = getFormNameAndPath(form)

        print('POST: ', self.request.POST)
        self.context[form_name] = form(self.request.POST)

        from VetApp.forms import get_errors_from_form, save_form_data

        errors = get_errors_from_form(self.context[form_name])
        if errors != None:
            print("saveFormAndRender, form has errors: ", errors)
            self.context[form_name].errors = generate_error_sting(errors)
            return render(self.request, html_path, self.context)
        else: # no errors
            if save_form_data(self.context[form_name]): #save succsessed
                self.context[form_name].success = 'Model saved'
                return render(self.request, html_path, self.context)
            else: #was not able to save form
                print("saveFormAndRender, form could not be saved")
                self.context[form_name].errors = generate_error_sting({'save_error':"saveFormAndRender, form could not be saved"})
                return render(self.request, html_path, self.context)


class IndexView(BaseView):
    def _get(self):
        return render(self.request, 'index.html', self.context)

class AnimalView(BaseView):
    def _get(self):
        return self.initFormAndRender(AnimalForm)

    def _post(self):
        return self.saveFormAndRender(AnimalForm)

def isInteger(value):
    return isinstance(value, int) or (isinstance(value, str) and value.isdigit())


class OwnerView(BaseView):
    def _get(self):
        return self.initFormAndRender(OwnerForm)

    def _post(self):
        return self.saveFormAndRender(OwnerForm)


# @login_required(login_url='/')
class ItemView(BaseView):
    def _get(self):
        return self.initFormAndRender(ItemForm)

    def _post(self):
        return self.saveFormAndRender(ItemForm)

# @login_required(login_url='/')
# class AnimalView(BaseView):
#     def _get(self):
#         return render(self.request, 'animal.html', self.context)

# @login_required(login_url='/')
class VisitView(BaseView):
    def _get(self):
        return self.initFormAndRender(VisitForm)

    def _post(self):
        return self.saveFormAndRender(VisitForm)


# @login_required(login_url='/')
class OperationView(BaseView):
    def _get(self):
        return render(self.request, 'operation.html', self.context)

# @login_required(login_url='/')
class DrugView(BaseView):
    def _get(self):
        return render(self.request, 'drug.html', self.context)

# @login_required(login_url='/')
class BillView(BaseView):
    def _get(self):
        return render(self.request, 'bill.html', self.context)

# @login_required(login_url='/')
class VetView(BaseView):
    def _get(self):
        return self.initFormAndRender(VetForm)

    def _post(self):
        return self.saveFormAndRender(VetForm)

# @login_required(login_url='/')
class SettingsView(BaseView):
    def _get(self):
        return render(self.request, 'settings.html', self.context)
