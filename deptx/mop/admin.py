from django.contrib import admin
from models import Task, TaskState, Document, Mail, Requisition


admin.site.register(Task)
admin.site.register(TaskState)
admin.site.register(Document)
admin.site.register(Mail)
admin.site.register(Requisition)
