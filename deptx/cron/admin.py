from django.contrib import admin
from cron.models import MissionInstance, CaseInstance, CronDocumentInstance, HelpMail, CaseQuestionInstance

admin.site.register(MissionInstance)
admin.site.register(CaseInstance)
admin.site.register(CronDocumentInstance)
admin.site.register(HelpMail)
admin.site.register(CaseQuestionInstance)
