from django.forms import ModelForm
from django import forms

from models import HelpMail#, ChatMessage
from players.models import Cron

class HelpMailForm(ModelForm):
    class Meta:
        model = HelpMail
        fields = ['body']
     
class ControlHelpMailForm(ModelForm):
    cron = forms.ModelChoiceField(queryset=Cron.objects.order_by('user__username'))
    class Meta:
        model = HelpMail
        fields = ['cron', 'body']

# class ChatForm(ModelForm):
#     class Meta:
#         model = ChatMessage
#         fields = ['message' ]
    
