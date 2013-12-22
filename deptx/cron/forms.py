from django.forms import ModelForm

from models import HelpMail

class HelpMailForm(ModelForm):
    class Meta:
        model = HelpMail
        fields = ['body']
     
class ControlHelpMailForm(ModelForm):
    class Meta:
        model = HelpMail
        fields = ['cron', 'body']
    
