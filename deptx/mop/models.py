from django.db import models
from datetime import datetime   

from players.models import Mop
from assets.models import Unit, Task, Requisition, Document

class DocumentInstance(models.Model):
    document = models.ForeignKey(Document)
    mop = models.ForeignKey(Mop)
    
    def __unicode__(self):
        return self.document.name + " / " + self.mop.user.username


class TaskInstance(models.Model):
    STATE_ACTIVE = 2
    STATE_REPORTED = 3
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
    date = models.DateTimeField(default=datetime.now)
    used = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.blank.mop.user.username + " " + self.blank.requisition.serial + " " + self.data
    

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

    SUBJECT_NONE = 1
  
    SUBJECT_REQUEST_FORM = 101
    SUBJECT_REQUEST_TASK = 102
    SUBJECT_REQUEST_DOCUMENT = 103
        
    SUBJECT_RECEIVE_FORM = 201
    SUBJECT_RECEIVE_TASK = 202
    SUBJECT_RECEIVE_DOCUMENT = 203
    
    SUBJECT_ERROR = 211
    SUBJECT_INFORMATION = 212
    
    SUBJECT_CHOICES_SENDING = (
        (SUBJECT_NONE, "(no subject)"),
        (SUBJECT_REQUEST_FORM, "Requesting Form"),
        (SUBJECT_REQUEST_TASK, "Requesting Task"),
        (SUBJECT_REQUEST_DOCUMENT, "Requesting Document"),
    )
    
    
    SUBJECT_CHOICES_RECEIVING = (
        (SUBJECT_RECEIVE_FORM, "Assigning Form"),
        (SUBJECT_RECEIVE_TASK, "Assigning Task"),
        (SUBJECT_RECEIVE_DOCUMENT, "Assigning Document"),
        (SUBJECT_ERROR, "Error"),
        (SUBJECT_INFORMATION, "Information"),
    )
    
    SUBJECT_CHOICES = SUBJECT_CHOICES_SENDING + SUBJECT_CHOICES_RECEIVING
    
    
    mop = models.ForeignKey(Mop)
    unit = models.ForeignKey(Unit)
    date = models.DateTimeField(default=datetime.now)
    subject = models.IntegerField(choices=SUBJECT_CHOICES, default=SUBJECT_NONE)
    body = models.TextField()
    read = models.BooleanField()
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_NORMAL)
    type = models.IntegerField(choices=TYPE_CHOICES)
    
    requisitionInstance = models.ForeignKey(RequisitionInstance, null=True, blank=True)  
    
    def __unicode__(self):
        if self.subject is None:
            return "no subject"
        else:
            return self.get_subject_display()

    
    
    

    
    