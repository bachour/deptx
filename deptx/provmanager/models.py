from django.db import models

from deptx.helpers import generateUUID


class Provenance(models.Model):
    name = models.CharField(max_length=50)
    store_id = models.IntegerField(blank=True, null=True)
    serial = models.SlugField(max_length=36, default=generateUUID)
    
    node1 = models.CharField(max_length=50, blank=True, null=True)
    attribute1 = models.CharField(max_length=50, blank=True, null=True)
    node2 = models.CharField(max_length=50, blank=True, null=True)
    attribute2 = models.CharField(max_length=50, blank=True, null=True)
    
    
    def __unicode__(self):
        return self.name + " - store: " + self.store_id.__str__()
