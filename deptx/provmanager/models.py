from django.db import models

from deptx.helpers import generateUUID

class Provenance(models.Model):
    name = models.CharField(max_length=50)
    store_id = models.IntegerField()
    serial = models.SlugField(max_length=36, default=generateUUID)
    
    
    def __unicode__(self):
        return self.name + " - store: " + self.store_id.__str__()
