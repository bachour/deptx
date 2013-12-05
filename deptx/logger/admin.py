from django.contrib import admin
from logger.models import ProvLog, ActionLog

class ActionLogAdmin(admin.ModelAdmin):
    list_filter = ('action', 'cron', 'mop', 'createdAt')

class ProvLogAdmin(admin.ModelAdmin):
    list_filter = ('action', 'cronDocumentInstance__cron', 'mopDocumentInstance__mop', 'createdAt')

admin.site.register(ProvLog, ProvLogAdmin)
admin.site.register(ActionLog, ActionLogAdmin)
