from django.db import models

from deptx.helpers import generateUUID, now
from players.models import Cron
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class Provenance(models.Model):
    TYPE_NONE = 0
    TYPE_CRON = 1
    TYPE_MOP_TEMPLATE = 2
    TYPE_MOP_INSTANCE = 3
    
    CHOICES_TYPE = (
        (TYPE_NONE, "NONE"),
        (TYPE_CRON, "CRON"),
        (TYPE_MOP_TEMPLATE, "MOP_TEMPLATE"),
        (TYPE_MOP_INSTANCE, "MOP_INSTANCE"),
    )
    
    name = models.CharField(max_length=50)
    store_id = models.IntegerField(blank=True, null=True)
    
    type = models.IntegerField(choices=CHOICES_TYPE, default=TYPE_NONE)
    
    attribute1 = models.CharField(max_length=500, blank=True, null=True)
    attribute2 = models.CharField(max_length=500, blank=True, null=True)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def __unicode__(self):
        return "%s - %s - store: %d" % (self.get_type_display(), self.name, self.store_id)

class ProvenanceLog(models.Model):
    cron = models.ForeignKey(Cron)
    store_id = models.IntegerField(blank=True, null=True)
    counter = models.IntegerField(default=0)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
         
    def __unicode__(self):
        return self.cron.user.username   
    