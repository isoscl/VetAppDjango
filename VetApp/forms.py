from django import forms
from django.contrib.auth.forms import AuthenticationForm

# from VetApp.models import Vet

from VetApp.translate import g_login_text, g_form_labels, g_form_placeholders,g_count_type_list

from VetApp.models import *

from datetime import datetime

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

def set_instakce_to(obj, kwargs):
    if obj:
        kwargs.update({'instance': obj})

def clean_pk(_pk):
    if (type(_pk) is str and _pk.isdigit()) or (type(_pk) is int):
        return int(_pk)
    return None

def get_object(_pk, obj):
    _pk = clean_pk(_pk)
    if _pk:
        try:
            return obj.objects.get(pk=int(_pk))
        except ObjectDoesNotExist:
            return None #TODO: this error should be handled
    return None



def format_widgets_and_add_pk(self, obj=None):
    _pk = None
    if obj:
        _pk = obj.pk
    for field in self.Meta().fields:
        self.fields[field].widget.attrs.update({'class':'form-control','placeholder':g_form_placeholders[field]})
    self.fields['pk'] = forms.IntegerField(widget = forms.HiddenInput(),
    required=False, initial=_pk)


class SpecieDescriptionForm(forms.ModelForm):
    class Meta:
        model = SpecieDescription
        fields = ['text']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(SpecieDescriptionForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)


class MoneyInput(forms.widgets.NumberInput):
    def __init__(self, *args, **kwargs):
        print(kwargs)
        kwargs.update({'attrs':{'min': '0', 'max': '99999', 'step': '0.05'}})
        super(MoneyInput, self).__init__(*args, **kwargs)

class ItemForm(forms.ModelForm):
    class Meta:
        model=Item
        fields=['name', 'description', 'stock_price', 'price',
        'barcode', 'count_type', 'archive']
        widgets =  {'name': forms.TextInput(attrs={'required': True,}),
                    'description': forms.Textarea(attrs={'rows': 5,}),
                    'stock_price':MoneyInput(), 'price':MoneyInput()}
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)

class VisitAnimalForm(forms.ModelForm):
    class Meta:
        model=VisitAnimal
        fields=['animal', 'operations', 'items','anamnesis',
                'status','diagnosis','treatment']
        widgets={'animal': forms.HiddenInput(),
                'anamnesis':forms.Textarea(attrs={'rows': 2,}),
                'status':forms.Textarea(attrs={'rows': 2,}),
                'diagnosis':forms.Textarea(attrs={'rows': 2,}),
                'treatment':forms.Textarea(attrs={'rows': 2,})}
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        print('VisitAnimalForm: args',args,' kwargs: ',kwargs)
        #never give args for parent TODO: check if this is correct
        #convert animal object to int presenting it pk
        animal = None
        if len(args) > 0:
            animal = args[0].get('animal', None)
            if animal and not (type(animal) is int):
                args[0]['animal'] = animal.pk

        super(VisitAnimalForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)
        if animal:
            self.animal_pk = animal.pk
            self.animal_text = str(animal)

class VetForm(forms.ModelForm):
    class Meta:
        model=Vet
        fields = ['vet_number']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(VetForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)


class VisitItemForm(forms.Form):
    # class Meta:
    #     fields = ['name', 'count']
    pk = forms.CharField(widget=forms.HiddenInput(),required=False)
    item_pk = forms.CharField(widget=forms.HiddenInput())
    count = forms.DecimalField()

    def __fill_item_data(self,item):
        if item:
            self.item_pk = item.pk
            self.item_name = item.name
            self.item_price = item.price
            return True
        else:
            print("VisitItemForm.__fill_item_data. item is None!")
            return False

    def __init__(self, *args, **kwargs):
        print('VisitItemForm: ', args , 'kwargs', kwargs)
        visititem = kwargs.pop('instance', None)
        if visititem:
            self.__fill_item_data(visititem.item)
            args = ({'pk':visititem.pk,'item_pk':visititem.item.pk,
            'count':visititem.count},)
        else:
            if len(args) > 0:
                item = args[0].get('item')
                count = args[0].get('count', 1)
                self.__fill_item_data(item)
                args = ({'pk':None,'item_pk':item.pk,
                'count':count},)
            else:
                print('VisitItemForm args length is zero!')

        super(VisitItemForm, self).__init__(*args, **kwargs)


class VisitForm(forms.ModelForm):
    class Meta:
        model=Visit
        fields = ['start_time', 'end_time', 'visit_reason', 'vet', 'owner']
        time_fields = {'start_time':'datetime-local','end_time':'datetime-local'}
        widgets = {'visit_reason':forms.Textarea(attrs={'rows': 5,}),
                   'owner': forms.HiddenInput(),}
        widgets.update(make_time_widgets(time_fields))

        save_after_object = ['visitanimals', 'items']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        print('VisitForm-args', *args)
        print('VisitForm-kwargs', kwargs)

        #TODO: check that all needed paramers are given

        visit = None
        if len(args) > 0:
            visit = get_object(self.Meta.model, args[0].get('id', None))
        set_instakce_to(visit, kwargs)
        super(VisitForm, self).__init__(*args, **kwargs)


        format_widgets_and_add_pk(self, visit)

        #make Owner label
        if not self.setFields(args[0], visit):
            print('VisitForm.setFields: Failed')

    def setFields(self, parameters, visit):
        self.items = []

        obj = get_object(1, Item)

        self.visititem_forms = [VisitItemForm({'item':obj, 'count':1}),
        VisitItemForm({'item':obj, 'count':1}),VisitItemForm({'item':obj, 'count':1})
        ,VisitItemForm({'item':obj, 'count':1}), VisitItemForm({'item':obj, 'count':1}),VisitItemForm({'item':obj, 'count':1})
        ,VisitItemForm({'item':obj, 'count':1})]

        if visit:
            self.fields['owner'].initial = visit.owner.pk
            self.fields['vet'].initial = visit.vet.pk
            self.owner_label = g_form_labels['owner']
            self.owner_text = str(visit.owner)

            self.items = visit.items

            self.formset = []
            for visitanimal in visit.visitanimals:
                self.formset.append(VisitAnimalForm(initial=visitanimal))

            return True
        else:
            owner_pk = parameters.get('owner', None)
            vet_pk = parameters.get('vet', None)
            #check that we have owner and vet
            if not (owner_pk and vet_pk):
                print("VisitForm->setFields: missing pk! owner_pk:", owner_pk, 'vet_pk: ', vet_pk)
                return False

            #check that objects are in DB and set them to form
            owner = get_object(owner_pk, Owner)
            vet = get_object(vet_pk, Vet)
            if owner and vet:
                self.fields['owner'].initial = owner_pk
                self.fields['vet'].initial = vet_pk
                self.owner_label = g_form_labels['owner']
                self.owner_text = str(owner)
            else:
                print("VisitForm->setFields: object not found: owner", owner, " vet: ", vet)
                return False

            formset = []
            for index in parameters.get('animals', '').split(','):
                #ignore empty indexes, should only occure when no animals in parameters
                if index == '':
                    continue
                #find animals from database
                tmp_animal = get_object(index, Animal)
                if tmp_animal:
                    formset.append(VisitAnimalForm({'animal':tmp_animal}))
                else:
                    print("VisitForm->setFields: animal not found from database. id: ", index)
                    return False
            self.formset = formset
            return True
        return False



class OwnerForm(forms.ModelForm):
    class Meta:
        model= Owner
        fields = ['name', 'address', 'phonenumber', 'email', 'other_info','animals', 'archive']
        widgets = {'name': forms.TextInput(attrs={'required': True,}),
                    'email': forms.EmailInput()}
        save_after_object = ['animals']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(OwnerForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)

    def __setFields(self, **kwargs):
        owner = kwargs.pop('instance',None)
        if not owner == None:
            self.setChoiceField(PostOffice, initial=owner.post_office)
        else:
            self.setChoiceField(PostOffice)


class AnimalFrom(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name', 'official_name', 'birthday', 'micro_num',
        'rec_num', 'tattoo', 'insurance', 'passport', 'other_info',
        'death_day']
        widgets = {'name': forms.TextInput(attrs={'required': True,}),
                    'insurance': forms.Textarea(attrs={'rows': 5,}),
                    'other_info': forms.Textarea(attrs={'rows': 5}),}
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(AnimalFrom, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)

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


class SexForm(forms.ModelForm):
    class Meta:
        model = Sex
        fields = ['name']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(SexForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(ColorForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)

class SpecieForm(forms.ModelForm):
    class Meta:
        model = Specie
        fields = ['name']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(SpecieForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)

class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = ['name']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(RaceForm, self).__init__(*args, **kwargs)
        format_widgets_and_add_pk(self)

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
