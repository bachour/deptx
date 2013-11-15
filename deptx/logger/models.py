from django.db import models
from deptx.helpers import now
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from players.models import Cron, Mop


class Log(models.Model):
    cron = models.ForeignKey(Cron, blank=True, null=True)
    mop = models.ForeignKey(Mop, blank=True, null=True)
    action = models.CharField(max_length=100, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def __unicode__(self):
        return "%s %s %s" % (self.cron.user.username, self.action, self.modifiedAt)