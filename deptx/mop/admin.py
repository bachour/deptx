from django.contrib import admin
from models import Task, TaskStatus, Document, Mail

admin.site.register(Task)
admin.site.register(TaskStatus)
admin.site.register(Document)
admin.site.register(Mail)
