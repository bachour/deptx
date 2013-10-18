from django.contrib import admin
from assets.models import Unit, Requisition, Task, Document, Mission, Case
from provmanager.models import Provenance

class DocumentAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(DocumentAdmin,self).get_form(request, obj,**kwargs)
        # form class is created per request by modelform_factory function
        # so it's safe to modify
        #we modify the the queryset
        form.base_fields['provenance'].queryset = form.base_fields['provenance'].queryset.filter(type=Provenance.TYPE_CRON)
        return form

class TaskAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(TaskAdmin,self).get_form(request, obj,**kwargs)
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

# class CaseDocumentInline(admin.StackedInline):
#     model = DocumentAdmin
#     extra = 0
#  
# class CaseAdmin(admin.ModelAdmin):
#     inlines = [CaseDocumentInline]




admin.site.register(Unit)
admin.site.register(Requisition)
admin.site.register(Task, TaskAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Mission)
admin.site.register(Case, CaseAdmin)
#admin.site.register(Case,)


