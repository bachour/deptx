from django.contrib import admin
from logger.models import ProvLog, ActionLog

admin.site.register(ProvLog)
admin.site.register(ActionLog)
