from django import forms
from django.contrib.auth.forms import AuthenticationForm

# from VetApp.models import Vet

from VetApp.translate import g_login_text, g_form_labels, g_form_placeholders,g_count_type_list

from VetApp import models
from VetApp.models import *
from VetApp.items import *

from datetime import datetime, date

import json

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




def make_js_query(_type):
    return '''object_query(request, response, \'{0}\')'''.format(_type)

class TableField(object):
    def __init__(self,_type,name, objects=[], link=True, delete=True, add=True):
        self.error = None
        if _type in models.__all__:
            self._type=_type
        else:
            self._type = None
            self.error = 'Can not create table with type: '+ str(_type)
        self.name = name
        self.objects = objects
        self.link = link
        self.delete = delete
        self.add = add

    def __str__(self):
        return create_table(_type = self._type, name = self.name,
                            objects=self.objects, link=self.link,
                            delete=self.delete, add=self.add)

def create_table_name(_type, name):
    return _type + "_" + name + "_table"

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
        <button type="button" id="{0}-add-btn" class="btn btn-primary" onclick="addButtonFunction('Animal','',true)"> Add </button>
        </div>'''.format(table_name)
    html += '''<table id="{0}" class="table table-striped table-hover table-condensed">
            <tr>
                <th style="display:none" width="0%"></th>'''.format(table_name)

    if _type:
        header_list = eval('models.'+_type).table_header_string_list()

        for i in range(1, len(header_list)):
            html += '<th >%s</th>' % g_form_labels[header_list[i]]

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
            table_row += create_html_table_cell('''<button type="button" class="btn btn-danger"
            onclick="$(this).closest(\'tr\').remove()";>X</button>''')

        html += (table_row + '</tr>')

    return html + '''</table>'''


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
    type={4} {5} {6} {8} value={7}></{0}></td>'''.format(html_type, name, placeholder, _class,
    input_type, ('' if not maxlength else 'maxlength="{}"'.format(maxlength)),
    ('' if not required else 'required'), value, other_tags)

    return html

class CharField(object):
    def __init__(self, name, value="", max_length=255, required=False, label='True'):
        self.name = name
        self.max_length = max_length
        self.label = label
        self.required = required
        self.error = None
        self.set_value(value)

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input',self.value,
        input_type='text', maxlength=self.max_length,label=self.label,
        required=self.required)

    def set_value(self, value):
        value = str(value)
        if len(value) < self.max_length and ((len(value) > 0) if self.required else True):
            self.value = value
            return True
        else:
            self.value = ''
            self.error = "Too long string"
            return False

class HiddenField(object):
    def __init__(self, name, value='', max_length=255):
        self.name = name
        self.max_length = max_length
        self.error = None
        self.set_value(value)


    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], html_type='input', value=self.value,
        input_type='hidden', maxlength=self.max_length, label=False)

    def set_value(self, value):
        if len(str(value)) < self.max_length:
            self.value = str(value)
            return True
        else:
            self.value = ''
            self.error = "Too long string"
            return False

class TextField(object):
    def __init__(self, name, value="", max_length=500, required=False,
    label='True', cols=40, rows=5):
        self.name = name
        self.max_length = max_length
        self.label = label
        self.required = required
        self.cols=cols
        self.rows=rows
        self.error = None
        self.set_value(value)

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'textarea',self.value,
        input_type='text', maxlength=self.max_length, label=self.label,
        required=self.required, other_tags='cols="{0}" rows="{1}"'.format(
        self.cols, self.rows))

    def set_value(self, value):
        value = str(value)
        if len(value) < self.max_length and ((len(value) > 0) if self.required else True):
            self.value = value
            return True
        else:
            self.value = ''
            self.error = "Too long string"
            return False

class EmailField(object):
    def __init__(self, name, value="", max_length=50, required=False, label='True'):
        self.name = name
        self.max_length = max_length
        self.label = label
        self.required = required
        self.error = None
        self.set_value(value)

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input',self.value,
        input_type='email', maxlength=self.max_length,label=self.label,
        required=self.required)

    def set_value(self, value):
        value = str(value)
        if len(value) < self.max_length:
            if '@' in value:
                self.value = value
                return True
            elif value == '':
                if self.required:
                    self.value = ''
                    self.error = "Field is required"
                    return False
                else:
                    self.value = ''
                    return True
            else:
                self.value = ''
                self.error = "@ is missing"
                return False
        else:
            self.value = ''
            self.error = "Too long string"
            return False

class DateTimeField(object):
    def __init__(self, name, value="", required=False, label='True'):
        self.name = name
        self.label = label
        self.required = required
        self.error = None
        self.set_value(value)

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input',self.value,
        input_type='datetime-local', maxlength='',label=self.label,
        required=self.required)

    def set_value(self, value):
        print("Check what is this value (DateTime): ", value)
        if(value == '' or value == None):
            if not self.required:
                self.value = datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)
                return True
            else:
                self.error = "Field is required"
                self.value = ''
                return False
        elif(False): #TODO implement string to datetime convertion
            pass
            return True
        else:
            self.error = "can not convert given value to datetime"
            return False

class DateField(object):
    def __init__(self, name, value="", required=False, label='True'):
        self.name = name
        self.label = label
        self.required = required
        self.error = None
        self.set_value(value)

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input',self.value,
        input_type='date', maxlength='',label=self.label,
        required=self.required)

    def set_value(self, value):
        print("Check what is this value (Date): ", value)
        if(value == '' or value == None):
            if not self.required:
                self.value = date(year=2000, month=1, day=1)
                return True
            else:
                self.error = "Field is required"
                self.value = ''
                return False
        elif(False): #TODO implement string to datetime convertion
            pass
            return True
        else:
            self.error = "can not convert given value to datetime"
            return False

class BooleanField(object):
    def __init__(self, name, label='True', value=False):
        self.name = name
        self.label = label
        self.error = None
        self.set_value(value)

    def __str__(self):
        return generate_html_input_field("form-control",self.name,
        g_form_placeholders[self.name], 'input',value=self.value,
        input_type='checkbox', maxlength='',label=self.label,
        required=False)

    def set_value(self, value):
        if type(value == bool):
            self.value = value
            return True
        elif type(value) == str and value.lower() in ['true', 'false']:
            self.value = (value.lower() == 'true')
            return True
        else:
            self.error = 'Can not convert value to bool'
            self.value = False
            return False

class ForeignKeyField(object):
    def __init__(self, name, selected_id=None, required=False, label=True,options=[]):
        self.name = name
        self.required = required
        self.label = label
        self.options = options
        self.error = None

        if isinstance(selected_id, int):
            self.selected_id = selected_id
        elif isinstance(selected_id, str) and selected_id.isdigit():
            self.selected_id = int(selected_id)
        else:
            self.selected_id = selected_id #TODO convert to None!
            if selected_id != None:
                self.error = "Can not conver selected_id to integer"
            elif self.required:
                self.error = "Field is required"
            else:
                pass

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

def model_field_to_form_field(field, value=''):
    #get type from field type string
    _type = str(type(field)).split('.')[-1][:-2]
    print("Field type is: ", _type, 'value: ', value)
    if(_type == 'CharField'):
        return CharField(name=field.name, max_length=field.max_length,
         required = not field.blank, value=value)# field.help_text)
    elif(_type == 'AutoField'):
        return HiddenField(name=field.name, value=value)
    elif(_type == 'TextField'):
        return TextField(name=field.name, max_length=field.max_length,
         required = not field.blank, value=value)
    elif(_type == 'EmailField'):
        return EmailField(name=field.name, max_length=field.max_length,
        required = not field.blank, value=value)
    elif(_type == 'BooleanField'):
        return BooleanField(name=field.name, value=value)
    elif(_type == 'DateTimeField'):
        return DateTimeField(name=field.name, required = not field.blank, value=value)
    elif(_type == 'DateField'):
        return DateField(name=field.name, required = not field.blank, value=value)
    elif(_type == 'ForeignKey'):
        return ForeignKeyField(name=field.name, required = not field.blank,
        options=field.related_model.objects.all(), selected_id=(value.pk if hasattr(value, 'pk') else None))
    elif(_type == 'DecimalField'):
        #<input class="form-control" id="id_price" max="99999" min="0"
        #name="price" placeholder="Hinta" step="0.05" type="number" />
        pass
    # elif(_type == ''):
    #     pass
    else:
        return None

def get_model_class_from_form(form_self):
    return eval(form_self.__class__.__name__[:-4])

def get_errors_from_form(form_self):
    model_class = get_model_class_from_form(form_self)
    errors = {}

    #check if any field has errors
    for i in range(0,len(model_class._meta.fields)):
        name = str(model_class._meta.fields[i]).split('.')[-1]
        error = getattr(form_self, name).error
        if error:
            print("get_errors_from_form, Found error: ", error)
            errors['field_'+name] = error

    #check if any table has errors
    for i in range(0,len(model_class._meta.many_to_many)):
        name = model_class._meta.many_to_many[i].name
        error = getattr(form_self, name).error
        if error:
            print("get_errors_from_form, Found error: ", error)
            errors['field_'+name] = error

    #check if the actual form has errors
    if len(form_self.errors) > 0:
        errors[form_self.__class__.__name__] = form_self.errors

    if len(errors) == 0:
        return None
    else:
        return errors


def _clean_data_for_table(data, object_model):
    print('Data type is: ',type(data), ' data is: ', data)

    objects = []
    if type(data) is str:
        for obj in json.loads('['+data+']'):
            db_obj = object_model.objects.get(pk=obj['pk'])
            if db_obj:
                objects.append(db_obj)
            else:
                print("obejct with that pk was not found, pk=",obj['pk'])
    else:
        objects = data.all()
    return objects


def __generate_fields(form_self, data = {}, table_options={}):
    #generate basic fields
    model_class = get_model_class_from_form(form_self)

    for i in range(0,len(model_class._meta.fields)):
        field_name = str(model_class._meta.fields[i]).split('.')[-1]
        field = model_field_to_form_field(model_class._meta.fields[i],
                        data[field_name] if field_name in data else '')
        if(field):
            setattr(form_self, field_name, field)
        else:
            form_self.errors.append("model_field_to_form_field could not make field for "+ field_name)
            print("model_field_to_form_field could not make field for", field_name)

    #=getattr(model, model_class._meta.many_to_many[i].name).all()
    #generate many_to_many tables

    for i in range(0,len(model_class._meta.many_to_many)):
        field_name = model_class._meta.many_to_many[i].name
        table_dict = table_options[field_name] if field_name in table_options else {}
        table_object_model = model_class._meta.many_to_many[i].related_model
        field = TableField(_type=table_object_model.__name__,
            name=table_dict['name'] if 'name' in table_dict else '',
            objects= _clean_data_for_table(data[field_name], table_object_model) if data else [],
            link=table_dict['link'] if 'link' in table_dict else True,
            delete=table_dict['delete'] if 'delete' in table_dict else True,
            add=table_dict['add'] if 'add' in table_dict else True)
        setattr(form_self, field_name, field)

#generate
def _form_generic_init(form_self, args, table_options={}):
    form_self.errors = []

    model_class = get_model_class_from_form(form_self)

    #get field names
    form_self.field_names = []
    for i in range(0,len(model_class._meta.fields)):
        form_self.field_names.append(str(model_class._meta.fields[i]).split('.')[-1])
    #get field names for many to many relations
    form_self.many_to_many_fields_names = []
    for i in range(0,len(model_class._meta.many_to_many)):
        form_self.many_to_many_fields_names.append(model_class._meta.many_to_many[i].name)

    #Choose what kind of event is making this form
    if len(args) > 0 and ('id' in args[0]) and args[0]['id'] != '':
        #we should have model in databace
        model = model_class.objects.get(pk=args[0]['id'])
        form_self.model = model
        if model != None:
            #fill data dict with data from args or from model
            data = {}

            for field_name in form_self.field_names:
                if field_name in args[0]:
                    data[field_name] = args[0][field_name]
                else:
                    data[field_name] = getattr(model,field_name)

            for field_name in form_self.many_to_many_fields_names:
                if field_name in args[0]:
                    data[field_name] = args[0][field_name]
                else:
                    data[field_name] = getattr(model,field_name)

            __generate_fields(form_self, data = data, table_options=table_options)
        else:
            form_self.errors.append("No model with id: " + str(args[0]['id']))
            __generate_fields(form_self, data = {}, table_options=table_options) #make empty form
    else:
        if len(args) > 0:
            __generate_fields(form_self, data = args[0], table_options=table_options)
        else:
            __generate_fields(form_self, data = {}, table_options=table_options)


#saves the data stored in form object to database
def save_form_data(form_self):
    new_model = False
    #check if form data is for new model
    if not hasattr(form_self, 'model'):
        form_self.model = get_model_class_from_form(form_self)() #create empty model
        new_model = True

    for field_name in form_self.field_names:
        field = getattr(form_self, field_name)
        if hasattr(field, 'value'):
            setattr(form_self.model,field_name, field.value)
        elif hasattr(field, 'selected_id'):
            setattr(form_self.model,field_name, field.selected_id)
        else:
            print("save_form_data, Can not get data from field, no value or selected_id found")


    #save before many_to_many relations, because new model do not yet have pk
    #so those relations can not be created
    if new_model:
        form_self.model.save()

    for field_name in form_self.many_to_many_fields_names:
        setattr(form_self.model,field_name, getattr(form_self, field_name).objects)

    form_self.model.save()

    return True  #TODO: iplement failure handling

class AnimalForm(object):
    def __init__(self, *args, **kwargs):
        print('Type: ',type(self), ": args: ", args, ' kwargs: ', kwargs)
        _form_generic_init(self, args=args)

class VetForm(object):
    def __init__(self, *args, **kwargs):
        print('Type: ',type(self), ": args: ", args, ' kwargs: ', kwargs)
        _form_generic_init(self, args=args)

#Possible uses
# args = {} is when user wants to create new ownermodel_class
# args = {'id': ['123']} is when user wants to open user
#
class OwnerForm(object):
    def __init__(self, *args, **kwargs):
        print('Type: ',type(self), ": args: ", args, ' kwargs: ', kwargs)
        _form_generic_init(self, args=args, table_options={'animals':{
        'name':'',
        'link':True,
        'delete': True,
        'add':True
        }})

class SpecieDescriptionForm(forms.ModelForm):
    class Meta:
        model = SpecieDescription
        fields = ['text']
        labels = translate_labels(fields)

    def __init__(self, *args, **kwargs):
        super(SpecieDescriptionForm, self).__init__(*args, **kwargs)
        format_widgets(self)

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
