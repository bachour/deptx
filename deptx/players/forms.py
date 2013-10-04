from django import forms
from django.forms import ModelForm

from players.models import Player, Mop



class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['firstName', 'lastName', 'email']


class MopForm(ModelForm):
    class Meta:
        model = Mop
        fields = ['firstname', 'lastname', 'dob', 'gender', 'weight', 'height', 'marital', 'hair', 'eyes']
        
        widgets = {'dob' : forms.DateInput(attrs={'class': 'datepicker'})}
        
