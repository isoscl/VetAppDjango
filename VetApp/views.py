from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import Http404

from VetApp.forms import AuthForm, RaceForm, SpecieForm, SexForm, ColorForm, AnimalFrom
from VetApp.forms import OwnerForm, MyModelChoiceField
from VetApp.models import Animal

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

    def validate_form(self, form):
        if form.is_valid():
            print("Is valid")
            obj = form.Meta.model()
            for label_name in form.cleaned_data:
                setattr(obj, label_name, form.cleaned_data[label_name])
            obj.save()
            return True
        else:
            print("Error")
            return False



class IndexView(BaseView):
    def _get(self):
        return render(self.request, 'index.html', self.context)

class AnimalView(BaseView):
    def _get(self):
        self.context['animal_form'] = AnimalFrom()
        return render(self.request, 'animal.html', self.context)

    def _post(self):
        self.context['animal_form'] = AnimalFrom(self.request.POST)
        if self.validate_form(self.context['animal_form']):
            return render(self.request, 'animal.html', self.context)
        else:
            return render(self.request, 'animal.html', self.context)

class OwnerView(BaseView):
    def _get(self):
        self.context['owner_form'] = OwnerForm()
        return render(self.request, 'owner.html', self.context)

    def _post(self):
        self.context['owner_form'] = OwnerForm(self.request.POST)
        if self.validate_form(self.context['owner_form']):
            return render(self.request, 'owner.html', self.context)
        else:
            return render(self.request, 'owner.html', self.context)


# @login_required(login_url='/')
# class AnimalView(BaseView):
#     def _get(self):
#         return render(self.request, 'animal.html', self.context)

@login_required(login_url='/')
class VisitView(BaseView):
    def _get(self):
        return render(self.request, 'visit.html', self.context)

@login_required(login_url='/')
class ItemView(BaseView):
    def _get(self):
        return render(self.request, 'item.html', self.context)

@login_required(login_url='/')
class OperationView(BaseView):
    def _get(self):
        return render(self.request, 'operation.html', self.context)

@login_required(login_url='/')
class DrugView(BaseView):
    def _get(self):
        return render(self.request, 'drug.html', self.context)

@login_required(login_url='/')
class BillView(BaseView):
    def _get(self):
        return render(self.request, 'bill.html', self.context)

@login_required(login_url='/')
class VetView(BaseView):
    def _get(self):
        return render(self.request, 'vet.html', self.context)

@login_required(login_url='/')
class SettingsView(BaseView):
    def _get(self):
        return render(self.request, 'settings.html', self.context)
