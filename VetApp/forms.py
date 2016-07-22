from django import forms
from django.contrib.auth.forms import AuthenticationForm

# from VetApp.models import Vet

from VetApp.translate import g_login_text, g_form_labels, g_form_placeholders,g_count_type_list

from VetApp import models
from VetApp.models import *
from VetApp.items import *

from datetime import datetime

import logging

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

def set_instance_to(obj, kwargs):
    if obj:
        kwargs.update({'instance': obj})

def clean_pk(_pk):
    if (type(_pk) is str and _pk.isdigit()) or (type(_pk) is int):
        return int(_pk)
    return None

def get_object(_pk, obj):
    _pk = clean_pk(_pk)
    if _pk != None:
        try:
            return obj.objects.get(pk=int(_pk))
        except ObjectDoesNotExist:
            print("Can not find object:", obj, " with id:", _pk)
            return None #TODO: this error should be handled
    return None



def set_pk(self, obj):
    _pk = None
    if obj:
        _pk = obj.pk
    self.fields['pk'] = forms.IntegerField(widget = forms.HiddenInput(), required=False, initial=_pk)


def format_widgets(self):
    if hasattr(self,'Meta'): #TODO: remove this old when changed to new
        for field in self.Meta().fields:
            self.fields[field].widget.attrs.update({'class':'form-control','placeholder':g_form_placeholders[field]})
    else:
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class':'form-control','placeholder':g_form_placeholders[field]})

def model_attrs_to_tuple(model):
    args = {}
    for key in model._meta.get_fields():
        if hasattr(model,key.name):
            args[key.name] = getattr(model,key.name)
    return (args,) #"cast" dict to tuple

def create_table_name(_type, name):
    return _type + "_" + name + "_table"


def make_js_query(_type):
    return '''object_query(request, response, \'{0}\')'''.format(_type)

class TableField(object):
    def __init__(self,_type,name, objects=[], link=True, delete=True, add=True):
        self._type=_type
        self.name = name
        self.objects = objects
        self.link = link
        self.delete = delete
        self.add = add

    def __str__(self):
        return create_table(_type = self._type, name = self.name,
                            objects=self.objects, link=self.link,
                            delete=self.delete, add=self.add)

def create_html_table_cell(string, hidden=False):
    if(hidden):
        return '<td style="display:none" width="0%"">' + string + '</td>'
    else:
        return '<td>' + string + '</td>'

def create_table(_type, name, objects=[], link=True, delete=True, add=True):
    table_name = create_table_name(_type,name)
    html = ''
    if add:
        html += '''<div class="ui-widget">
          <input id="{0}-search"> </input>
        <button id="{0}-add-btn" class="btn btn-primary"> Add </button>
        </div>'''.format(table_name)
    html += '''<table id="{0}" class="table table-striped table-hover table-condensed">
            <tr>
                <th style="display:none" width="0%"></th>'''.format(table_name)

    if _type in models.__all__:
        header_list = eval('models.'+_type).table_header_string_list()

        for i in range(1, len(header_list)):
            html += '<th >%s</th>' % g_form_labels[header_list[i]]
    else:
        print("ERROR: forms.py create_table() can not find object named: " + _type)

    if delete:
        html += '<th></th>'

    html += '</tr>' # last cell for button

    for obj in objects:
        model_dict = models.model_to_dict(obj)

        table_row = "<tr>"
        for key in obj.table_header_string_list():
            if( link  and key == 'name'):
                table_row += create_html_table_cell('<a target="_blank" href="/'+ _type.lower() +'/?id='+model_dict['pk']+'">' + model_dict[key] + '</a>')
            elif( key == 'pk'):
                table_row += create_html_table_cell(model_dict[key], True)
            else:
                table_row += create_html_table_cell(model_dict[key])

        if delete:
            table_row += create_html_table_cell('''<button class="btn btn-danger"
            onclick="$(this).closest(\'tr\').remove()";>X</button>''')

        html += (table_row + '</tr>')

    return html + '''</table>'''

class SpecieDescriptionForm(forms.ModelForm):
    class Meta:
        model = SpecieDescription
        fields = ['text']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(SpecieDescriptionForm, self).__init__(*args, **kwargs)
        format_widgets(self)

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
        format_widgets(self)

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
        format_widgets(self)
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
        format_widgets(self)


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
        set_instance_to(visit, kwargs)

        super(VisitForm, self).__init__(*args, **kwargs)

        format_widgets(self)
        set_pk(self, visit)

        #make Owner label
        if len(args) == 0 or not self.setFields(args[0], visit):
            print('VisitForm.setFields: Failed')
            #TODO: set error message

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


class OwnerForm2():
    def __init__(self, *args, **kwargs):
        pass

    name = forms.CharField(label=g_form_labels['name'], max_length=100)
    address = forms.CharField(label=g_form_labels['address'], max_length=100, required=False)

    #  = models.ForeignKey('PostOffice',  on_delete=models.CASCADE, blank=True, null=True)
    #post_office = forms.ModelChoiceField(queryset=PostOffice.objects.all())
    #animals = forms.ModelMultipleChoiceField(queryset=Animal.objects,required = False)

    phonenumber = forms.CharField(label=g_form_labels['phonenumber'], max_length=100, required=False)
    email = forms.CharField(label=g_form_labels['address'], max_length=100, required=False, widget=forms.EmailInput())
    other_info = forms.CharField(label=g_form_labels['other_info'], max_length=500, required=False)

    archive = forms.BooleanField(initial=False, required = False) #if reguired will say it is required
    id = forms.CharField(widget = forms.HiddenInput(), required = False)


def generate_html_input_field(_class,name, placeholder, html_type, value="",
    input_type='text',maxlength=None, label=True, required=False, other_tags=""):
    html = '<tr>'
    if(label):
        html += '''<th><label for="id_{0}">{1}:</label></th>'''.format(name,
        g_form_labels[name])
    html += '''<td><{0} class="{3}" id="id_{1}" name="{1}" placeholder="{2}"
    type={4} {5} {6} {8}>{7}</{0}></td>'''.format(html_type, name, placeholder, _class,
    input_type, ('' if not maxlength else 'maxlength="{}"'.format(maxlength)),
    ('' if not required else 'required'), value, other_tags)

    return html

class CharField(object):
    def __init__(self, name, value="", max_length=255, required=False, label='True'):
        self.name = name
        self.value = value
        self.max_length = max_length
        self.label = label
        self.required = required

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input',self.value,
        input_type='text', maxlength=self.max_length,label=self.label,
        required=self.required)

class HiddenField(object):
    def __init__(self, name, value=''):
        self.name = name
        self.value = value

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], html_type='input', value=self.value,
        input_type='hidden', maxlength='', label=False)

class TextField(object):
    def __init__(self, name, value="", max_length=500, required=False,
    label='True', cols=40, rows=5):
        self.name = name
        self.value = value
        self.max_length = max_length
        self.label = label
        self.required = required
        self.cols=cols
        self.rows=rows

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'textarea',self.value,
        input_type='text', maxlength=self.max_length, label=self.label,
        required=self.required, other_tags='cols="{0}" rows="{1}"'.format(
        self.cols, self.rows))

class EmailField(object):
    def __init__(self, name, value="", max_length=50, required=False, label='True'):
        self.name = name
        self.value = value
        self.label = label
        self.max_length = max_length
        self.required = required

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input',self.value,
        input_type='email', maxlength=self.max_length,label=self.label,
        required=self.required)

class DateTimeField(object):
    def __init__(self, name, value="", required=False, label='True'):
        self.name = name
        self.value = value
        self.label = label
        self.required = required

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input',self.value,
        input_type='datetime-local', maxlength='',label=self.label,
        required=self.required)

class BooleanField(object):
    def __init__(self, name, label='True'):
        self.name = name
        self.label = label

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input','',
        input_type='checkbox', maxlength='',label=self.label,
        required=False)

class ForeignKeyField(object):
    def __init__(self, name, selected_id=None, required=False, label=True,options=[]):
        self.name = name
        self.selected_id = selected_id
        self.required = required
        self.label = label
        self.options = options

    def __str__(self):
        html = '<tr>'
        if self.label:
            html += '<th><label for="id_{0}">{1}:</label></th>'.format(self.name,
            g_form_labels[self.name])
        html += '''<td><select class="form-control" id="id_{0}"
        name="{0}" placeholder="{1}">'''.format(self.name,g_form_placeholders[self.name])

        html += '''<option value="" {0}>---------</option>'''.format(
        'selected="selected"' if not self.selected_id else '')
        for model in self.options:
            html += '''<option value="{0}" {2}>{1}</option>'''.format(model.pk, str(model),
            'selected="selected"' if self.selected_id == model.pk else '')

        return html + '</select></td></tr>'

def model_field_to_form_field(field):
    #get type from field type string
    _type = _type = str(type(field)).split('.')[-1][:-2]
    print("Field type is: ", _type)
    if(_type == 'CharField'):
        return CharField(name=field.name, max_length=field.max_length,
         required = not field.blank)# field.help_text)
    elif(_type == 'AutoField'):
        return HiddenField(name=field.name)
    elif(_type == 'TextField'):
        return TextField(name=field.name, max_length=field.max_length,
         required = not field.blank)
    elif(_type == 'EmailField'):
        return EmailField(name=field.name, max_length=field.max_length,
        required = not field.blank)
    elif(_type == 'BooleanField'):
        return BooleanField(name=field.name)
    elif(_type == 'DateTimeField'):
        return DateTimeField(name=field.name, max_length=field.max_length,
         required = not field.blank)
    elif(_type == 'ForeignKey'):
        return ForeignKeyField(name=field.name, required = not field.blank,
        options=field.related_model.objects.all())
    elif(_type == 'DecimalField'):
        #<input class="form-control" id="id_price" max="99999" min="0"
        #name="price" placeholder="Hinta" step="0.05" type="number" />
        pass
    # elif(_type == ''):
    #     pass
    else:
        return None

def genereate_fields(form_self, many_to_many_options={}):
    #find responding model
    if( form_self and form_self.__class__ and form_self.__class__.__name__ and
        (form_self.__class__.__name__[:-4] in models.__all__ )):
        #eval model
        model = eval(form_self.__class__.__name__[:-4])


        #generate basic fields
        for i in range(0,len(model._meta.fields)):
            print("Making field: ", model._meta.fields[i])
            field = model_field_to_form_field(model._meta.fields[i])
            if(field):
                setattr(form_self, field.name, field)
            else:
                print("model_field_to_form_field could not make field for", model._meta.fields[i])

        #generate many_to_many tables
        for i in range(0,len(model._meta.many_to_many)):
            field = TableField(_type=model._meta.many_to_many[i].related_model.__name__,
                            name='', objects=[], link=True, delete=True, add=True)
            setattr(form_self, model._meta.many_to_many[i].name, field)

        return True
    return False

class OwnerForm(object):
    def __init__(self, *args, **kwargs):
        print("OwnerForm: args: ", args, ' kwargs: ', kwargs)

        if(genereate_fields(self)):
            print("Initialization ok")
        else:
            print("Error at Initialization")

    def __str__(self):
        return '<b>test</b>'
        # print(generate_html_input_field("form-control",'name', 'placeholder', 'input', 'text', label=True))

        #print(self.__class__.__name__[:-4])

        # print(type(Owner._meta.fields[0]))
        # print(Owner._meta.many_to_many[0])
        # print()

        #Owner._meta.related_objects has linked fields like Visits

        # for i in range(0,len(Owner._meta.fields)):
        #     field = Owner._meta.fields[i]
        #     #if(str(type(field)).split('.')[-1][:-2] == 'ForeignKey'):
        #         #print(field.related_model.objects.all())
        #     print(str(type(field)).split('.')[-1][:-2], field.name, field.blank, field.max_length, field.help_text)

            # if ('django.db.models.field' in str(type(Owner.__dict__[key])) ):
            #     print(str(type(Owner.__dict__[key])))


    # def __repr__(self):
    #     return '<%(cls)s bound=%(bound)s, valid=%(valid)s, fields=(%(fields)s)>' % {
    #         'cls': self.__class__.__name__,
    #         'bound': True,#self.is_bound,
    #         'valid': True, #is_valid,
    #         'fields': ';'.join([self.name, self.animal])#self.fields),
    #     }
        #return '<a> HEI </a>'



class OwnerForm2(forms.Form):
    name = forms.CharField(label=g_form_labels['name'], max_length=100)
    address = forms.CharField(label=g_form_labels['address'], max_length=100, required=False)

    #  = models.ForeignKey('PostOffice',  on_delete=models.CASCADE, blank=True, null=True)
    #post_office = forms.ModelChoiceField(queryset=PostOffice.objects.all())
    #animals = forms.ModelMultipleChoiceField(queryset=Animal.objects,required = False)

    phonenumber = forms.CharField(label=g_form_labels['phonenumber'], max_length=100, required=False)
    email = forms.CharField(label=g_form_labels['address'], max_length=100, required=False, widget=forms.EmailInput())
    other_info = forms.CharField(label=g_form_labels['other_info'], max_length=500, required=False)

    archive = forms.BooleanField(initial=False, required = False) #if reguired will say it is required
    id = forms.CharField(widget = forms.HiddenInput(), required = False)



    def __init__(self, *args, **kwargs):

        print("args: ", args)
        print("kwargs: ", kwargs)

        class only_all():
            def all():
                return []

        animal_query = []
        if len(args) == 1:
            owner = get_object(args[0].get('id', None),Owner)

            # owner.animals = [get_object(args[0].get('id', None),Animal)]
            # owner.save()

            if owner:
                args = model_attrs_to_tuple(owner)
                animal_query = args[0]['animals']
                args[0]['animals'] = None
                print("Args are: ",args)
            else:
                logging.error("Owner not found")
                pass #TODO:error!
        else:
            pass #pass on arguments as they are

        super(OwnerForm, self).__init__(*args, **kwargs)

        #self.fields['animals'] = args[0]['animals']
        print("animal query: ", animal_query)
        #self.fields['animals'] = animal_query

        format_widgets(self)
        print(self.fields)

class OwnerForm_old(forms.ModelForm):
    class Meta:
        model= Owner
        fields = ['name', 'address', 'phonenumber', 'email', 'other_info','animals', 'archive']
        widgets = {'name': forms.TextInput(attrs={'required': True,}),
                    'email': forms.EmailInput()}
        save_after_object = ['animals']
        labels = translate_labels(fields)



    def __init__(self, *args, **kwargs):
        owner = None

        print(args)

        if len(args) > 0:
            owner = get_object(args[0].get('id', None),self.Meta.model)
            args = (self.getArgsFromModel(owner),)
            #django object to list
            args[0]['animals'] = args[0]['animals'].all()
            args[0]['pk'] = owner.pk
            print("Owner animal list: ",args[0]['animals'])

        super(OwnerForm, self).__init__(*args, **kwargs)
        format_widgets(self)

        print("Owner fields: ",self.fields)
        #help(self.fields["animals"])

#self.fields['pk'] = forms.IntegerField(widget = forms.HiddenInput(),
#required=False, initial=_pk)

    # def __setFields(self, **kwargs):
    #     owner = kwargs.pop('instance',None)
    #     if not owner == None:
    #         self.setChoiceField(PostOffice, initial=owner.post_office)
    #     else:
    #         self.setChoiceField(PostOffice)


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
        format_widgets(self)

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
        format_widgets(self)

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(ColorForm, self).__init__(*args, **kwargs)
        format_widgets(self)

class SpecieForm(forms.ModelForm):
    class Meta:
        model = Specie
        fields = ['name']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(SpecieForm, self).__init__(*args, **kwargs)
        format_widgets(self)

class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = ['name']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(RaceForm, self).__init__(*args, **kwargs)
        format_widgets(self)

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
