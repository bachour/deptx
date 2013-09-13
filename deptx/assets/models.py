from django.db import models

from provmanager.models import Provenance

from deptx.helpers import generateUUID

GRAPH_FOLDER = "graphs/"
JSON_FOLDER = "json/"

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
    CATEGORY_DOCUMENT = 2
    
    CATEGORY_CHOICES = (
        (CATEGORY_FORM, "form"),
        (CATEGORY_TASK, "task"),
        (CATEGORY_DOCUMENT, "document"),
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

class Mission(models.Model):
    name = models.CharField(max_length=50)
    rank = models.IntegerField()
    
    intro = models.TextField(blank=True, null=True)
    briefing = models.TextField(blank=True, null=True)
    debriefing = models.TextField(blank=True, null=True)
    outro = models.TextField(blank=True, null=True)
    
    
    def __unicode__(self):
        return self.name + " (" + str(self.rank) + ")"

  
class Case(models.Model):
    name = models.CharField(max_length=50)
    mission = models.ForeignKey(Mission)
    rank = models.IntegerField()
    serial = models.SlugField(max_length=36, default=generateUUID)
    
    intro = models.TextField(blank=True, null=True)
    outro = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.mission.name + " - Case " + str(self.rank) + ": " + self.name

class Document(models.Model):
    name = models.CharField(max_length=256)
    serial = models.CharField(max_length=36, default=generateUUID)
    content = models.TextField()
    unit = models.ForeignKey(Unit)
    provenance = models.OneToOneField(Provenance, blank=True, null=True, related_name="document")
    case = models.ForeignKey(Case, blank=True, null=True)
    task = models.OneToOneField(Task, blank=True, null=True)
            
    def __unicode__(self):
        return self.name
    


#class Provenance(models.Model):
#    document = models.OneToOneField(Document)
#    pdBundle = models.OneToOneField(PDBundle)
#    imagefile = models.ImageField(upload_to="graphs/", blank=True, null=True)
#   
#    def __unicode__(self):
#        return "Provenance of " + self.document.name
        

