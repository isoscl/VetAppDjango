from django import forms
from django.contrib.auth.forms import AuthenticationForm

# from VetApp.models import Vet

from VetApp.translate import g_login_text, g_form_labels, g_form_placeholders

from VetApp.models import Sex, Color, Specie, Race, Animal
# g_login_text = {'username_placeholder':'Nimi','password_placeholder':'Salasana',
#                 'username_text':'Käyttäjä', 'password_text':'Salasana'}

# class AnimalFort

# class ButtonWidget(forms.Widget):
#     def render(self, name, text, url, attrs=None):
#         return '''<a name="{name}" href="{url}">"{text}"</a>'''.format(name=name,url=url, text=text)


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.setForms()

    def setLabel(self, name, text=None):
        if not text:
            text = name
        # print(name, self.fields[name].widget, self.fields[name].widget.__dict__)
        if hasattr(self.fields[name].widget, 'format'):
            self.fields[name].widget.input_type = 'date'

        self.fields[name].label = g_form_labels[text]
        self.fields[name].widget.attrs.update({'class':'form-control','placeholder':g_form_placeholders[name]})

    def setModelChoiceField(self,field, queryset, required=False):
        self.fields[field]=forms.ModelChoiceField(queryset=queryset, required=required)
        self.setLabel(field)

    def setModelFileds(self):
        for field in self.Meta().fields:
            self.setLabel(field)

    def setForms(self):
        pass


class AnimalFrom(BaseForm):
    class Meta:
        model = Animal
        fields = ['name', 'official_name', 'birthday', 'micro_num',
        'rec_num', 'tattoo', 'insurance', 'passport', 'other_info',
        'death_day']
        #widgets = {'birthday':forms.DateField(input_formats=[])}

    def __init__(self, *args, **kwargs):
        super(AnimalFrom, self).__init__(*args, **kwargs)
        self.setFields(**kwargs)
        self.setModelFileds()

    def setFields(self, **kwargs):
        specie = kwargs.pop('specie','')
        sex = kwargs.pop('sex','')
        race = kwargs.pop('race','')
        color = kwargs.pop('color','')
        self.setModelChoiceField('specie', Specie.objects.filter(name=specie))
        self.setModelChoiceField('sex', Sex.objects.filter(name=sex))
        self.setModelChoiceField('race', Race.objects.filter(name=race))
        self.setModelChoiceField('color', Color.objects.filter(name=color))



class SexForm(BaseForm):
    def setForms(self):
        self.setLabel('name', 'sex')

    class Meta:
        model = Sex
        fields = ['name']



class ColorForm(BaseForm):
    def setForms(self):
        self.setLabel('name', 'color')

    class Meta:
        model = Color
        fields = ['name']

class SpecieForm(BaseForm):
    def setForms(self):
        self.setLabel('name', 'specie')
    class Meta:
        model = Specie
        fields = ['name']

class RaceForm(BaseForm):
    def setForms(self):
        self.setLabel('name', 'race')

    class Meta:
        model = Race
        fields = ['name']

    def __init__(self, *args, **kwargs):
        specie = kwargs.pop('specie','') #there shold be defined specie what would be selected
        super(RaceForm, self).__init__(*args, **kwargs)
        self.fields['specie']=forms.ModelChoiceField(queryset=Specie.objects.filter(name=specie)) #select the correct object
        self.setLabel('specie', 'specie')

class AuthForm(AuthenticationForm):
    # class Meta:
    #     labels = {'username':g_login_text['username_text']}
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm,self).__init__(*args,**kwargs)
        self.fields['username'].label = ''
        self.fields['password'].label = ''
        self.fields['username'].widget.attrs.update({'class':'form-control','placeholder':g_login_text['username_placeholder']})
        self.fields['password'].widget.attrs.update({'class':'form-control','placeholder':g_login_text['password_placeholder']})

    def confirm_login_allowed(self, user):
        print("user", user)
        pass
