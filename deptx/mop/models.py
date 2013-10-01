from django.db import models
from deptx.helpers import now 

from players.models import Mop
from assets.models import Unit, Task, Requisition, Document



class DocumentInstance(models.Model):
    document = models.ForeignKey(Document)
    mop = models.ForeignKey(Mop)
    
    provenanceState = models.TextField(blank=True, null=True)
    modified = models.BooleanField(default=False)
    correct = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    date = models.DateTimeField(default=now(), auto_now=True)
    
    def __unicode__(self):
        if (self.modified):
            status = "modified"
        else:
            status = "original"
        return self.document.serial + " (" + status + ")"

class TaskInstance(models.Model):
    STATE_ACTIVE = 2
    STATE_SOLVED = 4
    STATE_FAILED = 5
    
    STATE_CHOICES = (
        (STATE_ACTIVE, "active"),
        (STATE_SOLVED, "solved"),
        (STATE_FAILED, "failed"),
    )
    
    task = models.ForeignKey(Task)
    mop = models.ForeignKey(Mop)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_ACTIVE)
    date = models.DateTimeField(default=now(), auto_now=True)
    
    def __unicode__(self):
        return self.task.name + " / " + self.mop.user.username

class RequisitionBlank(models.Model):
    mop = models.ForeignKey(Mop)
    requisition = models.ForeignKey(Requisition)
    
    def __unicode__(self):
        return self.requisition.name + " - " + self.mop.user.username 

class RequisitionInstance(models.Model):
    blank = models.ForeignKey(RequisitionBlank)
    data = models.CharField(max_length=256)
    date = models.DateTimeField(default=now(), auto_now=True)
    used = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.blank.requisition.unit.serial + ": " + self.blank.requisition.serial + " (" + str(self.date) + ")"
    

class Mail(models.Model):
    TYPE_RECEIVED = 0
    TYPE_SENT = 1
    TYPE_DRAFT = 2
    
    TYPE_CHOICES = (
        (TYPE_RECEIVED, "received"),
        (TYPE_SENT, "sent"),
        (TYPE_DRAFT, "draft")
    )
    
    STATE_NORMAL = 0
    STATE_TRASHED = 1
    STATE_DELETED = 2
    
    STATE_CHOICES = (
        (STATE_NORMAL, "normal"),
        (STATE_TRASHED, "trashed"),
        (STATE_DELETED, "deleted")
    )
  
    SUBJECT_EMPTY = 1
    
    SUBJECT_REQUEST_FORM = 101
    SUBJECT_REQUEST_TASK = 102
    SUBJECT_REQUEST_DOCUMENT = 103
    SUBJECT_SUBMIT_REPORT = 104
        
    SUBJECT_RECEIVE_FORM = 201
    SUBJECT_RECEIVE_TASK = 202
    SUBJECT_RECEIVE_DOCUMENT = 203
    
    SUBJECT_ERROR = 211
    SUBJECT_INFORMATION = 212
    SUBJECT_REPORT_EVALUATION = 213
    SUBJECT_UNCAUGHT_CASE = 214
    
    SUBJECT_CHOICES_SENDING = (
        (SUBJECT_EMPTY, "---------"),
        (SUBJECT_REQUEST_FORM, "Requesting Form"),
        (SUBJECT_REQUEST_TASK, "Requesting Task"),
        (SUBJECT_REQUEST_DOCUMENT, "Requesting Document"),
        (SUBJECT_SUBMIT_REPORT, "Submitting Report"),
    )
    
    
    SUBJECT_CHOICES_RECEIVING = (
        (SUBJECT_RECEIVE_FORM, "Assigning Form"),
        (SUBJECT_RECEIVE_TASK, "Assigning Task"),
        (SUBJECT_RECEIVE_DOCUMENT, "Assigning Document"),
        (SUBJECT_ERROR, "Error"),
        (SUBJECT_INFORMATION, "Information"),
        (SUBJECT_REPORT_EVALUATION, "Task Evaluation Result"),
        (SUBJECT_UNCAUGHT_CASE, "dfjhsjdvnvewe;efhjk")
    )
    
    SUBJECT_CHOICES = SUBJECT_CHOICES_SENDING + SUBJECT_CHOICES_RECEIVING
    
    
    mop = models.ForeignKey(Mop)
    unit = models.ForeignKey(Unit, blank=True, null=True)
    date = models.DateTimeField(default=now(), auto_now=True)
    subject = models.IntegerField(choices=SUBJECT_CHOICES, default=SUBJECT_EMPTY, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    read = models.BooleanField(default=False)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_NORMAL)
    type = models.IntegerField(choices=TYPE_CHOICES)
    processed = models.BooleanField(default=False)
    
    requisitionInstance = models.ForeignKey(RequisitionInstance, null=True, blank=True)
    documentInstance = models.ForeignKey(DocumentInstance, null=True, blank=True)  
    
    def __unicode__(self):
        if self.subject is None:
            subject = "no subject"
        else:
            subject = self.get_subject_display()
        return "%s - %s - %s - processed: %s" % (self.get_type_display(), self.mop.user.username, subject, str(self.processed))

    
    
    

    
    