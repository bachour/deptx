from django.db import models

class Provenance(models.Model):
    name = models.CharField(max_length=50)
    store_id = models.IntegerField()
    
    
    def __unicode__(self):
        return self.name + " - store: " + self.store_id.__str__()
