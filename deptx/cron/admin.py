from django.contrib import admin
from cron.models import MissionInstance, CaseInstance, CronDocumentInstance, HelpMail, CaseQuestionInstance, ChatMessage, RiddleAttempt, OperationTracker

class MissionInstanceAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'mission', 'progress', 'modifiedAt')

class CaseInstanceAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'case', 'modifiedAt')

class CronDocumentInstanceAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'cronDocument', 'solved', 'failedAttempts', 'modifiedAt')

class HelpMailAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'type', 'isRead', 'modifiedAt')

class CaseQuestionInstanceAdmin(admin.ModelAdmin):
    list_filter = ('cron', 'question__case', 'question', 'correct', 'submitted', 'isBad', 'failedAttempts', 'modifiedAt')

class RiddleAttemptAdmin(admin.ModelAdmin):
    list_filter = ('correct', 'riddle__rank', 'attempt', 'cron')

admin.site.register(MissionInstance, MissionInstanceAdmin)
admin.site.register(CaseInstance, CaseInstanceAdmin)
admin.site.register(CronDocumentInstance, CronDocumentInstanceAdmin)
admin.site.register(HelpMail, HelpMailAdmin)
admin.site.register(CaseQuestionInstance, CaseQuestionInstanceAdmin)
admin.site.register(ChatMessage)
admin.site.register(RiddleAttempt, RiddleAttemptAdmin)
admin.site.register(OperationTracker)
