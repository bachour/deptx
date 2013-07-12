from django.db import models

from deptx.helpers import generateUUID

class Unit(models.Model):
    name = models.CharField(max_length=256)
    serial = models.CharField(max_length=36, default=generateUUID)
    description = models.TextField()
    isAdministrative = models.BooleanField()
    
    def __unicode__(self):
        return self.name
    
class Requisition(models.Model):
    CATEGORY_FORM = 0
    CATEGORY_TASK = 1
    
    CATEGORY_CHOICES = (
        (CATEGORY_FORM, "form for form"),
        (CATEGORY_TASK, "form for task"),
    )
    
    
    name = models.CharField(max_length=256)
    serial = models.CharField(max_length=36, default=generateUUID)
    description = models.TextField()
    unit = models.ForeignKey(Unit)
    category = models.IntegerField(choices=CATEGORY_CHOICES)
    trust = models.IntegerField(default=25)
    isInitial = models.BooleanField()
    
    def __unicode__(self):
        return self.name

class Task(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    unit = models.ForeignKey(Unit)
    serial = models.CharField(max_length=36, default=generateUUID)
    trust = models.IntegerField(default=25)

    def __unicode__(self):
        return self.name