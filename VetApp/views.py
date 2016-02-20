from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.http import Http404


class BaseView(View):
    def get(self, request):
        self.request = request
        self.initView()
        return self._get()
    
    def initView(self):
        self.context = {}
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
    

class IndexView(BaseView):
    def _get(self):
        return render(self.request, 'index.html', self.context)

@login_required(login_url='/')
class OwnerView(BaseView):
    def _get(self):
        return render(self.request, 'owner.html', self.context)

@login_required(login_url='/')
class AnimalView(BaseView):
    def _get(self):
        return render(self.request, 'animal.html', self.context)
    
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