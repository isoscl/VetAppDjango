from django import forms
from django.contrib.auth.forms import AuthenticationForm

# from VetApp.models import Vet

from VetApp.translate import g_login_text, g_form_labels, g_form_placeholders

from VetApp.models import Sex, Color, Specie, Race, Animal, Owner, PostOffice
# g_login_text = {'username_placeholder':'Nimi','password_placeholder':'Salasana',
#                 'username_text':'Käyttäjä', 'password_text':'Salasana'}

# class AnimalFort

# class ButtonWidget(forms.Widget):
#     def render(self, name, text, url, attrs=None):
#         return '''<a name="{name}" href="{url}">"{text}"</a>'''.format(name=name,url=url, text=text)


# <div class="container">
#     <div class="row" id="error-container">
#          <div class="span12">
#              <div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">×</button>test error message</div>
#            </div>
#       	</div>
#   	</div>

#<dic class="alert alert-warning"><a href="#" class"close" data-dismiss="error">x</a><strong>%s</strong></div>

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
        self.setForms()

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

    def setForms(self):
        pass

    def setChoiceField(self, class_obj, name=None):
        self.setModelChoiceField(class_obj.getText(),
        class_obj.objects.all())
        #0=list number 1=str in choice
        if name:
            tmp_object= class_obj.objects.get(name=name)
            for choice in self.fields[class_obj.getText()].choices:
                if choice[1] == tmp_object.toString():
                    self.fields[class_obj.getText()].initial = choice[0]
                    break;


    def setModelChoiceField(self,field, queryset, required=False):
        self.fields[field]=MyModelChoiceField(queryset=queryset, required=required,
        empty_label=g_form_labels['select'])
        self.setLabel(field)

    def setPosOffice(self, name=None, number=None):
        self.fields['post_office']=MyModelChoiceField(
        queryset=PostOffice.objects.all(), required=False,
        empty_label=g_form_labels['select'])

        if name and number:
            po = PostOffice.objects.get(name=name, number=number)

            for c in self.fields['post_office'].choices:
                if c[1] == po.toString():
                    self.fields['post_office'].initial = c[0]
                    break;
        self.setLabel('post_office')


class OwnerForm(BaseForm):
    class Meta:
        model= Owner
        fields = ['name', 'address', 'phonenumber', 'email', 'other_info', 'archive']
        widgets = {'name': forms.TextInput(attrs={'required': True,}),
                    'email': forms.EmailInput()}

    def __init__(self, *args, **kwargs):
        super(OwnerForm, self).__init__(*args, **kwargs)
        #self.setFields(**kwargs)
        self.setModelFileds()
        self.setPosOffice() #self.setPosOffice("Hamina", '12345')

        #PostOffice(name='Kotka', number=49990).save()

class AnimalFrom(BaseForm):
    class Meta:
        model = Animal
        fields = ['name', 'official_name', 'birthday', 'micro_num',
        'rec_num', 'tattoo', 'insurance', 'passport', 'other_info',
        'death_day']
        widgets = {'name': forms.TextInput(attrs={'required': True,}),
                    'insurance': forms.Textarea(attrs={'rows': 5,}),
                    'other_info': forms.Textarea(attrs={'rows': 5}),}

    def __init__(self, *args, **kwargs):
        super(AnimalFrom, self).__init__(*args, **kwargs)
        self.setFields(**kwargs)
        self.setModelFileds()

        # Color(name='Musta').save()
        # Sex(name='Uros').save()
        # s = Specie(name='Koira')
        # s.save()
        # Race(name='Russeli', specie=s).save()


    def setFields(self, **kwargs):
        specie = kwargs.pop('specie','')
        sex = kwargs.pop('sex','')
        race = kwargs.pop('race','')
        color = kwargs.pop('color','')
        self.setChoiceField(Specie, name=specie)
        self.setChoiceField(Sex, name=sex)
        self.setChoiceField(Race, name=race)
        self.setChoiceField(Color, name=color)

        # po = PostOffice(name='Kotka',number='12345')
        # po.save()
        # po = PostOffice(name='Kouvola',number='12345')
        # po.save()


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
