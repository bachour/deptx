from django.db import models
from datetime import datetime   

from players.models import Mop

from deptx.helpers import generateUUID

class Task(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    episode = models.IntegerField(default=-1)
    trust = models.IntegerField(default=20)
    value = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name


class TaskState(models.Model):
    STATE_ACCESSIBLE = 0
    STATE_REQUESTED = 1
    STATE_ACTIVE = 2
    STATE_REPORTED = 3
    STATE_SOLVED = 4
    STATE_FAILED = 5
    
    STATE_CHOICES = (
        (STATE_ACCESSIBLE, "accessible"),
        (STATE_REQUESTED, "requested"),
        (STATE_ACTIVE, "active"),
        (STATE_REPORTED, "reported"),
        (STATE_SOLVED, "solved"),
        (STATE_FAILED, "failed"),
    )
    
    task = models.ForeignKey(Task)
    mop = models.ForeignKey(Mop)
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_ACCESSIBLE)
    serial = models.CharField(max_length=36, default=generateUUID)
    
    def __unicode__(self):
        return self.task.name + " / " + self.mop.user.username

class Document(models.Model):
    name = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


class Requisition(models.Model):
    TYPE_FORM = 0
    TYPE_TASK = 1
    TYPE_DOCUMENT = 2
    
    TYPE_CHOICES = (
        (TYPE_FORM, "form for a form"),
        (TYPE_TASK, "form for a task"),
        (TYPE_DOCUMENT, "form for a document")
    )
    
    mop = models.ForeignKey(Mop)
    type = models.IntegerField(choices=TYPE_CHOICES)
    data = models.CharField(max_length=256)
    date = models.DateTimeField(default=datetime.now)
    used = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.get_type_display()
    

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
    
    
    UNIT_POLICE = 1
    UNIT_MEDICAL = 2
    UNIT_TRANSPORTATION = 3
    UNIT_FOREIGN = 4
    UNIT_ADMINISTRATION = 5
    
    UNIT_CHOICES = (
        (UNIT_POLICE, "Unit of Criminal Offense"),
        (UNIT_MEDICAL, "Unit of Health"),
        (UNIT_TRANSPORTATION, "Unit of Mobility"),
        (UNIT_FOREIGN, "Unit of Foreign Affairs"),
        (UNIT_ADMINISTRATION, "Unit of Administration"),
    )
    
    SUBJECT_REQUEST_FORM = 101
    SUBJECT_REQUEST_DOCUMENT = 102
    SUBJECT_SEND_FORM = 103
    SUBJECT_SEND_DOCUMENT = 104
    
    SUBJECT_RECEIVE_FORM = 201
    SUBJECT_RECEIVE_DOCUMENT = 202
    SUBJECT_ASSIGNED_TASK = 203
    SUBJECT_ERROR = 204
    
    
    SUBJECT_CHOICES = (
        (SUBJECT_REQUEST_FORM, "Requesting Form"),
        (SUBJECT_REQUEST_DOCUMENT, "Requesting Document"),
        (SUBJECT_SEND_FORM, "Sending Form"),
        (SUBJECT_SEND_DOCUMENT, "Sending Document"),
        (SUBJECT_RECEIVE_FORM, "Requested Form"),
        (SUBJECT_RECEIVE_DOCUMENT, "Requested Document"),
        (SUBJECT_ASSIGNED_TASK, "Task assigned"),
        (SUBJECT_ERROR, "Error"),
    )
    
    
    mop = models.ForeignKey(Mop)
    unit = models.IntegerField(choices=UNIT_CHOICES, null=True, blank=True)
    date = models.DateTimeField(default=datetime.now)
    subject = models.IntegerField(choices=SUBJECT_CHOICES, null=True, blank=True)
    body = models.TextField()
    read = models.BooleanField()
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_NORMAL)
    type = models.IntegerField(choices=TYPE_CHOICES)
    
    requisition = models.ForeignKey(Requisition, null=True, blank=True)
    document = models.ForeignKey(Document, null=True, blank=True)
    
    
    def __unicode__(self):
        return self.get_subject_display()

    
    
    
    
    