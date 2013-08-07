from django.contrib import admin
from cron.models import CronTracker, CaseInstance, CronDocumentInstance

admin.site.register(CronTracker)
admin.site.register(CaseInstance)
admin.site.register(CronDocumentInstance)
