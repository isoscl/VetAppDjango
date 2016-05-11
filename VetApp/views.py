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

    #initForm and return render or 404
    def initFormAndRender(self, form, form_name=None, html_path=None):

        form_name, html_path = getFormNameAndPath(form)

        print('GET: ', self.request.GET)
        if(len(self.request.GET) > 0):
            self.context[form_name] = form(self.request.GET)
        else:
            self.context[form_name] = form()
        #print(self.context[form_name])

        # print("FORM is: ", self.context[form_name])

        return render(self.request, html_path, self.context)


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

    def saveFormAndRender(self, form, form_name=None, html_path=None):
        if form_name is None:
            form_name = form.__name__[:-4].lower() + '_form' # XXXFORM -> xxx_form

        if html_path is None:
            html_path = form.__name__[:-4].lower() + '.html'

        print('POST: ', self.request.POST)
        self.context[form_name] = form(self.request.POST)

        if self.context[form_name].is_valid():
            print(self.context[form_name].cleaned_data)

            print("Is valid")
            _id = self.request.POST['id']

            obj = None
            if not _id is (None or ''):
                if _id.isdigit(): #check that id is valid
                    try:
                        print("get object")
                        obj = form.Meta.model.objects.get(id=int(_id))
                    except ObjectDoesNotExist:
                        return Http404()
                else:
                    return Http404()
            else:
                print("new object")
                obj = form.Meta.model() #new object

            save_after_object_variables = []
            if hasattr(form.Meta, 'save_after_object'):
                save_after_object_variables = form.Meta.save_after_object

            print(form.Meta, save_after_object_variables)
            for label_name in self.context[form_name].cleaned_data:
                if not (label_name == 'pk') and not (label_name in save_after_object_variables):
                    print('----',obj, label_name, self.context[form_name].cleaned_data[label_name])
                    setattr(obj, label_name, self.context[form_name].cleaned_data[label_name])
            obj.save()
            if len(save_after_object_variables) > 0:
                #self.context[form_name].saveRelatedObjects()

                for label_name in save_after_object_variables:
                    setattr(obj, label_name, self.context[form_name].cleaned_data[label_name])
                obj.save()

            self.request.message = g_save_tests['saved']

            return redirect('/'+form.__name__[:-4].lower()+'/?id='+str(obj.pk)+'&saved')
        else:
            print("Error")
            return render(self.request, html_path, self.context)



class IndexView(BaseView):
    def _get(self):
        return render(self.request, 'index.html', self.context)

class AnimalView(BaseView):
    def _get(self):
        return self.initFormAndRender(AnimalFrom)

    def _post(self):
        return self.saveFormAndRender(AnimalFrom)

def isInteger(value):
    return isinstance(value, int) or (isinstance(value, str) and value.isdigit())


class OwnerView(BaseView):
    def _get(self):
        return self.initFormAndRender(OwnerForm)

    def _post(self):
        print('Owner POST: ', self.request.POST)
        form_name,  html_path = getFormNameAndPath(OwnerForm)
        self.context[form_name] = OwnerForm(self.request.POST)

        if self.context[form_name].is_valid():
            print(self.context[form_name].cleaned_data)

            print("Is valid")
            _id = self.request.POST['id']

            if _id is '':
                pass
            elif isInteger(_id):
                pass
            else:
                print("Erorr: id was invalid format", _id)
                return Http404()

            obj = None
            if not _id is (None or ''):
                if _id.isdigit(): #check that id is valid
                    try:
                        print("get object")
                        obj = form.Meta.model.objects.get(id=int(_id))
                    except ObjectDoesNotExist:
                        return Http404()
                else:
                    return Http404()
            else:
                print("new object")
                obj = form.Meta.model() #new object

            save_after_object_variables = []
            if hasattr(form.Meta, 'save_after_object'):
                save_after_object_variables = form.Meta.save_after_object

            print(form.Meta, save_after_object_variables)
            for label_name in self.context[form_name].cleaned_data:
                if not (label_name == 'pk') and not (label_name in save_after_object_variables):
                    print('----',obj, label_name, self.context[form_name].cleaned_data[label_name])
                    setattr(obj, label_name, self.context[form_name].cleaned_data[label_name])
            obj.save()
            if len(save_after_object_variables) > 0:
                #self.context[form_name].saveRelatedObjects()

                for label_name in save_after_object_variables:
                    setattr(obj, label_name, self.context[form_name].cleaned_data[label_name])
                obj.save()

            self.request.message = g_save_tests['saved']

            return redirect('/'+form.__name__[:-4].lower()+'/?id='+str(obj.pk)+'&saved')
        else:
            print("Error")
            return render(self.request, html_path, self.context)

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
