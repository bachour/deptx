from django.db import models
from datetime import datetime   

from players.models import Mop

class Task(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    episode = models.IntegerField(default=-1)
    trust = models.IntegerField(default=20)
    value = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name


class TaskStatus(models.Model):
    STATUS_ACCESSIBLE = 0
    STATUS_CURRENT = 1
    STATUS_SOLVED = 2
    STATUS_FAILED = 3
    
    STATUS_CHOICES = (
        (STATUS_ACCESSIBLE, "accessible"),
        (STATUS_CURRENT, "current"),
        (STATUS_SOLVED, "solved"),
        (STATUS_FAILED, "failed"),
    )
    
    task = models.ForeignKey(Task)
    mop = models.ForeignKey(Mop)
    status = models.IntegerField(choices=STATUS_CHOICES)
    
    def __unicode__(self):
        return self.task.name + " / " + self.mop.user.username

class Document(models.Model):
    name = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name

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
    
    UNIT_CHOICES = (
        (UNIT_POLICE, "Unit of Criminal Offense"),
        (UNIT_MEDICAL, "Unit of Health"),
        (UNIT_TRANSPORTATION, "Unit of Mobility"),
        (UNIT_FOREIGN, "Unit of Foreign Affairs"),
    )
    
    SUBJECT_REQUEST_FORM = 101
    SUBJECT_REQUEST_DOCUMENT = 102
    SUBJECT_SEND_FORM = 103
    SUBJECT_SEND_DOCUMENT = 104
    
    SUBJECT_RECEIVE_FORM = 201
    SUBJECT_RECEIVE_DOCUMENT = 202
    
    
    SUBJECT_CHOICES = (
        (SUBJECT_REQUEST_FORM, "Requesting Form"),
        (SUBJECT_REQUEST_DOCUMENT, "Requesting Document"),
        (SUBJECT_SEND_FORM, "Sending Form"),
        (SUBJECT_SEND_DOCUMENT, "Sending Document"),
        (SUBJECT_RECEIVE_FORM, "Requested Form"),
        (SUBJECT_RECEIVE_DOCUMENT, "Requested Document"),
    )
    
    
    mop = models.ForeignKey(Mop)
    unit = models.IntegerField(choices=UNIT_CHOICES, null=True, blank=True)
    date = models.DateTimeField(default=datetime.now)
    subject = models.IntegerField(choices=SUBJECT_CHOICES, null=True, blank=True)
    body = models.TextField()
    attachement = models.ForeignKey(Document, null=True, blank=True)
    read = models.BooleanField()
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_NORMAL)
    type = models.IntegerField(choices=TYPE_CHOICES)
    
    def __unicode__(self):
        return self.get_subject_display()