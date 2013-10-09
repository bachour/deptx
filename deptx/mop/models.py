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
    #TODO re-add auto_now
    date = models.DateTimeField(default=now())
    
    def getTrust(self):
        return self.document.getTrust()
    
    def save(self, *args, **kwargs):
        super(DocumentInstance, self).save(*args, **kwargs)
        #TODO what if object was not created?
        year, week, day = self.date.isocalendar()
        weekTrust, created = WeekTrust.objects.get_or_create(mop=self.mop, year=year, week=week)
        weekTrust.trust += self.getTrust()
        weekTrust.save()
        
#         trustTracker, created = TrustInstance.objects.get_or_create(mop=self.mop, documentInstance=self)
    
    def __unicode__(self):
        if (self.modified):
            status = "modified"
        else:
            status = "original"
        return self.document.serial + " (" + status + ")"

class TaskInstance(models.Model):
    STATUS_ACTIVE = 0
    STATUS_SOLVED = 1
    STATUS_FAILED = 2
    STATUS_UNSOLVED = 3
    
    CHOICES_STATUS = (
        (STATUS_ACTIVE, "active"),
        (STATUS_SOLVED, "solved"),
        (STATUS_FAILED, "failed"),
        (STATUS_UNSOLVED, "unsolved"),
    )
    
    task = models.ForeignKey(Task)
    mop = models.ForeignKey(Mop)
    status = models.IntegerField(choices=CHOICES_STATUS, default=STATUS_ACTIVE)
    date = models.DateTimeField(default=now(), auto_now=True)
    
    def getTrust(self):
        if self.status == self.STATUS_SOLVED:
            return self.task.getTrustSolved()
        elif self.status == self.STATUS_FAILED:
            return self.task.getTrustFailed()
        elif self.status == self.STATUS_UNSOLVED:
            return self.task.getTrustUnsolved()
        else:
            return 0
    
    def save(self, *args, **kwargs):
        super(TaskInstance, self).save(*args, **kwargs)
        #TODO what if object was not created?
        if not self.status == self.STATUS_ACTIVE:
            year, week, day = self.date.isocalendar()
            weekTrust, created = WeekTrust.objects.get_or_create(mop=self.mop, year=year, week=week)
            weekTrust.trust += self.getTrust()
            weekTrust.save()

#             trustTracker, created = TrustInstance.objects.get_or_create(mop=self.mop, taskInstance=self)

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
    
    CHOICES_TYPE = (
        (TYPE_RECEIVED, "received"),
        (TYPE_SENT, "sent"),
        (TYPE_DRAFT, "draft")
    )
    
    STATE_NORMAL = 0
    STATE_TRASHED = 1
    STATE_DELETED = 2
    
    CHOICES_STATE = (
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
    
    CHOICES_SUBJECT_SENDING = (
        (SUBJECT_EMPTY, "---------"),
        (SUBJECT_REQUEST_FORM, "Requesting Form"),
        (SUBJECT_REQUEST_TASK, "Requesting Task"),
        (SUBJECT_REQUEST_DOCUMENT, "Requesting Document"),
        (SUBJECT_SUBMIT_REPORT, "Submitting Report"),
    )
    
    
    CHOICES_SUBJECT_RECEIVING = (
        (SUBJECT_RECEIVE_FORM, "Assigning Form"),
        (SUBJECT_RECEIVE_TASK, "Assigning Task"),
        (SUBJECT_RECEIVE_DOCUMENT, "Assigning Document"),
        (SUBJECT_ERROR, "Error"),
        (SUBJECT_INFORMATION, "Information"),
        (SUBJECT_REPORT_EVALUATION, "Task Evaluation Result"),
        (SUBJECT_UNCAUGHT_CASE, "dfjhsjdvnvewe;efhjk")
    )
    
    CHOICES_SUBJECT = CHOICES_SUBJECT_SENDING + CHOICES_SUBJECT_RECEIVING
    
    
    mop = models.ForeignKey(Mop)
    unit = models.ForeignKey(Unit, blank=True, null=True)
    date = models.DateTimeField(default=now(), auto_now=True)
    subject = models.IntegerField(choices=CHOICES_SUBJECT, default=SUBJECT_EMPTY, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    read = models.BooleanField(default=False)
    state = models.IntegerField(choices=CHOICES_STATE, default=STATE_NORMAL)
    type = models.IntegerField(choices=CHOICES_TYPE)
    processed = models.BooleanField(default=False)
    
    requisitionInstance = models.ForeignKey(RequisitionInstance, null=True, blank=True)
    documentInstance = models.ForeignKey(DocumentInstance, null=True, blank=True)  
    
    def __unicode__(self):
        if self.subject == None:
            subject = "no subject"
        else:
            subject = self.get_subject_display()
        return "%s - %s - %s - processed: %s" % (self.get_type_display(), self.mop.user.username, subject, str(self.processed))

class WeekTrust(models.Model):
    mop = models.ForeignKey(Mop)
    trust = models.IntegerField(default=0)
    year = models.IntegerField(default=now().isocalendar()[0])
    week = models.IntegerField(default=now().isocalendar()[1])
    
    def __unicode__(self):
        return "%s - %d-%d - %d" % (self.mop.user.username, self.year, self.week, self.trust)

# class TrustInstance(models.Model):
#     mop = models.ForeignKey(Mop)
#     date = models.DateTimeField(default=now())
#     taskInstance = models.ForeignKey(TaskInstance, blank=True, null=True)
#     documentInstance = models.ForeignKey(DocumentInstance, blank=True, null=True)
#     weekModifier = models.IntegerField(default=None, blank=True, null=True)
#     #TODO add trust cost for mail errors
#     #Mail = models.ForeignKey(Mail, blank=True, null=True)
#     
#     def getTrust(self):
#         if not self.taskInstance == None:
#             return self.taskInstance.getTrust()
#         elif not self.documentInstance == None:
#             return self.documentInstance.getTrust()
#         elif not self.weekModifier == None:
#             return self.weekModifier
#         else:
#             return 0
#     
#     def getCategory(self):
#         if not self.taskInstance == None:
#             return "TASK"
#         elif not self.documentInstance == None:
#             return "DOCUMENT"
#         elif not self.weekModifier == None:
#             return "WEEK"
#         else:
#             return "!!!NOTHING!!!"
#         
#     def __unicode__(self):
#         return "%s %s %s" % (self.mop.user.username, self.getCategory(), self.getTrust())
#         
#     
#     

    
    