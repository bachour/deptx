from django.contrib import admin
from cron.models import MissionInstance, CaseInstance, CronDocumentInstance


admin.site.register(MissionInstance)
admin.site.register(CaseInstance)
admin.site.register(CronDocumentInstance)
