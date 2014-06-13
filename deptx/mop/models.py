from django.db import models

from players.models import Mop
from assets.models import Unit, Requisition, CronDocument, MopDocument, StoryFile
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from provmanager.models import Provenance
from mop.clearance import Clearance, getMinimumGreen, getMinimumYellow, getMinimumOrange, getMinimumRed, get_next_level_at, proposed_clearance
import deptx.friendly_id as friendly_id
import re
from django.template import Context, loader, Template
from django.core.exceptions import ValidationError
from django.contrib import messages
from deptx.helpers import now
from deptx.settings import STATIC_URL
import json
from datetime import timedelta

class MopTracker(models.Model):
    
    TUTORIAL_0_START = 0
    TUTORIAL_1_SENT_HOW_TO_REQUEST_FORM = 10
    TUTORIAL_2_SENT_HOW_TO_REQUEST_DOCUMENT = 20
    TUTORIAL_3_SENT_HOW_TO_CHECK_PROVENANCE = 30
    TUTORIAL_4_SENT_HOW_TO_SUBMIT_DOCUMENT = 40
    TUTORIAL_5_SENT_CONCLUSION = 50
    TUTORIAL_6_DONE = 60

    
    CHOICES_TUTORIAL = (
        (TUTORIAL_0_START, 'TUTORIAL_0_START'),
        (TUTORIAL_1_SENT_HOW_TO_REQUEST_FORM, 'TUTORIAL_1_SENT_HOW_TO_REQUEST_FORM'),
        (TUTORIAL_2_SENT_HOW_TO_REQUEST_DOCUMENT, 'TUTORIAL_2_SENT_HOW_TO_REQUEST_DOCUMENT'),
        (TUTORIAL_3_SENT_HOW_TO_CHECK_PROVENANCE, 'TUTORIAL_3_SENT_HOW_TO_CHECK_PROVENANCE'),
        (TUTORIAL_4_SENT_HOW_TO_SUBMIT_DOCUMENT, 'TUTORIAL_4_SENT_HOW_TO_SUBMIT_DOCUMENT'),
        (TUTORIAL_5_SENT_CONCLUSION, 'TUTORIAL_5_SENT_CONCLUSION'),
        (TUTORIAL_6_DONE, 'TUTORIAL_6_DONE'),
    )

    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    mop = models.OneToOneField(Mop, related_name="mopTracker")
    unreadEmails = models.IntegerField(default=0)
    hasCheckedInbox = models.BooleanField(default=False)
    trust = models.IntegerField(default=0)
    totalTrust = models.IntegerField(default=0)
    credit = models.IntegerField(default=0)
    clearance = models.IntegerField(choices=Clearance.CHOICES_CLEARANCE_ALL, default=Clearance.CLEARANCE_BLUE)
    
    fileUploadAllowed = models.BooleanField(default=False)
    specialStatusAllowed = models.BooleanField(default=False, help_text="Special Status is only active when Citizen Helper also has Red Clearance level (or above)")
    
    tutorial = models.IntegerField(choices=CHOICES_TUTORIAL, default=TUTORIAL_0_START)
    tutorialProvErrors = models.IntegerField(default=0)
    
    @property
    def hasSpecialStatus(self):
        if self.clearance >= Clearance.CLEARANCE_RED and self.specialStatusAllowed:
            return True
        else:
            return False
    
    @property
    def nextLevelAt(self):
        return get_next_level_at(self.clearance)
        
    def getCssUrl(self):
        if self.hasSpecialStatus:
            return STATIC_URL + 'mop/mop_color_white.css'
        else:
            return Clearance(self.clearance).getCssUrl()
    
    def getMailUrl(self):
        if self.hasSpecialStatus:
            return STATIC_URL + 'mop/mail_white.png'
        else:
            return Clearance(self.clearance).getMailUrl()
    
    def getBadgeUrl(self):
        return Clearance(self.clearance).getBadgeUrl()
    
    def addTrust(self, trust, forTotal):
        self.trust += trust
        if forTotal:
            self.totalTrust += trust
            self.check_for_promotion()
        self.save()
    
    def check_for_promotion(self):
        proposedClearance = proposed_clearance(self.totalTrust)
        if self.clearance < proposedClearance:
            self.clearance = proposedClearance
            self.save()
            promotion_email(self.mop, Mail.BODY_PERFORMANCE_PROMOTION)
    
    def check_for_demotion(self):
        proposedClearance = proposed_clearance(self.totalTrust)
        if self.clearance > proposedClearance:
            self.clearance = proposedClearance
            self.save()
            promotion_email(self.mop, Mail.BODY_PERFORMANCE_DEMOTION)
       
    def isTutorial(self):
        if self.tutorial == self.TUTORIAL_6_DONE:
            return False
        else:
            return True
    
    def __unicode__(self):
        return "%s %s %s" % (self.mop.user.username, self.trust, self.get_clearance_display())

class TrustInstance(models.Model):
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    mop = models.ForeignKey(Mop)
    oldTrust = models.IntegerField(default=0)
    newTrust = models.IntegerField(default=0)
    totalTrust = models.IntegerField(default=0)
    oldClearance = models.IntegerField(choices=Clearance.CHOICES_CLEARANCE_ALL, default=Clearance.CLEARANCE_BLUE)
    newClearance = models.IntegerField(choices=Clearance.CHOICES_CLEARANCE_ALL, default=Clearance.CLEARANCE_BLUE)
    specialStatus = models.BooleanField(default=False)
    
    def getBadgeUrl(self):
        return Clearance(self.newClearance).getBadgeUrl()
        
    def __unicode__(self):
        return "%s (%s)" % (self.mop.user.username, self.oldTrust)


class PerformancePeriod(models.Model):
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    reviewDate = models.DateField()
    reviewTime = models.TimeField(blank=True, null=True)
    processed = models.BooleanField(default=False)
    
    @property
    def startDate(self):
        performancePeriod_list = PerformancePeriod.objects.all().order_by('-reviewDate')
        for performancePeriod in performancePeriod_list:
            if performancePeriod.processed and not performancePeriod == self:
                return performancePeriod.reviewDate

    @property
    def days(self):
        days = (self.reviewDate - self.startDate).days
        return days
    
    def trustForBlue(self):
        return "1-%s" % (getMinimumGreen(self.days)-1)
    def trustForGreen(self):
        return "%s-%s" % (getMinimumGreen(self.days), getMinimumYellow(self.days)-1)
    def trustForYellow(self):
        return "%s-%s" % (getMinimumYellow(self.days), getMinimumOrange(self.days)-1)
    def trustForOrange(self):
        return "%s-%s" % (getMinimumOrange(self.days), getMinimumRed(self.days)-1)    
    def trustForRed(self):
        return "&#8805;%s" % getMinimumRed(self.days)
    
    def __unicode__(self):
        return "%s (processed: %s)" % (self.reviewDate, self.processed)

class PerformanceInstance(models.Model):
    TYPE_PROMOTION = 1
    TYPE_DEMOTION = 2
    TYPE_NEUTRAL = 3
    
    CHOICES_TYPE = (
        (TYPE_PROMOTION, "promotion"),
        (TYPE_DEMOTION, "demotion"),
        (TYPE_NEUTRAL, "neutral"),
    )
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    mop = models.ForeignKey(Mop)
    trust = models.IntegerField(default=0)
    performance = models.IntegerField(choices=Clearance.CHOICES_CLEARANCE_ALL, default=Clearance.CLEARANCE_BLUE)
    result = models.IntegerField(choices=Clearance.CHOICES_CLEARANCE_ALL, default=Clearance.CLEARANCE_BLUE)
    type = models.IntegerField(choices=CHOICES_TYPE, default=TYPE_NEUTRAL)
    period = models.ForeignKey(PerformancePeriod)
    
    @property
    def credit(self):
        credit = int(self.trust * 0.2)
        if credit <0:
            credit = 0
        return credit
    
    @property
    def rank(self):
        performanceInstance_list = PerformanceInstance.objects.filter(period=self.period).order_by('-trust')
        counter = 1
        for performanceInstance in performanceInstance_list:
            if performanceInstance.trust == self.trust:
                return counter
            else:
                counter = counter + 1
    
    def getPerformanceBadgeUrl(self):
        return Clearance(self.performance).getBadgeUrlStar()
    
    def getResultBadgeUrl(self):
        return Clearance(self.result).getBadgeUrl()
    
    def __unicode__(self):
        return "%s %s - trust: %s - clearance: %s - result: %s" % (self.period.reviewDate, self.mop.user.username, self.trust, self.get_performance_display(), self.get_type_display())
    
class RandomizedDocument(models.Model):
    mop = models.ForeignKey(Mop, blank=True, null=True)
    mopDocument = models.ForeignKey(MopDocument)
    provenance = models.OneToOneField(Provenance, related_name="randomizedDocument")
    serial = models.CharField(max_length=36, blank=True, null=True, unique=True, help_text="leave blank, will be generated by system")
    isTutorial = models.BooleanField(default=False)
    #TODO/PERHAPS replace with Due-date
    active = models.BooleanField(default=True)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    appearAt = models.DateTimeField(blank=True, null=True)
    dueAt = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        if self.active == True:
            active = "ACTIVE"
        else:
            active = "INACTIVE"
        return "%s: %s - %s (%s)" % (active, self.serial, self.mopDocument.provenance.name, self.createdAt)
    
    @property
    def unit(self):
        return self.mopDocument.unit
    
    @property
    def hasTimeLeft(self):
        if self.isTutorial:
            return True
        try:
            if self.dueAt > now():
                return True
            else:
                return False
        except:
            return True
        
    
    @property
    def hasAppeared(self):
        if self.isTutorial:
            return True
        try:
            if self.appearAt <= now():
                return True
            else:
                return False
        except:
            return True
        
    
    def getBadgeUrl(self):
        return Clearance(self.mopDocument.clearance).getBadgeUrl()
    
    def clean(self, *args, **kwargs):
        if self.isTutorial:
            try:
                randomizedDocument = RandomizedDocument.objects.get(isTutorial=True)
                if not self == randomizedDocument:
                    raise ValidationError('You can only have one document for the tutorial! Change document %s first!' % randomizedDocument.serial)
            except RandomizedDocument.DoesNotExist:
                pass
        super(RandomizedDocument, self).clean(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        return self.clean(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super(RandomizedDocument, self).save(*args, **kwargs)
        if self.id and not self.serial:
            self.serial = Clearance(self.mopDocument.clearance).generateSerial(self)
            super(RandomizedDocument, self).save()
    
class MopDocumentInstance(models.Model):
    STATUS_ACTIVE = 0
    STATUS_LIMBO = 1
    STATUS_REPORTED = 2
    STATUS_REVOKED = 3
    STATUS_HACKED = 4
    STATUS_IGNORE = 5
     
    CHOICES_STATUS = (
        (STATUS_ACTIVE, "active"),
        (STATUS_LIMBO, "limbo"),
        (STATUS_REPORTED, "reported"),
        (STATUS_REVOKED, "revoked"),
        (STATUS_HACKED, "hacked"),
        (STATUS_IGNORE, "ignore"),
    )
    
    TYPE_MOP = 0
    TYPE_CRON = 1
    
    CHOICES_TYPE = (
        (TYPE_MOP, "MOP"),
        (TYPE_CRON, "CRON"),
    )

    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    mop = models.ForeignKey(Mop)
    status = models.IntegerField(choices=CHOICES_STATUS, default=STATUS_ACTIVE)
    modified = models.BooleanField(default=False)
    correct = models.BooleanField(default=False)
    provenanceState = models.TextField(blank=True, null=True)

    #stuff needed if it is a mop-document or cron-document
    type = models.IntegerField(choices=CHOICES_TYPE, default=TYPE_MOP)
    randomizedDocument = models.ForeignKey(RandomizedDocument, blank=True, null=True)
    cronDocument = models.ForeignKey(CronDocument, blank=True, null=True)
    
    def getClearance(self):
        if self.type == self.TYPE_CRON:
            return self.cronDocument.clearance
        else:
            return self.randomizedDocument.mopDocument.clearance
    
    def getTrustFinal(self):
        clearance = Clearance(self.getClearance())
        if self.status == self.STATUS_REPORTED:
            if self.correct:
                return clearance.getTrustReportedCorrect()
            else:
                return clearance.getTrustReportedIncorrect()
        elif self.status == self.STATUS_REVOKED:
            return clearance.getTrustRevoked()
        else:
            return 0
    
    def getTrustRequested(self):
        clearance = Clearance(self.getClearance())
        return clearance.getTrustRequested()

    def getDocumentSerial(self):
        if self.type == self.TYPE_MOP:
            return self.randomizedDocument.serial
        else:
            return self.cronDocument.serial
    
    def __unicode__(self):
        return "%s" % (self.getDocumentSerial())
        
class RequisitionBlank(models.Model):
    mop = models.ForeignKey(Mop)
    requisition = models.ForeignKey(Requisition)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def __unicode__(self):
        return self.requisition.name + " - " + self.mop.user.username 

class RequisitionInstance(models.Model):
    blank = models.ForeignKey(RequisitionBlank)
    data = models.TextField(blank=True, null=True)
    used = models.BooleanField(default=False)
    trashed = models.BooleanField(default=False)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    serial = models.CharField(max_length=36, blank=True, null=True, unique=True, help_text="leave blank, will be generated by system")
    
    
    def fullSerial(self):
        return "%s-%s" % (self.blank.requisition.serial, self.serial)
    
    def __unicode__(self):
        return "%s-%s" % (self.blank.requisition.serial, self.serial)
    
    def save(self, *args, **kwargs):
        if not self.blank.requisition.category == Requisition.CATEGORY_HELP:
            self.data = re.sub("[^0-9A-Za-z-]", "", self.data)
        super(RequisitionInstance, self).save(*args, **kwargs)
        if self.id and not self.serial:
            self.serial = "%s" % (friendly_id.encode(self.id))
            super(RequisitionInstance, self).save(*args, **kwargs)

class MopFile(models.Model):
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    mop = models.ForeignKey(Mop)
    data = models.FileField(upload_to='uploads/%Y/%m/%d')   
    
    def __unicode__(self):
        return "%s %s" % (self.mop.user.username, self.data.name)

class StoryFileInstance(models.Model):
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    mop = models.ForeignKey(Mop)
    storyFile = models.ForeignKey(StoryFile)
    
    def __unicode__(self):
        return "%s %s" % (self.mop.user.username, self.storyFile.serial)

class Mail(models.Model):
    TYPE_RECEIVED = 0
    TYPE_SENT = 1
    TYPE_DRAFT = 2
    
    CHOICES_TYPE = (
        (TYPE_RECEIVED, "sent by unit"),
        (TYPE_SENT, "sent by player"),
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
    SUBJECT_REQUEST_DOCUMENT = 103
    SUBJECT_SUBMIT_DOCUMENT = 104
    SUBJECT_REQUEST_HELP = 105
    SUBJECT_SPECIAL = 106
        
    SUBJECT_RECEIVE_FORM = 201
    SUBJECT_RECEIVE_DOCUMENT = 203
    SUBJECT_REVOKE_DOCUMENT = 204
    
    SUBJECT_ERROR = 211
    SUBJECT_INFORMATION = 212
    SUBJECT_REPORT_EVALUATION = 213
    SUBJECT_HELP = 214
    SUBJECT_SPECIAL_DENIED = 215
    SUBJECT_SPECIAL_GRANTED = 216
    
    
    SUBJECT_UNCAUGHT_CASE = 301
    
    
    
    CHOICES_SUBJECT_SENDING = (
        (SUBJECT_EMPTY, "---------"),
        (SUBJECT_REQUEST_FORM, "Requesting Form"),
        (SUBJECT_REQUEST_DOCUMENT, "Requesting Document"),
        (SUBJECT_SUBMIT_DOCUMENT, "Submitting Document"),
        (SUBJECT_REQUEST_HELP, "Asking for Help"),
    )
    
    CHOICES_SUBJECT_SENDING_SPECIAL = (
        (SUBJECT_SPECIAL, "Special Status Communication"),
    )
    
    
    CHOICES_SUBJECT_RECEIVING = (
        (SUBJECT_RECEIVE_FORM, "Assigning Form"),
        (SUBJECT_RECEIVE_DOCUMENT, "Assigning Document"),
        (SUBJECT_REVOKE_DOCUMENT, "Revoking Document"),
        (SUBJECT_ERROR, "Error"),
        (SUBJECT_INFORMATION, "Information"),
        (SUBJECT_REPORT_EVALUATION, "Evaluation Result"),
        (SUBJECT_HELP, "Help"),
        (SUBJECT_UNCAUGHT_CASE, "dfjhsjdvnvewe;efhjk"),
        (SUBJECT_SPECIAL_DENIED, "Request Denied"),
        (SUBJECT_SPECIAL_GRANTED, "Request Granted"),
    )
    
    CHOICES_SUBJECT = CHOICES_SUBJECT_SENDING + CHOICES_SUBJECT_SENDING_SPECIAL + CHOICES_SUBJECT_RECEIVING
    
    BODY_UNCAUGHT_CASE = -1
    #do not set a value to zero!!! bad for checking if value is set (e.g. in templates)
    BODY_ERROR_NO_SUBJECT = 1
    
    BODY_ERROR_MISSING_FORM = 10
    BODY_ERROR_MISSING_DOCUMENT = 11
    BODY_ERROR_MISSING_UNIT = 12
    
    BODY_ERROR_WRONG_UNIT = 20
    BODY_ERROR_WRONG_FORM = 21
    BODY_ERROR_WRONG_DOCUMENT = 22
    
    BODY_ERROR_REDUNDANT_DOCUMENT = 30
        
    BODY_ERROR_UNFOUND_FORM = 40
    BODY_ERROR_UNFOUND_DOCUMENT = 41
    
    BODY_ERROR_EXISTING_FORM = 50
    BODY_ERROR_EXISTING_DOCUMENT = 51
    
    BODY_ERROR_LACKING_TRUST = 60
    
    BODY_ASSIGNING_FORM = 100
    BODY_ASSIGNING_DOCUMENT = 101
    BODY_REVOKING_DOCUMENT = 102
    
    BODY_REPORT_FAIL = 110
    BODY_REPORT_SUCCESS = 111
    
    #OLD REPORTS
    BODY_PERFORMANCE_REPORT_PROMOTION = 120
    BODY_PERFORMANCE_REPORT_DEMOTION = 121
    BODY_PERFORMANCE_REPORT_NEUTRAL = 122
    
    #NEW PROMOTIONS
    BODY_PERFORMANCE_PROMOTION = 123
    BODY_PERFORMANCE_DEMOTION = 124
    
    BODY_SPECIAL_DENIED = 150
    BODY_SPECIAL_GRANTED = 151
    BODY_SPECIAL_ALREADY = 152
    
    BODY_TUTORIAL_1_INTRO = 210
    BODY_TUTORIAL_2_DOCUMENT_REQUEST = 220
    BODY_TUTORIAL_3_TASK_COMPLETION = 230
    BODY_TUTORIAL_4a_INCORRECT_MODIFICATION = 241
    BODY_TUTORIAL_4b_INCORRECT_MODIFICATION_2 = 242
    BODY_TUTORIAL_4c_CORRECT_MODIFICATION = 243
    BODY_TUTORIAL_5_CONCLUSION = 250
    
    BODY_MANUAL = 300
    
    CHOICES_BODY_TYPE = (
        (BODY_UNCAUGHT_CASE, 'BODY_UNCAUGHT_CASE'),
        (BODY_ERROR_NO_SUBJECT, 'BODY_ERROR_NO_SUBJECT'),
        (BODY_ERROR_MISSING_FORM, 'BODY_ERROR_MISSING_FORM'),
        (BODY_ERROR_MISSING_DOCUMENT, 'BODY_ERROR_MISSING_DOCUMENT'),
        (BODY_ERROR_MISSING_UNIT, 'BODY_ERROR_MISSING_UNIT'),
        (BODY_ERROR_WRONG_UNIT, 'BODY_ERROR_WRONG_UNIT'),
        (BODY_ERROR_WRONG_FORM, 'BODY_ERROR_WRONG_FORM'),
        (BODY_ERROR_WRONG_DOCUMENT, 'BODY_ERROR_WRONG_DOCUMENT'),
        (BODY_ERROR_REDUNDANT_DOCUMENT, 'BODY_ERROR_REDUNDANT_DOCUMENT'),
        (BODY_ERROR_UNFOUND_FORM, 'BODY_ERROR_UNFOUND_FORM'),
        (BODY_ERROR_UNFOUND_DOCUMENT, 'BODY_ERROR_UNFOUND_DOCUMENT'),
        (BODY_ERROR_EXISTING_FORM, 'BODY_ERROR_EXISTING_FORM'),
        (BODY_ERROR_EXISTING_DOCUMENT, 'BODY_ERROR_EXISTING_DOCUMENT'),
        (BODY_ERROR_LACKING_TRUST, 'BODY_ERROR_LACKING_TRUST'),
        (BODY_ASSIGNING_FORM, 'BODY_ASSIGNING_FORM'),
        (BODY_ASSIGNING_DOCUMENT, 'BODY_ASSIGNING_DOCUMENT'),
        (BODY_REVOKING_DOCUMENT, 'BODY_REVOKING_DOCUMENT'), 
        (BODY_REPORT_FAIL, 'BODY_REPORT_FAIL'),
        (BODY_REPORT_SUCCESS, 'BODY_REPORT_SUCCESS'),
        (BODY_PERFORMANCE_REPORT_PROMOTION, 'BODY_PERFORMANCE_REPORT_PROMOTION'),
        (BODY_PERFORMANCE_REPORT_DEMOTION, 'BODY_PERFORMANCE_REPORT_DEMOTION'),
        (BODY_PERFORMANCE_REPORT_NEUTRAL, 'BODY_PERFORMANCE_REPORT_NEUTRAL'),
        (BODY_PERFORMANCE_PROMOTION, 'BODY_PROMOTION'),
        (BODY_PERFORMANCE_DEMOTION, 'BODY_DEOMOTION'),
        (BODY_SPECIAL_DENIED, 'BODY_SPECIAL_DENIED'),
        (BODY_SPECIAL_GRANTED, 'BODY_SPECIAL_GRANTED'),
        (BODY_SPECIAL_ALREADY, 'BODY_SPECIAL_ALREADY'),
        (BODY_TUTORIAL_1_INTRO, 'BODY_TUTORIAL_1_INTRO'),
        (BODY_TUTORIAL_2_DOCUMENT_REQUEST, 'BODY_TUTORIAL_2_DOCUMENT_REQUEST'),
        (BODY_TUTORIAL_3_TASK_COMPLETION, 'BODY_TUTORIAL_3_TASK_COMPLETION'),
        (BODY_TUTORIAL_4a_INCORRECT_MODIFICATION, 'BODY_TUTORIAL_4a_INCORRECT_MODIFICATION'),
        (BODY_TUTORIAL_4b_INCORRECT_MODIFICATION_2, 'BODY_TUTORIAL_4b_INCORRECT_MODIFICATION_2'),
        (BODY_TUTORIAL_4c_CORRECT_MODIFICATION, 'BODY_TUTORIAL_4c_CORRECT_MODIFICATION'),
        (BODY_TUTORIAL_5_CONCLUSION, 'BODY_TUTORIAL_5_CONCLUSION'),
        (BODY_MANUAL, 'BODY_MANUAL'),
    )
    
    mop = models.ForeignKey(Mop)
    unit = models.ForeignKey(Unit, blank=True, null=True)

    subject = models.IntegerField(choices=CHOICES_SUBJECT, default=SUBJECT_EMPTY, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    read = models.BooleanField(default=False)
    state = models.IntegerField(choices=CHOICES_STATE, default=STATE_NORMAL)
    type = models.IntegerField(choices=CHOICES_TYPE)
    processed = models.BooleanField(default=False)
    trust = models.IntegerField(blank=True, null=True)
    bodyType = models.IntegerField(choices=CHOICES_BODY_TYPE, blank=True, null=True)
    replyTo = models.ForeignKey('self', blank=True, null=True)
    needsReply = models.BooleanField(default=False)
        
    requisitionBlank = models.ForeignKey(RequisitionBlank, null=True, blank=True)
    requisitionInstance = models.ForeignKey(RequisitionInstance, null=True, blank=True)
    mopDocumentInstance = models.ForeignKey(MopDocumentInstance, null=True, blank=True)
    performanceInstance = models.ForeignKey(PerformanceInstance, blank=True, null=True)
    
    serial = models.CharField(max_length=36, blank=True, null=True, unique=True, help_text="leave blank, will be generated by system")
    sentAt = models.DateTimeField(default=now())
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    
    def generateBody(self):
        try:
            data = self.replyTo.requisitionInstance.data
        except:
            data = None
        mop = self.mop
        text = None
        template = None
        tutorialData = {}
        tutorialData['mopco'] = Unit.objects.get(type=Unit.TYPE_COMMUNICATIVE)
    
        if self.bodyType == self.BODY_UNCAUGHT_CASE:
            template = loader.get_template('mop/mail/uncaught_case.txt')
        elif self.bodyType == self.BODY_ERROR_NO_SUBJECT:
            text = self.unit.mail_error_no_subject
        elif self.bodyType == self.BODY_ERROR_MISSING_FORM:
            text = self.unit.mail_error_missing_form
        elif self.bodyType == self.BODY_ERROR_MISSING_DOCUMENT:
            text = self.unit.mail_error_missing_document
        elif self.bodyType == self.BODY_ERROR_MISSING_UNIT:
            template = loader.get_template('mop/mail/no_unit.txt')
        elif self.bodyType == self.BODY_ERROR_WRONG_UNIT:
            text = self.unit.mail_error_wrong_unit
            data = self.replyTo.requisitionInstance.fullSerial
        elif self.bodyType == self.BODY_ERROR_WRONG_FORM:
            text = self.unit.mail_error_wrong_form
        elif self.bodyType == self.BODY_ERROR_WRONG_DOCUMENT:
            text = self.unit.mail_error_wrong_document
        elif self.bodyType == self.BODY_ERROR_REDUNDANT_DOCUMENT:
            text = self.unit.mail_error_redundant_document
        elif self.bodyType == self.BODY_ERROR_UNFOUND_FORM:
            text = self.unit.mail_error_unfound_form
        elif self.bodyType == self.BODY_ERROR_UNFOUND_DOCUMENT:
            text = self.unit.mail_error_unfound_document
        elif self.bodyType == self.BODY_ERROR_EXISTING_FORM:
            text = self.unit.mail_error_existing_form
        elif self.bodyType == self.BODY_ERROR_EXISTING_DOCUMENT:
            text = self.unit.mail_error_existing_document
        elif self.bodyType == self.BODY_ERROR_LACKING_TRUST:
            text = self.unit.mail_error_lacking_trust
        elif self.bodyType == self.BODY_ASSIGNING_FORM:
            text = self.unit.mail_assigning_form
        elif self.bodyType == self.BODY_ASSIGNING_DOCUMENT:
            text = self.unit.mail_assigning_document
        elif self.bodyType == self.BODY_REVOKING_DOCUMENT:
            text = self.unit.mail_revoking_document
            data = self.mopDocumentInstance.getDocumentSerial()
        elif self.bodyType == self.BODY_REPORT_FAIL:
            text = self.unit.mail_report_fail
        elif self.bodyType == self.BODY_REPORT_SUCCESS:
            text = self.unit.mail_report_success
        elif self.bodyType == self.BODY_PERFORMANCE_REPORT_PROMOTION:
            template = loader.get_template('mop/mail/performance_report_promotion.txt')
            data = self.performanceInstance
        elif self.bodyType == self.BODY_PERFORMANCE_REPORT_DEMOTION:
            template = loader.get_template('mop/mail/performance_report_demotion.txt')
            data = self.performanceInstance
        elif self.bodyType == self.BODY_PERFORMANCE_REPORT_NEUTRAL:
            template = loader.get_template('mop/mail/performance_report_neutral.txt')
            data = self.performanceInstance
        elif self.bodyType == self.BODY_PERFORMANCE_PROMOTION:
            template = loader.get_template('mop/mail/promotion.txt')
        elif self.bodyType == self.BODY_PERFORMANCE_DEMOTION:
            template = loader.get_template('mop/mail/demotion.txt')
        elif self.bodyType == self.BODY_TUTORIAL_1_INTRO:
            template = loader.get_template('mop/mail/tutorial_1_intro.txt')
            tutorialData['document_requisition'] = Requisition.objects.get(type=Requisition.TYPE_TUTORIAL_REQUEST)
            tutorialData['form_requisition'] = Requisition.objects.get(type=Requisition.TYPE_INITIAL, category=Requisition.CATEGORY_FORM)
        elif self.bodyType == self.BODY_TUTORIAL_2_DOCUMENT_REQUEST:
            template = loader.get_template('mop/mail/tutorial_2_document_request.txt')
            tutorialData['document'] = RandomizedDocument.objects.get(isTutorial=True)
            tutorialData['requisition'] = Requisition.objects.get(type=Requisition.TYPE_TUTORIAL_REQUEST)
        elif self.bodyType == self.BODY_TUTORIAL_3_TASK_COMPLETION:
            template = loader.get_template('mop/mail/tutorial_3_task_completion.txt')
        elif self.bodyType == self.BODY_TUTORIAL_4a_INCORRECT_MODIFICATION:
            template = loader.get_template('mop/mail/tutorial_4a_incorrect_modification.txt')
        elif self.bodyType == self.BODY_TUTORIAL_4b_INCORRECT_MODIFICATION_2:
            template = loader.get_template('mop/mail/tutorial_4b_incorrect_modification_2.txt')
        elif self.bodyType == self.BODY_TUTORIAL_4c_CORRECT_MODIFICATION:
            template = loader.get_template('mop/mail/tutorial_4c_correct_modification.txt')
            tutorialData['document'] = RandomizedDocument.objects.get(isTutorial=True)
            tutorialData['form_requisition'] = Requisition.objects.get(type=Requisition.TYPE_INITIAL, category=Requisition.CATEGORY_FORM)
        elif self.bodyType == self.BODY_TUTORIAL_5_CONCLUSION:
            template = loader.get_template('mop/mail/tutorial_5_conclusion.txt')
        elif self.bodyType == self.BODY_SPECIAL_ALREADY:
            template = loader.get_template('mop/mail/special_already.txt')
        elif self.bodyType == self.BODY_SPECIAL_DENIED:
            template = loader.get_template('mop/mail/special_denied.txt')
        elif self.bodyType == self.BODY_SPECIAL_GRANTED:
            template = loader.get_template('mop/mail/special_granted.txt')
        elif self.bodyType == self.BODY_MANUAL:
            text = self.body
        else:
            text = self.get_bodyType_display()
        
        c = Context({"data": data, "tutorialData":tutorialData, "mop":mop})    
        if not template == None:
            output = template.render(c)
        else:
            t = Template(text)
            output = t.render(c)
        
        return output

    def clean(self, *args, **kwargs):
        if self.type == self.TYPE_SENT:
            if not self.mopDocumentInstance is None:
                if not self.mopDocumentInstance.modified:
                    raise ValidationError('You can only send a document if you have processed it.')
        super(Mail, self).clean(*args, **kwargs)

    def full_clean(self, *args, **kwargs):
        return self.clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Mail, self).save(*args, **kwargs)
        if self.id and not self.serial:
            self.serial = "%s" % (friendly_id.encode(self.id))
            super(Mail, self).save(*args, **kwargs)
    
    def __unicode__(self):
        if self.subject == None:
            subject = "no subject"
        else:
            subject = self.get_subject_display()
        if self.type == self.TYPE_RECEIVED:
            try:
                sender = self.unit.serial
            except:
                sender = None
            receiver = self.mop.user.username
            sender_receiver = "%s to %s" % (sender, receiver)
            state = "read: %s" % self.read 
        elif self.type == self.TYPE_SENT:
            try:
                receiver = self.unit.serial
            except:
                receiver = None
            sender = self.mop.user.username
            sender_receiver = "%s to %s" % (sender, receiver)
            state = "processed: %s" % self.processed
        elif self.type == self.TYPE_DRAFT:
            sender = self.mop.user.username
            sender_receiver = "draft by %s" % sender
            state = ""
            
        return "%s - %s - %s - %s (%s)" % (sender_receiver, subject, self.trust, state, self.sentAt)


def promotion_email(mop, bodyType):
    mail = Mail()
    mail.unit = Unit.objects.filter(type=Unit.TYPE_ADMINISTRATIVE)[0]
    mail.subject = Mail.SUBJECT_INFORMATION
    mail.bodyType = bodyType
    mail.type = Mail.TYPE_RECEIVED
    mail.processed = True
    mail.mop = mop
    mail.save()
    from logger.models import ActionLog
    from logger import logging
    data = json.dumps({'totalTrust':mop.mopTracker.totalTrust, 'newClearance':mop.mopTracker.clearance})
    logging.log_action(ActionLog.ACTION_MOP_RECEIVE_MAIL_PERFORMANCE, mop=mop, mail=mail, data=data)  
