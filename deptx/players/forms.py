from django import forms
from django.forms import ModelForm

from players.models import Player, Mop, Cron



class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'age', 'town', 'country', 'gender']

class CronForm(ModelForm):
    class Meta:
        model = Cron
        fields = ['email', 'overSixteen']
    
    overSixteen = forms.BooleanField(label='Over Sixteen', error_messages = {'required': 'You need to be 16 or older to join Cr0n.'})
        
    def clean(self):
        if not self.cleaned_data.get('overSixteen'):
            raise forms.ValidationError('haha')
        return self.cleaned_data

class MopForm(ModelForm):
    class Meta:
        model = Mop
        fields = ['firstname', 'lastname', 'dob', 'gender', 'weight', 'height', 'marital', 'hair', 'eyes']
        
        widgets = {'dob' : forms.DateInput(attrs={'class': 'datepicker'})}
        
class MopCheckForm(ModelForm):
        
    class Meta:
        model = Mop
        fields = ['firstname', 'lastname', 'dob', 'gender', 'weight', 'height', 'marital', 'hair', 'eyes']
        
        widgets = {'dob' : forms.DateInput(attrs={'class': 'datepicker'})}
    
class PasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    serial = forms.CharField()

    def clean_serial(self):
        s = self.cleaned_data['serial']
        try:
            Mop.objects.get(serial=s)
        except:
            raise forms.ValidationError('no citizen helper with this identifier found')
        return s    
    
    def clean(self):
        cleaned_data = self.cleaned_data # individual field's clean methods have already been called
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Passwords must be identical.")
        return cleaned_data
