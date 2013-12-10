from django.forms import ModelForm

from models import HelpMail

class HelpMailForm(ModelForm):
    class Meta:
        model = HelpMail
        fields = ['subject', 'body']
     
class ControlHelpMailForm(ModelForm):
    class Meta:
        model = HelpMail
        fields = ['cron', 'subject', 'isReply', 'body']
    
