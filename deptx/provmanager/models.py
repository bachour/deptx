from django.db import models

from deptx.helpers import generateUUID, now
from players.models import Cron
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class Provenance(models.Model):
    TYPE_NONE = "NONE"
    TYPE_CRON = "CRON"
    TYPE_MOP_TEMPLATE = "MOP_TEMPLATE"
    TYPE_MOP_INSTANCE = "MOP_INSTANCE"
    
    name = models.CharField(max_length=50)
    store_id = models.IntegerField(blank=True, null=True)
    serial = models.SlugField(max_length=36, default=generateUUID)
    
    node1 = models.CharField(max_length=50, blank=True, null=True)
    attribute1 = models.CharField(max_length=50, blank=True, null=True)
    node2 = models.CharField(max_length=50, blank=True, null=True)
    attribute2 = models.CharField(max_length=50, blank=True, null=True)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def getType(self):
        try:
            self.document
            return self.TYPE_CRON
        except:
            pass
        try:
            self.task
            return self.TYPE_MOP_TEMPLATE
        except:
            pass
        try:
            self.taskInstance
            return self.TYPE_MOP_INSTANCE
        except:
            pass
        return self.TYPE_NONE
    
    def __unicode__(self):
        return "%s - %s - store: %d" % (self.getType(), self.name, self.store_id)

class ProvenanceLog(models.Model):
    cron = models.ForeignKey(Cron)
    store_id = models.IntegerField(blank=True, null=True)
    counter = models.IntegerField(default=0)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
         
    def __unicode__(self):
        return self.cron.user.username   
    