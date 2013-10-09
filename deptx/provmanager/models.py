from django.db import models

from deptx.helpers import generateUUID, now
from players.models import Cron
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class Provenance(models.Model):
    name = models.CharField(max_length=50)
    store_id = models.IntegerField(blank=True, null=True)
    serial = models.SlugField(max_length=36, default=generateUUID)
    
    node1 = models.CharField(max_length=50, blank=True, null=True)
    attribute1 = models.CharField(max_length=50, blank=True, null=True)
    node2 = models.CharField(max_length=50, blank=True, null=True)
    attribute2 = models.CharField(max_length=50, blank=True, null=True)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    
    def __unicode__(self):
        return self.name + " - store: " + self.store_id.__str__()

class ProvenanceLog(models.Model):
    cron = models.ForeignKey(Cron)
    store_id = models.IntegerField(blank=True, null=True)
    counter = models.IntegerField(default=0)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
         
    def __unicode__(self):
        return self.cron.user.username   
    