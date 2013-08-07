from django.forms import ModelForm

from models import Mail, RequisitionInstance

class MailForm(ModelForm):
    class Meta:
        model = Mail
        fields = ['unit', 'subject', 'requisitionInstance', 'documentInstance' ]
        
class RequisitionInstanceForm(ModelForm):
    class Meta:
        model = RequisitionInstance
        fields = ['data']
    
