from django.db import models

from provmanager.models import Provenance

from deptx.helpers import generateUUID


class Unit(models.Model):
    name = models.CharField(max_length=256)
    serial = models.CharField(max_length=8, unique=True)
    description = models.TextField(default="Working on Provenance")
    tagline = models.CharField(max_length=256, default="Prov is all around you", help_text="one sentence descripion; their motto")
    isAdministrative = models.BooleanField(default=False)
    
    mail_error_no_subject = models.TextField(default="Your mail could not be filtered automatically. Please choose an appropriate subject next time.", help_text="when there is no subject selected")
    mail_error_missing_form = models.TextField(default="You did not attach a form. Please always attach a form.", help_text="when no form was attached")
    mail_error_wrong_unit = models.TextField(default="Form {{data}} cannot be processed by us. Please send it to the appropriate unit.", help_text="when the form was sent to the wrong unit")
    mail_error_wrong_form = models.TextField(default="The type of form does not match your request.", help_text="when subject and form do not match")
    mail_error_redundant_document = models.TextField(default="You have attached an unnecessary document.", help_text="when a document was attached despite not being required")
    mail_error_missing_document = models.TextField(default="Your report can only be processed if you attach a document.", help_text="trying to submit a report without attaching a document")
    mail_error_wrong_document = models.TextField(default="Attached document {{data}} does not belong to report concerning task {{task}}.", help_text="when the document does not belong to the task from the form")
    mail_error_unfound_form = models.TextField(default="Form {{data}} which you requested does not exist.", help_text="when no form with the serial could be found")
    mail_error_unfound_task = models.TextField(default="Task {{data}} which you requested does not exist within this unit.", help_text="when the requested task does not correspond to a task by this unit (or any task)")
    mail_error_unfound_document = models.TextField(default="Document {{data}} which you requested does not exist within this unit.", help_text="when the requested document does not correspond to a document by this unit (or any document)")
    mail_error_existing_form = models.TextField(default="You already have access to form {{data}}.", help_text="when the player already has the blank form")
    mail_error_existing_task = models.TextField(default="You have already been assigned to task {{data}}.", help_text="when the player has already worked on the task (and maybe even finished it)")
    mail_error_existing_document = models.TextField(default="You already have access to document {{data}}.", help_text="when the player has already gotten the document")
    mail_error_unassigned_task = models.TextField(default="We could not find task {{data}} your report is about.", help_text="when the player is not working on the task (or it is by another unit)")
    mail_assigning_form = models.TextField(default="We have assigned form {{data}} to you.", help_text="when the user gets a new form")
    mail_assigning_task = models.TextField(default="We have assigned task {{data}} to you.", help_text="when the user gets a new task")
    mail_assigning_document = models.TextField(default="We have assigned document {{data}} to you", help_text="when the user gets a new document")
    mail_report_fail = models.TextField(default="Your report {{data}} was incorrect.", help_text="when the provenance investigation was incorrect")
    mail_report_success = models.TextField(default="Good work. Report {{data}} was correct.", help_text="when the provenance investigation was correct")

    
    
    def __unicode__(self):
        return self.serial
    
class Requisition(models.Model):
    CATEGORY_FORM = 0
    CATEGORY_TASK = 1
    CATEGORY_DOCUMENT = 2
    CATEGORY_SUBMISSION = 3
    
    CATEGORY_CHOICES = (
        (CATEGORY_FORM, "form"),
        (CATEGORY_TASK, "task"),
        (CATEGORY_DOCUMENT, "document"),
        (CATEGORY_SUBMISSION, "submission"),
    )
    
    
    name = models.CharField(max_length=256)
    serial = models.CharField(max_length=36, default=generateUUID)
    unit = models.ForeignKey(Unit)
    category = models.IntegerField(choices=CATEGORY_CHOICES)
    trust = models.IntegerField(default=25)
    isInitial = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name

class Task(models.Model):
    name = models.CharField(max_length=256)
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
    
    isPublished = models.BooleanField(default=False)
    
    
    def __unicode__(self):
        return self.name + " (" + str(self.rank) + " - published: " + str(self.isPublished) + ")"

  
class Case(models.Model):
    name = models.CharField(max_length=50)
    mission = models.ForeignKey(Mission)
    rank = models.IntegerField()
    serial = models.SlugField(max_length=36, default=generateUUID)
    
    intro = models.TextField(blank=True, null=True)
    outro = models.TextField(blank=True, null=True)
    
    isPublished = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.mission.name + " - Case " + str(self.rank) + ": " + self.name + " (published: " + str(self.isPublished) + ")"

class Document(models.Model):
    name = models.CharField(max_length=256)
    serial = models.CharField(max_length=36, default=generateUUID)
    unit = models.ForeignKey(Unit)
    provenance = models.OneToOneField(Provenance, blank=True, null=True, related_name="document")
    case = models.ForeignKey(Case, blank=True, null=True)
    task = models.OneToOneField(Task, blank=True, null=True)
            
    def __unicode__(self):
        return self.name

        

