from django.contrib import admin
from mop.models import Badge
#from mop.models import TaskInstance, Mail, RequisitionInstance, RequisitionBlank, DocumentInstance, Badge #, WeekTrust
from provmanager.models import Provenance

#class TaskInstanceAdmin(admin.ModelAdmin):
#    def get_form(self, request, obj=None, **kwargs):
#        form = super(TaskInstanceAdmin,self).get_form(request, obj,**kwargs)
#        form.base_fields['provenance'].queryset = form.base_fields['provenance'].queryset.filter(type=Provenance.TYPE_MOP_INSTANCE)
#        return form

#admin.site.register(TaskInstance, TaskInstanceAdmin)
#admin.site.register(Mail)
#admin.site.register(RequisitionInstance)
#admin.site.register(RequisitionBlank)
#admin.site.register(DocumentInstance)
admin.site.register(Badge)
#admin.site.register(WeekTrust)

