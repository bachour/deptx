from django.db import models

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from players.models import Cron, Mop
from cron.models import CronDocumentInstance
from mop.models import MopDocumentInstance
    
class ActionLog(models.Model):
    ACTION_CRON_CREATED = 0
    ACTION_CRON_LOGIN = 1
    ACTION_CRON_LOGOUT = 2
    ACTION_CRON_HACK_DOCUMENT = 3
    ACTION_CRON_SOLVE_DOCUMENT = 4
    
    
    CHOICES_ACTION = (
        (ACTION_CRON_CREATED, "account created"),
        (ACTION_CRON_LOGIN, "logged in"),
        (ACTION_CRON_LOGOUT, "logged out"),
    )
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    cron = models.ForeignKey(Cron, blank=True, null=True)
    mop = models.ForeignKey(Mop, blank=True, null=True)
    action = models.IntegerField(choices=CHOICES_ACTION)
    data = models.TextField()
    
    def __unicode__(self):
        if self.cron is not None:
            name =  "Cron: %s" % self.cron.user.username
        elif self.mop is not None:
            name = "Mop: %s" % self.mop.user.username
        else:
            name = "ERROR"
        return "%s - %s" % (name, self.get_action_display())

    
class ProvLog(models.Model):
    ACTION_MOVE = 0
    ACTION_CLICK = 1
    ACTION_SUBMIT = 2
    ACTION_MEDIA = 3
    
    CHOICES_ACTION = (
        (ACTION_MOVE, "moved node"),
        (ACTION_CLICK, "clicked node/attribute"),
        (ACTION_SUBMIT, "pressed submit"),
        (ACTION_MEDIA, "opened media"),
    )
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    cronDocumentInstance = models.ForeignKey(CronDocumentInstance, blank=True, null=True)
    mopDocumentInstance = models.ForeignKey(MopDocumentInstance, blank=True, null=True)
    
    action = models.IntegerField(choices=CHOICES_ACTION)
    node1 = models.CharField(max_length=128, blank=True, null=True)
    node2 = models.CharField(max_length=128, blank=True, null=True)
    attribute1 = models.CharField(max_length=128 ,blank=True, null=True)
    attribute2 = models.CharField(max_length=128 ,blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    selected = models.NullBooleanField(blank=True, null=True)
    empty = models.NullBooleanField(blank=True, null=True)
    correct = models.NullBooleanField(blank=True, null=True)
    
    def __unicode__(self):
        if self.cronDocumentInstance is not None:
            name =  "Cron: %s (%s)" % (self.cronDocumentInstance.cron.user.username, self.cronDocumentInstance.cronDocument.serial)
        elif self.mopDocumentInstance is not None:
            name = "Mop: %s (%s)" % (self.mopDocumentInstance.mop.user.username, self.mopDocumentInstance.randomizedDocument.serial)
        else:
            name = "ERROR"
        return "%s - %s" % (name, self.get_action_display())
    