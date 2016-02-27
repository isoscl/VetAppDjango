from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist

from VetApp.translate import g_save_tests
from VetApp.forms import *
from VetApp.models import *

from VetApp import models

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
        if form_name is None:
            form_name = form.__name__[:-4].lower() + '_form' # XXXFORM -> xxx_form

        if html_path is None:
            html_path = form.__name__[:-4].lower() + '.html'

        _id = self.request.GET.get('id', '').strip('/')
        if not _id is '':
            if _id.isdigit():
                try:
                    obj = form.Meta.model.objects.get(id=int(_id))
                    self.context[form_name] = form(instance=obj)
                    self.context[form_name]['pk'].field.initial = obj.pk
                except ObjectDoesNotExist:
                    return Http404()
            else:
                return Http404()
        else:
            self.context[form_name] = form()

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


        self.context[form_name] = form(self.request.POST)

        if self.context[form_name].is_valid():
            print("Is valid")
            print("POST: ", self.request.POST)
            _id = self.request.POST['pk']

            obj = None
            if not _id is None:
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

            for label_name in self.context[form_name].cleaned_data:
                if not label_name == 'pk':
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
        return render(self.request, 'visit.html', self.context)


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
        return render(self.request, 'vet.html', self.context)

# @login_required(login_url='/')
class SettingsView(BaseView):
    def _get(self):
        return render(self.request, 'settings.html', self.context)
