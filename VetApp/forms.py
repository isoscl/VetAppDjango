from django import forms
from django.contrib.auth.forms import AuthenticationForm

# from VetApp.models import Vet

from VetApp.translate import g_login_text, g_form_labels, g_form_placeholders,g_count_type_list

from VetApp.models import *


def translate_labels(field_list):
    translate_dict = {}
    for field_name in field_list:
        translate_dict[field_name] = g_form_labels[field_name]
    return translate_dict

#work a round for django failure to add correct input types
def make_time_widgets(time_fields):
    widgets = {}
    for key in time_fields:
        if time_fields[key] == 'datetime-local':
            widget = forms.DateInput()
            widget.input_type = 'datetime-local'
        elif time_fields[key] == 'date':
            widget = forms.DateInput()
            widget.input_type = 'date'
        else:
            continue
        widgets[key] = widget
    return widgets

# from django.forms.utils import ErrorList
# class DivErrorList(ErrorList):
#     def __str__(self):              # __unicode__ on Python 2
#         return self.as_divs()
#     def as_divs(self):
#         if not self: return ''
#         #'<div class="form-group ">%s</div>'
#         return "" # '<input class="form-control" required>%s</input>'  % ''.join([self.errorhtml(e) for e in self])
#
#     def errorhtml(self, e):
#         return '' #<dic class="alert alert-warning"><a href="#" class"close" data-dismiss="error">x</a><strong>%s</strong></div>' % e

class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if not obj:
            return 'Tyhjä'
        else:
            return  obj.toString() #"%s, %s" % (obj.name, obj.number)

from datetime import datetime

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        #self.error_class=DivErrorList
        self.__setFields(**kwargs)

        #set model fields
        for field in self.Meta().fields:
            self.fields[field].widget.attrs.update({'class':'form-control','placeholder':g_form_placeholders[field]})
        self.fields['pk'] = forms.IntegerField(widget = forms.HiddenInput(), required=False)

    def setLabel(self, name, text=None):
        pass
        # if not text:
        #     text = name
        # if type(self.fields[name]) is forms.DateField:
        #     self.fields[name].widget.input_type = 'date'
        # elif type(self.fields[name]) is forms.DateTimeField:
        #     self.fields[name].widget.input_type = 'datetime-local'
        #     self.fields[name].widget.value = datetime.now()
        #
        # #self.fields[name].label = g_form_labels[text]


    def __setFields(self, **kwargs):
        pass

    def setFields(self, parameters):
        pass

    def cleanPk(self, _id):
        if (type(_id) is str and _id.isdigit()) or (type(_id) is int):
            return int(_id)
        return None

    def getObject(self,_id, obj):
        #return None or object with constuctor obj
        if (type(_id) is str and _id.isdigit()) or (type(_id) is int):
            return obj.objects.get(id=int(_id))
        elif not (type(id) is int):
            return None

    # def setChoiceFieldSingleObject(self,obj_class, obj_pk):
    #     if not obj_class is None:
    #         print("setChoiceField",obj_class)
    #         self.fields[obj_class.getText()]=MyModelChoiceField(queryset=obj_class.objects.all(),required=False)
    #         self.setLabel(obj_class.getText())
    #         self.fields[obj_class.getText()].initial = obj_pk

    # def setQueryInChoiceField(self):
    #     pass

    def getInternalForms(self):
        return {}

    # def setChoiceField(self, model_obj, initial=None):
    #     if not model_obj is None:
    #         #make field
    #         print("---------------------------------")
    #         self.fields[model_obj.getText()]=MyModelChoiceField(queryset=model_obj.objects.all(),
    #             required=False, empty_label=g_form_labels['select'])
    #         self.setLabel(model_obj.getText())
    #         #check if there is initial value and select it if found
    #         if initial:
    #             self.fields[model_obj.getText()].initial = initial.pk

    #field_name=str. list=str_list, required=bool, initila=int
    # def setChoiceFieldWithList(self, field_name, list, required=False, initial=None):
    #     _list = []
    #     for i in range(0,len(list)):
    #         _list.append((i, list[i]))
    #
    #     self.fields[field_name]=forms.ChoiceField(required=required, choices=_list)
    #     self.setLabel(field_name)
    #
    #     if initial:
    #         self.fields[model_obj.getText()].initial = initial


class SpecieDescriptionForm(BaseForm):
    class Meta:
        model = SpecieDescription
        fields = ['text']
        labels = translate_labels(fields)

    def __setFields(self, **kwargs):
        self.setChoiceField(Specie)


class MoneyInput(forms.widgets.NumberInput):
    def __init__(self, *args, **kwargs):
        print(kwargs)
        kwargs.update({'attrs':{'min': '0', 'max': '99999', 'step': '0.05'}})
        super(MoneyInput, self).__init__(*args, **kwargs)

class ItemForm(BaseForm):
    class Meta:
        model=Item
        fields=['name', 'description', 'stock_price', 'price',
        'barcode', 'count_type', 'archive']
        widgets =  {'name': forms.TextInput(attrs={'required': True,}),
                    'description': forms.Textarea(attrs={'rows': 5,}),
                    'stock_price':MoneyInput(), 'price':MoneyInput()}
        labels = translate_labels(fields)

    #def __setFields(self, **kwargs):
        #self.setChoiceFieldWithList('count_type', g_count_type_list)

class VisitAnimalForm(BaseForm):
    class Meta:
        model=VisitAnimal
        fields=['animal', 'operations', 'items','anamnesis',
                'status','diagnosis','treatment']
        widgets={'animal': forms.HiddenInput(),
                'anamnesis':forms.Textarea(attrs={'rows': 5,}),
                'status':forms.Textarea(attrs={'rows': 5,}),
                'diagnosis':forms.Textarea(attrs={'rows': 5,}),
                'treatment':forms.Textarea(attrs={'rows': 5,})}
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(VisitAnimalForm, self).__init__(*args, **kwargs)
        animal = kwargs.pop('initial', None).pop('animal', None)
        if not animal is None:
            self.animal_label = g_form_labels['animal']
            self.animal_text = str(animal)

class VetForm(BaseForm):
    class Meta:
        model=Vet
        fields = ['vet_number']
        labels = translate_labels(fields)

#from django.forms import formset_factory

def make_static_text_label(label, text):
    return '<label> %s: %s </label>' % (label, text)

class VisitForm(BaseForm):
    class Meta:
        model=Visit
        fields = ['start_time', 'end_time', 'visit_reason', 'vet', 'owner', 'items']
        time_fields = {'start_time':'datetime-local', 'end_time':'datetime-local'}
        widgets = {'visit_reason':forms.Textarea(attrs={'rows': 5,}),
                   'owner': forms.HiddenInput()}
        widgets.update(make_time_widgets(time_fields))

        save_after_object = ['visitanimals']
        labels = translate_labels(fields)

    # def getInternalForms(self):
    #     if hasattr(self, 'formset'):
    #         return {'formset':self.formset, 'owner_text':self.owner_text,
    #                 'owner_label':self.owner_label}
    #     return {}

    def __setFields(self, **kwargs):
        visit = kwargs.pop('instance',None)
        if not visit is None:
            self.setChoiceField(Owner, initial=visit.owner)
            self.setChoiceField(Vet, initial=visit.vet)

            formset = []
            for visitanimal in visit.visitanimals:
                formset.append(VisitAnimalForm(instance=visitanimal))
            self.formset = formset

    def setFields(self, parameters):
        constructor_dict = {'owner':Owner,'vet':Vet, 'animals':Animal}
        #parse objects from parameters
        if not('owner' in parameters and 'vet' in parameters):
            return False #vet or owner missing abort

        for key in parameters:
            if key == 'animals':
                animal_pk_list = parameters['animals'].split(',')
                formset = []
                for index in animal_pk_list:
                    #find animals from database
                    tmp_animal = self.getObject(index.strip(), constructor_dict[key])
                    if not tmp_animal is None:
                        formset.append(VisitAnimalForm(initial={'animal':tmp_animal}))
                    else:
                        print("VisitForm->setFields: animal not found from database. id: ", index)
                        return False

                print("VisitForm-setFields: add form set")
                self.formset = formset
            else:
                #add objects to correct places
                _pk = self.cleanPk(parameters[key].strip())
                obj = self.getObject(parameters[key].strip(), constructor_dict[key])
                if (not _pk is None) and (not obj is None):
                    print("set initial: ", key, " value: ", _pk)
                    self.fields[key].initial = _pk
                    #add owner label to list
                    if key == 'owner':
                        self.owner_label = g_form_labels[key]
                        self.owner_text = str(obj)
                else:
                    print("VisitForm->setFields: model not found: key: ", key, " pk: ", _pk)
                    return False #did not find object so abort
        return True



class OwnerForm(BaseForm):
    class Meta:
        model= Owner
        fields = ['name', 'address', 'phonenumber', 'email', 'other_info','animals', 'archive']
        widgets = {'name': forms.TextInput(attrs={'required': True,}),
                    'email': forms.EmailInput()}
        save_after_object = ['animals']
        labels = translate_labels(fields)

    def __setFields(self, **kwargs):
        owner = kwargs.pop('instance',None)
        if not owner == None:
            self.setChoiceField(PostOffice, initial=owner.post_office)
        else:
            self.setChoiceField(PostOffice)


class AnimalFrom(BaseForm):
    class Meta:
        model = Animal
        fields = ['name', 'official_name', 'birthday', 'micro_num',
        'rec_num', 'tattoo', 'insurance', 'passport', 'other_info',
        'death_day']
        widgets = {'name': forms.TextInput(attrs={'required': True,}),
                    'insurance': forms.Textarea(attrs={'rows': 5,}),
                    'other_info': forms.Textarea(attrs={'rows': 5}),}
        labels = translate_labels(fields)

    # def __init__(self, *args, **kwargs):
    #     super(AnimalFrom, self).__init__(*args, **kwargs)
        # Color(name='Musta').save()
        # Sex(name='Uros').save()
        # s = Specie(name='Koira')
        # s.save()
        # Race(name='Russeli', specie=s).save()

    def __setFields(self, **kwargs):
        animal = kwargs.pop('instance',None)
        if not animal is None:
            self.setChoiceField(Specie, initial=animal.specie)
            self.setChoiceField(Sex, initial=animal.sex)
            self.setChoiceField(Race, initial=animal.race)
            self.setChoiceField(Color, initial=animal.color)
        else:
            self.setChoiceField(Specie)
            self.setChoiceField(Sex)
            self.setChoiceField(Race)
            self.setChoiceField(Color)

        # po = PostOffice(name='Kotka',number='12345')
        # po.save()
        # po = PostOffice(name='Kouvola',number='12345')
        # po.save()


class SexForm(BaseForm):
    class Meta:
        model = Sex
        fields = ['name']
        labels = translate_labels(fields)



class ColorForm(BaseForm):
    class Meta:
        model = Color
        fields = ['name']
        labels = translate_labels(fields)

class SpecieForm(BaseForm):
    class Meta:
        model = Specie
        fields = ['name']
        labels = translate_labels(fields)

class RaceForm(BaseForm):
    class Meta:
        model = Race
        fields = ['name']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(RaceForm, self).__init__(*args, **kwargs)
        specie = kwargs.pop('specie','')
        self.setChoiceField(Specie, name=specie)

class AuthForm(AuthenticationForm):
    pass
#     # class Meta:
#     #     labels = {'username':g_login_text['username_text']}
#     def __init__(self, *args, **kwargs):
#         super(AuthenticationForm,self).__init__(*args,**kwargs)
#         # self.fields['username'].label = ''
#         # self.fields['password'].label = ''
#         # self.fields['username'].widget.attrs.update({'class':'form-control','placeholder':g_login_text['username_placeholder']})
#         # self.fields['password'].widget.attrs.update({'class':'form-control','placeholder':g_login_text['password_placeholder']})
#
#     def confirm_login_allowed(self, user):
#         print("user", user)
#         pass
