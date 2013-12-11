from django.contrib import admin
from logger.models import ProvLog, ActionLog

class ActionLogAdmin(admin.ModelAdmin):
    list_filter = ('action', 'cron', 'mop', 'createdAt')
    raw_id_fields = ('cron', 'mission', 'case', 'questionInstance', 'cronDocument', 'cronDocumentInstance', 'message', 'mop', 'mail', 'mopDocumentInstance', 'requisitionInstance')


class ProvLogAdmin(admin.ModelAdmin):
    list_filter = ('action', 'cronDocumentInstance__cron', 'mopDocumentInstance__mop', 'createdAt')
    raw_id_fields = ('cronDocumentInstance', 'mopDocumentInstance')

admin.site.register(ProvLog, ProvLogAdmin)
admin.site.register(ActionLog, ActionLogAdmin)
