from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from provmanager.models import Provenance

from deptx import friendly_id
from deptx.helpers import random_chars
from mop.clearance import Clearance
from django.core.exceptions import ValidationError

class Unit(models.Model):
    
    TYPE_NORMAL = 0
    TYPE_ADMINISTRATIVE = 1
    TYPE_COMMUNICATIVE = 2
    
    CHOICES_TYPE = (
        (TYPE_NORMAL, "normal"),
        (TYPE_ADMINISTRATIVE, "administrative"),
        (TYPE_COMMUNICATIVE, "communicative"),
    )
    
    name = models.CharField(max_length=256)
    serial = models.CharField(max_length=8, unique=True)
    description = models.TextField(default="Working on Provenance")
    tagline = models.CharField(max_length=256, default="Prov is all around you", help_text="one sentence descripion; their motto")

    type = models.IntegerField(choices=CHOICES_TYPE, default=TYPE_NORMAL)

    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    mail_error_no_subject = models.TextField(default="Your mail could not be filtered automatically. Please choose an appropriate subject next time.", help_text="when there is no subject selected")
    mail_error_missing_form = models.TextField(default="You did not attach a form. Please always attach a form.", help_text="when no form was attached")
    mail_error_wrong_unit = models.TextField(default="Form {{data}} cannot be processed by us. Please send it to the appropriate unit.", help_text="when the form was sent to the wrong unit")
    mail_error_wrong_form = models.TextField(default="The type of form does not match your request.", help_text="when subject and form do not match")
    mail_error_redundant_document = models.TextField(default="You have attached an unnecessary document.", help_text="when a document was attached despite not being required")
    mail_error_missing_document = models.TextField(default="Your report can only be processed if you attach a document.", help_text="trying to submit a report without attaching a document")
    mail_error_wrong_document = models.TextField(default="Attached document {{data}} does not match the report.", help_text="when the document is not the document from the form")
    mail_error_unfound_form = models.TextField(default="Form {{data}} which you requested does not exist.", help_text="when no form with the serial could be found")
    mail_error_unfound_document = models.TextField(default="Document {{data}} which you requested does not exist.", help_text="when the requested document does not correspond to a document by this unit (or any document)")
    mail_error_existing_form = models.TextField(default="You already have access to form {{data}}.", help_text="when the player already has the blank form")
    mail_error_existing_document = models.TextField(default="You already have access to document {{data}}.", help_text="when the player has already gotten the document")
    mail_error_lacking_trust = models.TextField(default="You do not have the required amount of performance credits to request document {{data}}.", help_text="when the player does not have enough credits to 'pay' for a document")
    mail_assigning_form = models.TextField(default="We have assigned form {{data}} to you.", help_text="when the user gets a new form")
    mail_assigning_document = models.TextField(default="We have assigned document {{data}} to you", help_text="when the user gets a new document")
    mail_report_fail = models.TextField(default="Your report {{data}} was incorrect.", help_text="when the provenance investigation was incorrect")
    mail_report_success = models.TextField(default="Good work. Report {{data}} was correct.", help_text="when the provenance investigation was correct")
 
    def clean(self, *args, **kwargs):
        if self.type == self.TYPE_ADMINISTRATIVE:
            try:
                unit = Unit.objects.get(type=Unit.TYPE_ADMINISTRATIVE)
                if not self == unit:
                    raise ValidationError('You can only have one unit set as administrative! Change unit %s first!' % unit.serial)
            except Requisition.DoesNotExist:
                pass
        if self.type == self.TYPE_COMMUNICATIVE:
            try:
                unit = Unit.objects.get(type=Unit.TYPE_COMMUNICATIVE)
                if not self == unit:
                    raise ValidationError('You can only have one unit set as communicative! Change unit %s first!' % unit.serial)
            except Requisition.DoesNotExist:
                pass
        super(Unit, self).clean(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        return self.clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Unit, self).save(*args, **kwargs)
 
    def __unicode__(self):
        return self.serial

#TODO Check if unit can have this type of requisition    
class Requisition(models.Model):
    CATEGORY_FORM = 0
#   CATEGORY_TASK = 1
    CATEGORY_DOCUMENT = 2
    CATEGORY_SUBMISSION = 3
    
    CHOICES_CATEGORY = (
        (CATEGORY_FORM, "request form"),
#         (CATEGORY_TASK, "request task"),
        (CATEGORY_DOCUMENT, "request document"),
        (CATEGORY_SUBMISSION, "submit document"),
    )
    
    TYPE_NORMAL = 0
    TYPE_INITIAL = 1
    TYPE_TUTORIAL = 2
    
    CHOICES_TYPE = (
        (TYPE_NORMAL, "normal"),
        (TYPE_INITIAL, "initial"),
        (TYPE_TUTORIAL, "tutorial"),
    )
    
    name = models.CharField(max_length=256)
    serial = models.CharField(max_length=32, blank=True, null=True, unique=True, help_text="leave blank to have it generated by system")
    unit = models.ForeignKey(Unit)
    category = models.IntegerField(choices=CHOICES_CATEGORY)
    type = models.IntegerField(choices=CHOICES_TYPE, default=TYPE_NORMAL)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def get_category_acr(self):
        if self.category == self.CATEGORY_FORM:
            return "FO"
        if self.category == self.CATEGORY_DOCUMENT:
            return "DC"
        if self.category == self.CATEGORY_SUBMISSION:
            return "SU"
        else:
            return "XX"
        
    def clean(self, *args, **kwargs):
        if self.type == self.TYPE_TUTORIAL:
            try:
                requisition = Requisition.objects.get(type=Requisition.TYPE_TUTORIAL)
                raise ValidationError('You can only have one form set as the tutorial form! Change form %s first!' % requisition.serial)
            except Requisition.DoesNotExist:
                pass
        super(Requisition, self).clean(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        return self.clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Requisition, self).save(*args, **kwargs)
        if self.id and not self.serial:
            self.serial = "%s-%s-%s%s" % (self.get_category_acr(), self.unit.serial, friendly_id.encode(self.id), random_chars(size=2, chars=self.unit.serial))
            super(Requisition, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.serial



class Mission(models.Model):
    CATEGORY_CASES = 0
    CATEGORY_MOPMAKER = 1
    
    CHOICES_CATEGORY = (
        (CATEGORY_CASES, "investigate cases"),
        (CATEGORY_MOPMAKER, "create mop account"),         
    )
    
    name = models.CharField(max_length=50)
    rank = models.IntegerField(unique=True)
    serial = models.SlugField(blank=True, null=True, unique=True, help_text="leave blank to have it generated by system")
    category = models.IntegerField(choices=CHOICES_CATEGORY, default=CATEGORY_CASES)
    
    intro = models.TextField(default="ENTER INTRO FOR MISSION")
    briefing = models.TextField(default="ENTER BRIEFING FOR MISSION")
    activity = models.TextField(default="ENTER ACTIVITY TEXT FOR MISSION")
    debriefing = models.TextField(default="ENTER DEBRIEFING FOR MISSION")
    outro = models.TextField(default="ENTER OUTRO FOR MISSION")
    
    isPublished = models.BooleanField(default=False)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def save(self, *args, **kwargs):
        super(Mission, self).save(*args, **kwargs)
        if self.id and not self.serial:
            self.serial = "%s%s%s" % (random_chars(size=2), friendly_id.encode(self.id), random_chars(size=2))
            super(Mission, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name + " (" + str(self.rank) + " - published: " + str(self.isPublished) + ") " + self.serial
  
class Case(models.Model):
    name = models.CharField(max_length=50)
    mission = models.ForeignKey(Mission)
    rank = models.IntegerField()
    serial = models.SlugField(max_length=36, blank=True, null=True, unique=True, help_text="leave blank to have it generated by system")
    preCase = models.ForeignKey('self', blank=True, null=True, help_text="The preCase has to be solved before this case is accesible to the players. Before you can select a preCase, the current Case needs to be saved and added to a mission.")
    
    intro = models.TextField(blank=True, null=True)
    outro = models.TextField(blank=True, null=True)
    
    isPublished = models.BooleanField(default=False)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def save(self, *args, **kwargs):
        super(Case, self).save(*args, **kwargs)
        if self.id and not self.serial:
            self.serial = "%s%s%s" % (random_chars(size=2), friendly_id.encode(self.id), random_chars(size=2))
            super(Case, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.mission.name + " - Case " + str(self.rank) + ": " + self.name + " (published: " + str(self.isPublished) + ") " + self.serial 

class AbstractDocument(models.Model):
    class meta:
        abstract = True
    
    name = models.CharField(max_length=64)
    unit = models.ForeignKey(Unit)
    provenance = models.OneToOneField(Provenance, related_name="document")
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()

class CronDocument(AbstractDocument):
    case = models.ForeignKey(Case)
    serial = models.CharField(max_length=36, blank=True, null=True, unique=True, help_text="leave blank, will be generated by system")
    clearance = models.IntegerField(choices=Clearance.CHOICES_CLEARANCE_CRONDOCUMENT, default=Clearance.CLEARANCE_MAX)

    def __unicode__(self):
        return "%s" % (self.serial)

    def getBadgeUrl(self):
        return Clearance(self.clearance).getBadgeUrl()
    
    def save(self, *args, **kwargs):
        super(CronDocument, self).save(*args, **kwargs)
        if self.id and not self.serial:
            self.serial = Clearance(self.clearance).generateSerial(self)
            super(CronDocument, self).save(*args, **kwargs)

class MopDocument(AbstractDocument):

    clearance = models.IntegerField(choices=Clearance.CHOICES_CLEARANCE_MOPDOCUMENT, default=Clearance.CLEARANCE_LOW)
    
    def __unicode__(self):
        return "%s - %s - %s" % (self.unit.serial, self.get_clearance_display(), self.provenance.name)

