from django.contrib import admin
from mop.models import TaskInstance, Mail, RequisitionInstance, RequisitionBlank, DocumentInstance

admin.site.register(TaskInstance)
admin.site.register(Mail)
admin.site.register(RequisitionInstance)
admin.site.register(RequisitionBlank)
admin.site.register(DocumentInstance)

