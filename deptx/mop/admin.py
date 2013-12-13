from django.contrib import admin
from mop.models import Mail, RequisitionInstance, RequisitionBlank, MopDocumentInstance, RandomizedDocument, MopTracker, PerformanceInstance, PerformancePeriod
from provmanager.models import Provenance

class RandomizedDocumentAdmin(admin.ModelAdmin):
    list_filter = ('mopDocument', 'active', 'mopDocument__clearance')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(RandomizedDocumentAdmin,self).get_form(request, obj,**kwargs)
        form.base_fields['provenance'].queryset = form.base_fields['provenance'].queryset.filter(type=Provenance.TYPE_MOP_INSTANCE)
        return form

class MailAdmin(admin.ModelAdmin):
    list_filter = ('mop', 'type', 'subject', 'processed', 'read', 'unit', 'sentAt', 'bodyType')
    raw_id_fields = ('mop', 'unit', 'requisitionBlank', 'requisitionInstance', 'mopDocumentInstance', 'performanceInstance', 'replyTo')

class RequisitionInstanceAdmin(admin.ModelAdmin):
    list_filter = ('blank__mop', 'blank__requisition', 'blank__requisition__type', 'blank__requisition__unit', 'createdAt')

class MopDocumentInstanceAdmin(admin.ModelAdmin):
    list_filter = ('mop', 'status', 'randomizedDocument__mopDocument', 'modified', 'correct', 'modifiedAt')

class MopTrackerAdmin(admin.ModelAdmin):
    list_filter = ('trust', 'clearance', 'tutorial', 'tutorialProvErrors', 'modifiedAt')

admin.site.register(Mail, MailAdmin)
admin.site.register(RequisitionInstance, RequisitionInstanceAdmin)
admin.site.register(RequisitionBlank)
admin.site.register(RandomizedDocument, RandomizedDocumentAdmin)
admin.site.register(MopDocumentInstance, MopDocumentInstanceAdmin)
admin.site.register(MopTracker, MopTrackerAdmin)
admin.site.register(PerformanceInstance)
admin.site.register(PerformancePeriod)


