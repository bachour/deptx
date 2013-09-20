from django.db import models

from deptx.helpers import generateUUID, now
from players.models import Player


class Provenance(models.Model):
    name = models.CharField(max_length=50)
    store_id = models.IntegerField(blank=True, null=True)
    serial = models.SlugField(max_length=36, default=generateUUID)
    
    node1 = models.CharField(max_length=50, blank=True, null=True)
    attribute1 = models.CharField(max_length=50, blank=True, null=True)
    node2 = models.CharField(max_length=50, blank=True, null=True)
    attribute2 = models.CharField(max_length=50, blank=True, null=True)
    
    date = models.DateTimeField(default=now(), auto_now=True)
    
    
    def __unicode__(self):
        return self.name + " - store: " + self.store_id.__str__()

class ProvenanceLog(models.Model):
    player = models.ForeignKey(Player)
    store_id = models.IntegerField(blank=True, null=True)
    counter = models.IntegerField(default=0)
         
    def __unicode__(self):
        return self.player.firstName + self.player.lastName   
    