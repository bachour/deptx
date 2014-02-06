from django.contrib import admin
from cron.models import MissionInstance, CaseInstance, CronDocumentInstance, HelpMail, CaseQuestionInstance, ChatMessage

class MissionInstanceAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'mission', 'progress', 'modifiedAt')

class CaseInstanceAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'case', 'modifiedAt')

class CronDocumentInstanceAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'cronDocument', 'solved', 'failedAttempts', 'modifiedAt')

class HelpMailAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'type', 'isRead', 'modifiedAt')

class CaseQuestionInstanceAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'question', 'correct', 'failedAttempts', 'answer1', 'answer2', 'modifiedAt')

admin.site.register(MissionInstance, MissionInstanceAdmin)
admin.site.register(CaseInstance, CaseInstanceAdmin)
admin.site.register(CronDocumentInstance, CronDocumentInstanceAdmin)
admin.site.register(HelpMail, HelpMailAdmin)
admin.site.register(CaseQuestionInstance, CaseQuestionInstanceAdmin)
admin.site.register(ChatMessage)
