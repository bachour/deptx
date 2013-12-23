from django.forms import ModelForm
from models import Mail, RequisitionInstance
from django import forms

class MailForm(ModelForm):
    class Meta:
        model = Mail
        fields = ['unit', 'subject', 'requisitionInstance', 'mopDocumentInstance' ]
        
class RequisitionInstanceForm(ModelForm):
    class Meta:
        model = RequisitionInstance
        fields = ['data']
        
class ControlMailForm(ModelForm):
    class Meta:
        model = Mail
        fields = ['mop', 'unit', 'subject', 'trust', 'body']
    
class MopFileForm(forms.Form):
    data= forms.FileField(
        label='Select a file to upload',
        help_text='max. 2 megabytes'
    )