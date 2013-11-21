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
        
