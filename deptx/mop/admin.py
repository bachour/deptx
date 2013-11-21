from django.contrib import admin
from mop.models import Mail, RequisitionInstance, RequisitionBlank, MopDocumentInstance, RandomizedDocument, TrustInstance, MopTracker
from provmanager.models import Provenance

class RandomizedDocumentAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(RandomizedDocumentAdmin,self).get_form(request, obj,**kwargs)
        form.base_fields['provenance'].queryset = form.base_fields['provenance'].queryset.filter(type=Provenance.TYPE_MOP_INSTANCE)
        return form

admin.site.register(Mail)
admin.site.register(RequisitionInstance)
admin.site.register(RequisitionBlank)
admin.site.register(RandomizedDocument, RandomizedDocumentAdmin)
admin.site.register(MopDocumentInstance)
admin.site.register(TrustInstance)
admin.site.register(MopTracker)


