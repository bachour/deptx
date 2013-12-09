from django.contrib import admin
from assets.models import Unit, Requisition, CronDocument, MopDocument, Mission, Case, CaseQuestion
from provmanager.models import Provenance

class CronDocumentAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(CronDocumentAdmin,self).get_form(request, obj,**kwargs)
        form.base_fields['provenance'].queryset = form.base_fields['provenance'].queryset.filter(type=Provenance.TYPE_CRON)
        return form

class MopDocumentAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(MopDocumentAdmin,self).get_form(request, obj,**kwargs)
        form.base_fields['provenance'].queryset = form.base_fields['provenance'].queryset.filter(type=Provenance.TYPE_MOP_TEMPLATE)
        return form

class CaseAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(CaseAdmin,self).get_form(request, obj,**kwargs)
        try:
            form.base_fields['preCase'].queryset = form.base_fields['preCase'].queryset.filter(mission=obj.mission).exclude(id=obj.id)
        except:
            form.base_fields['preCase'].queryset = Case.objects.none()
        return form


admin.site.register(Unit)
admin.site.register(Requisition)
admin.site.register(CronDocument, CronDocumentAdmin)
admin.site.register(MopDocument, MopDocumentAdmin)
admin.site.register(Mission)
admin.site.register(Case, CaseAdmin)
admin.site.register(CaseQuestion)


