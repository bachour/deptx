from django.contrib import admin
from mop.models import TaskInstance, Mail, RequisitionInstance, RequisitionBlank, DocumentInstance, Badge #, WeekTrust

admin.site.register(TaskInstance)
admin.site.register(Mail)
admin.site.register(RequisitionInstance)
admin.site.register(RequisitionBlank)
admin.site.register(DocumentInstance)
admin.site.register(Badge)
#admin.site.register(WeekTrust)

