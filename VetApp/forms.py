from django import forms
from django.contrib.auth.forms import AuthenticationForm

# from VetApp.models import Vet

from VetApp.translate import g_login_text, g_form_labels, g_form_placeholders

from VetApp.models import *


from django.forms.utils import ErrorList
class DivErrorList(ErrorList):
    def __str__(self):              # __unicode__ on Python 2
        return self.as_divs()
    def as_divs(self):
        if not self: return ''
        #'<div class="form-group ">%s</div>'
        return "" # '<input class="form-control" required>%s</input>'  % ''.join([self.errorhtml(e) for e in self])

    def errorhtml(self, e):
        return '' #<dic class="alert alert-warning"><a href="#" class"close" data-dismiss="error">x</a><strong>%s</strong></div>' % e

class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if not obj:
            return 'Tyhjä'
        else:
            return  obj.toString() #"%s, %s" % (obj.name, obj.number)

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.error_class=DivErrorList
        self.setFields(**kwargs)
        self.setModelFileds()

    def setLabel(self, name, text=None):
        if not text:
            text = name

        if type(self.fields[name]) is forms.DateField :
            self.fields[name].widget.input_type = 'date'

        self.fields[name].label = g_form_labels[text]
        self.fields[name].widget.attrs.update({'class':'form-control','placeholder':g_form_placeholders[name]})

    def setModelFileds(self):
        for field in self.Meta().fields:
            self.setLabel(field)
        self.fields['pk'] = forms.IntegerField(widget = forms.HiddenInput(), required=False)

    def setFields(self, **kwargs):
        pass

    def setChoiceField(self, model_obj, initial=None):
        self.setModelChoiceField(model_obj.getText(),model_obj.objects.all())

        if initial:
            self.fields[model_obj.getText()].initial = initial.pk

        #0=list number 1=str in choice
        # if name:
        #     tmp_object= model_obj.objects.get(name=name)
        #     for choice in self.fields[model_obj.getText()].choices:
        #         if choice[1] == tmp_object.toString():
        #              choice[0]
        #             break;

    def setModelChoiceField(self,field, queryset, required=False):
        self.fields[field]=MyModelChoiceField(queryset=queryset, required=required,
        empty_label=g_form_labels['select'])
        self.setLabel(field)

    # def setPosOffice(self, name=None, number=None):
    #     self.fields['post_office']=MyModelChoiceField(
    #     queryset=PostOffice.objects.all(), required=False,
    #     empty_label=g_form_labels['select'])

        # if name and number:
        #     po = PostOffice.objects.get(name=name, number=number)
        #
        #     for c in self.fields['post_office'].choices:
        #         if c[1] == po.toString():
        #             self.fields['post_office'].initial = c[0]
        #             break;
        # self.setLabel('post_office')

class SpecieDescriptionForm(BaseForm):
    class Meta:
        model = SpecieDescription
        fields = ['text']
    def __init__(self, *args, **kwargs):
        super(AnimalFrom, self).__init__(*args, **kwargs)

    def setFields(self, **kwargs):
        self.setChoiceField(Specie)


class ItemForm(BaseForm):
    class Meta:
        model=Item
        fields=['name', 'description', 'stock_price', 'price',
        'barcode', 'count_type', 'archive']


class OwnerForm(BaseForm):
    class Meta:
        model= Owner
        fields = ['name', 'address', 'phonenumber', 'email', 'other_info', 'archive']
        widgets = {'name': forms.TextInput(attrs={'required': True,}),
                    'email': forms.EmailInput()}

    def setFields(self, **kwargs):
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

    # def __init__(self, *args, **kwargs):
    #     super(AnimalFrom, self).__init__(*args, **kwargs)
        # Color(name='Musta').save()
        # Sex(name='Uros').save()
        # s = Specie(name='Koira')
        # s.save()
        # Race(name='Russeli', specie=s).save()

    def setFields(self, **kwargs):
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



class ColorForm(BaseForm):
    class Meta:
        model = Color
        fields = ['name']

class SpecieForm(BaseForm):
    class Meta:
        model = Specie
        fields = ['name']

class RaceForm(BaseForm):
    class Meta:
        model = Race
        fields = ['name']

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
