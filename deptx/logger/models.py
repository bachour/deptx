from django.db import models
from deptx.helpers import now

from players.models import Cron, Mop


class Log(models.Model):
    date = models.DateTimeField(default=now(), auto_now=True)
    cron = models.ForeignKey(Cron, blank=True, null=True)
    mop = models.ForeignKey(Mop, blank=True, null=True)
    action = models.CharField(max_length=100, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.cron.user.username + ": " + self.action + " (" + str(self.date) + ")"