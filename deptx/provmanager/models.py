from django.db import models

class Provenance(models.Model):
    store_id = models.IntegerField()
    
    def __unicode__(self):
        return "store: " + self.store_id.__str__()
