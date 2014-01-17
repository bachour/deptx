from django.db import models

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from players.models import Cron, Mop
from assets.models import Mission, Case, Requisition, CronDocument, StoryFile
from cron.models import CronDocumentInstance, MissionInstance, CaseInstance, HelpMail, CaseQuestionInstance
from mop.models import MopDocumentInstance, Mail, MopTracker, RequisitionInstance, MopFile
    
class ActionLog(models.Model):
    ACTION_CRON_CREATED = 0
    ACTION_CRON_ACTIVATED = 1
    ACTION_CRON_VIEW_STUDY = 2
    ACTION_CRON_LOGIN = 3
    ACTION_CRON_LOGOUT = 4
    
    ACTION_CRON_VIEW_INDEX = 10
    ACTION_CRON_VIEW_PROFILE = 11
    ACTION_CRON_VIEW_ARCHIVE = 12
    ACTION_CRON_VIEW_MESSAGES = 13
    ACTION_CRON_VIEW_MESSAGES_COMPOSE = 14
    ACTION_CRON_VIEW_FLUFF = 15
    
    ACTION_CRON_VIEW_MISSION_INTRO = 20
    ACTION_CRON_VIEW_MISSION_BRIEFING = 21
    ACTION_CRON_VIEW_MISSION_CASES = 22
    ACTION_CRON_VIEW_MISSION_DEBRIEFING = 23
    ACTION_CRON_VIEW_MISSION_OUTRO = 24
    
    ACTION_CRON_VIEW_CASE_INTRO = 30
    ACTION_CRON_VIEW_PROVENANCE = 31
    ACTION_CRON_VIEW_CASE_OUTRO = 32
    ACTION_CRON_VIEW_CASE_REPORT = 33
    
    ACTION_CRON_PROVENANCE_SUBMIT = 40
    ACTION_CRON_MESSAGE_SEND = 41
    ACTION_CRON_HACK_DOCUMENT = 42
    ACTION_CRON_MESSAGE_RECEIVE = 43
    ACTION_CRON_REPORT_SUBMIT = 44

    
    ACTION_MOP_CREATED = 100
    ACTION_MOP_LOGIN = 101
    ACTION_MOP_LOGOUT = 102
    
    ACTION_MOP_VIEW_INDEX = 109
    ACTION_MOP_VIEW_GUIDEBOOK = 110
    ACTION_MOP_VIEW_PERFORMANCE = 111
    ACTION_MOP_VIEW_COMPOSE = 112
    ACTION_MOP_VIEW_EDIT = 113
    ACTION_MOP_VIEW_INBOX = 114
    ACTION_MOP_VIEW_OUTBOX = 115
    ACTION_MOP_VIEW_DRAFT = 116
    ACTION_MOP_VIEW_TRASH = 117
    ACTION_MOP_VIEW_MAIL = 118
    ACTION_MOP_VIEW_FORMS_BLANKS = 119
    ACTION_MOP_VIEW_FORMS_FILL = 120
    ACTION_MOP_VIEW_FORMS_SIGNED = 121
    ACTION_MOP_VIEW_FORMS_ARCHIVE = 122
    ACTION_MOP_VIEW_DOCUMENTS_POOL = 123
    ACTION_MOP_VIEW_DOCUMENTS_DRAWER = 124
    ACTION_MOP_VIEW_DOCUMENTS_ARCHIVE = 125
    ACTION_MOP_VIEW_PROVENANCE = 126
    ACTION_MOP_VIEW_PROVENANCE_NO_CLEARANCE = 127
    ACTION_MOP_VIEW_FILES = 128
    ACTION_MOP_VIEW_STORY_FILE = 129
    
    ACTION_MOP_MAIL_SEND = 130
    ACTION_MOP_MAIL_DRAFT = 131
    ACTION_MOP_MAIL_TRASH = 132
    ACTION_MOP_MAIL_UNTRASH = 133
    ACTION_MOP_MAIL_COMPOSE_WITH_FORM = 134
    
    ACTION_MOP_FORM_SIGN = 140
    ACTION_MOP_FORM_TRASH = 141
    
    ACTION_MOP_PROVENANCE_SUBMIT = 150
    
    ACTION_MOP_RECEIVE_MAIL_ERROR = 160
    ACTION_MOP_RECEIVE_MAIL_FORM = 161
    ACTION_MOP_RECEIVE_MAIL_DOCUMENT = 162
    ACTION_MOP_RECEIVE_MAIL_REPORT = 163
    ACTION_MOP_RECEIVE_MAIL_TUTORIAL = 164
    ACTION_MOP_RECEIVE_MAIL_PERFORMANCE = 165
    ACTION_MOP_RECEIVE_MAIL_MANUAL = 166
    
    ACTION_MOP_TUTORIAL_PROGRESS = 170
    
    ACTION_MOP_FILE_UPLOAD = 180
    
    
    
    CHOICES_ACTION = (
        (ACTION_CRON_CREATED, "ACTION_CRON_CREATED"),
        (ACTION_CRON_ACTIVATED, "ACTION_CRON_ACTIVATED"),
        (ACTION_CRON_VIEW_STUDY, "ACTION_CRON_VIEW_STUDY"),
        (ACTION_CRON_LOGIN, "ACTION_CRON_LOGIN"),
        (ACTION_CRON_LOGOUT, "ACTION_CRON_LOGOUT"),
        (ACTION_CRON_VIEW_INDEX, "ACTION_CRON_VIEW_INDEX"),
        (ACTION_CRON_VIEW_PROFILE, "ACTION_CRON_VIEW_PROFILE"),
        (ACTION_CRON_VIEW_ARCHIVE, "ACTION_CRON_VIEW_ARCHIVE"),
        (ACTION_CRON_VIEW_MESSAGES, "ACTION_CRON_VIEW_MESSAGES"),
        (ACTION_CRON_VIEW_MESSAGES_COMPOSE, "ACTION_CRON_VIEW_MESSAGES_COMPOSE"),
        (ACTION_CRON_VIEW_FLUFF, "ACTION_CRON_VIEW_FLUFF"),
        (ACTION_CRON_VIEW_MISSION_INTRO, "ACTION_CRON_VIEW_MISSION_INTRO"),
        (ACTION_CRON_VIEW_MISSION_BRIEFING, "ACTION_CRON_VIEW_MISSION_BRIEFING"),
        (ACTION_CRON_VIEW_MISSION_CASES, "ACTION_CRON_VIEW_MISSION_CASES"),
        (ACTION_CRON_VIEW_MISSION_DEBRIEFING, "ACTION_CRON_VIEW_MISSION_DEBRIEFING"),
        (ACTION_CRON_VIEW_MISSION_OUTRO, "ACTION_CRON_VIEW_MISSION_OUTRO"),
        (ACTION_CRON_VIEW_CASE_INTRO, "ACTION_CRON_VIEW_CASE_INTRO"),
        (ACTION_CRON_VIEW_PROVENANCE, "ACTION_CRON_VIEW_PROVENANCE"),
        (ACTION_CRON_VIEW_CASE_OUTRO, "ACTION_CRON_VIEW_CASE_OUTRO"),
        (ACTION_CRON_VIEW_CASE_REPORT, "ACTION_CRON_VIEW_CASE_REPORT"),
        (ACTION_CRON_PROVENANCE_SUBMIT, "ACTION_CRON_PROVENANCE_SUBMIT"),
        (ACTION_CRON_MESSAGE_SEND, "ACTION_CRON_MESSAGE_SEND"),
        (ACTION_CRON_HACK_DOCUMENT, "ACTION_CRON_HACK_DOCUMENT"),
        (ACTION_CRON_MESSAGE_RECEIVE, "ACTION_CRON_MESSAGE_RECEIVE"),
        (ACTION_CRON_REPORT_SUBMIT, "ACTION_CRON_REPORT_SUBMIT"),
        (ACTION_MOP_CREATED, "ACTION_MOP_CREATED"),
        (ACTION_MOP_LOGIN, "ACTION_MOP_LOGIN"),
        (ACTION_MOP_LOGOUT, "ACTION_MOP_LOGOUT"),
        (ACTION_MOP_VIEW_INDEX, "ACTION_MOP_VIEW_INDEX"),
        (ACTION_MOP_VIEW_GUIDEBOOK, "ACTION_MOP_VIEW_GUIDEBOOK"),
        (ACTION_MOP_VIEW_PERFORMANCE, "ACTION_MOP_VIEW_PERFORMANCE"),
        (ACTION_MOP_VIEW_COMPOSE, "ACTION_MOP_VIEW_COMPOSE"),
        (ACTION_MOP_VIEW_EDIT, "ACTION_MOP_VIEW_EDIT"),
        (ACTION_MOP_VIEW_INBOX, "ACTION_MOP_VIEW_INBOX"),
        (ACTION_MOP_VIEW_OUTBOX, "ACTION_MOP_VIEW_OUTBOX"),
        (ACTION_MOP_VIEW_DRAFT, "ACTION_MOP_VIEW_DRAFT"),
        (ACTION_MOP_VIEW_TRASH, "ACTION_MOP_VIEW_TRASH"),
        (ACTION_MOP_VIEW_MAIL, "ACTION_MOP_VIEW_MAIL"),
        (ACTION_MOP_VIEW_FORMS_BLANKS, "ACTION_MOP_VIEW_FORMS_BLANKS"),
        (ACTION_MOP_VIEW_FORMS_FILL, "ACTION_MOP_VIEW_FORMS_FILL"),
        (ACTION_MOP_VIEW_FORMS_SIGNED, "ACTION_MOP_VIEW_FORMS_SIGNED"),
        (ACTION_MOP_VIEW_FORMS_ARCHIVE, "ACTION_MOP_VIEW_FORMS_ARCHIVE"),
        (ACTION_MOP_VIEW_DOCUMENTS_POOL, "ACTION_MOP_VIEW_DOCUMENTS_POOL"),
        (ACTION_MOP_VIEW_DOCUMENTS_DRAWER, "ACTION_MOP_VIEW_DOCUMENTS_DRAWER"),
        (ACTION_MOP_VIEW_DOCUMENTS_ARCHIVE, "ACTION_MOP_VIEW_DOCUMENTS_ARCHIVE"),
        (ACTION_MOP_VIEW_PROVENANCE, "ACTION_MOP_VIEW_PROVENANCE"),
        (ACTION_MOP_VIEW_PROVENANCE_NO_CLEARANCE, "ACTION_MOP_VIEW_PROVENANCE_NO_CLEARANCE"),
        (ACTION_MOP_VIEW_FILES, "ACTION_MOP_VIEW_FILES"),
        (ACTION_MOP_VIEW_STORY_FILE, "ACTION_MOP_VIEW_STORY_FILE"),
        (ACTION_MOP_MAIL_SEND, "ACTION_MOP_MAIL_SEND"),
        (ACTION_MOP_MAIL_DRAFT, "ACTION_MOP_MAIL_DRAFT"),
        (ACTION_MOP_MAIL_TRASH, "ACTION_MOP_MAIL_TRASH"),
        (ACTION_MOP_MAIL_UNTRASH, "ACTION_MOP_MAIL_UNTRASH"),
        (ACTION_MOP_MAIL_COMPOSE_WITH_FORM, "ACTION_MOP_MAIL_COMPOSE_WITH_FORM"),
        (ACTION_MOP_FORM_SIGN, "ACTION_MOP_FORM_SIGN "),
        (ACTION_MOP_FORM_TRASH, "ACTION_MOP_FORM_TRASH"),
        (ACTION_MOP_PROVENANCE_SUBMIT, "ACTION_MOP_PROVENANCE_SUBMIT"),
        (ACTION_MOP_RECEIVE_MAIL_ERROR, "ACTION_MOP_RECEIVE_MAIL_ERROR"),
        (ACTION_MOP_RECEIVE_MAIL_FORM, "ACTION_MOP_RECEIVE_MAIL_FORM"),
        (ACTION_MOP_RECEIVE_MAIL_DOCUMENT, "ACTION_MOP_RECEIVE_MAIL_DOCUMENT"),
        (ACTION_MOP_RECEIVE_MAIL_REPORT, "ACTION_MOP_RECEIVE_MAIL_REPORT"),
        (ACTION_MOP_RECEIVE_MAIL_TUTORIAL, "ACTION_MOP_RECEIVE_MAIL_TUTORIAL"),
        (ACTION_MOP_RECEIVE_MAIL_PERFORMANCE, "ACTION_MOP_RECEIVE_MAIL_PERFORMANCE"),
        (ACTION_MOP_RECEIVE_MAIL_MANUAL, "ACTION_MOP_RECEIVE_MAIL_MANUAL"),
        (ACTION_MOP_TUTORIAL_PROGRESS, "ACTION_MOP_TUTORIAL_PROGRESS"),
        (ACTION_MOP_FILE_UPLOAD, "ACTION_MOP_FILE_UPLOAD")
    )
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    action = models.IntegerField(choices=CHOICES_ACTION)
    
    cron = models.ForeignKey(Cron, blank=True, null=True)
    fluff = models.CharField(max_length=128, blank=True, null=True)
    mission = models.ForeignKey(Mission, blank=True, null=True)
    missionState = models.IntegerField(choices=MissionInstance.CHOICES_PROGRESS, blank=True, null=True)
    case = models.ForeignKey(Case, blank=True, null=True)
    caseSolved = models.NullBooleanField(blank=True, null=True)
    caseDocumentsSolved = models.NullBooleanField(blank=True, null=True)
    caseQuestionsSolved = models.NullBooleanField(blank=True, null=True)
    questionInstance = models.ForeignKey(CaseQuestionInstance, blank=True, null=True)
    questionInstanceCorrect = models.NullBooleanField(blank=True, null=True)
    cronDocument = models.ForeignKey(CronDocument, blank=True, null=True)
    cronDocumentInstance = models.ForeignKey(CronDocumentInstance, blank=True, null=True)
    cronDocumentInstanceCorrect = models.NullBooleanField(blank=True, null=True)
    message = models.ForeignKey(HelpMail, blank=True, null=True)
    successfulHack = models.NullBooleanField(blank=True, null=True)
    
    mop = models.ForeignKey(Mop, blank=True, null=True)
    mail = models.ForeignKey(Mail, blank=True, null=True)
    mopDocumentInstance = models.ForeignKey(MopDocumentInstance, blank=True, null=True)
    mopDocumentInstanceCorrect = models.NullBooleanField(blank=True, null=True)
    requisitionInstance = models.ForeignKey(RequisitionInstance, blank=True, null=True)
    tutorialProgress = models.IntegerField(choices=MopTracker.CHOICES_TUTORIAL, blank=True, null=True)
    mopFile = models.ForeignKey(MopFile, blank=True, null=True)
    storyFile = models.ForeignKey(StoryFile, blank=True, null=True)
    
    data = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        if self.cron is not None:
            name =  "Cron: %s" % self.cron.user.username
        elif self.mop is not None:
            name = "Mop: %s" % self.mop.user.username
        else:
            name = "ERROR"
        return "%s - %s (%s)" % (name, self.get_action_display(), self.createdAt)

    
class ProvLog(models.Model):
    ACTION_MOVE = 0
    ACTION_CLICK = 1
    ACTION_SUBMIT = 2
    ACTION_MEDIA = 3
    ACTION_OPEN = 4
    
    CHOICES_ACTION = (
        (ACTION_MOVE, "moved node"),
        (ACTION_CLICK, "clicked node/attribute"),
        (ACTION_SUBMIT, "pressed submit"),
        (ACTION_MEDIA, "opened media"),
        (ACTION_OPEN, "opened provenance"),
    )
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    cronDocumentInstance = models.ForeignKey(CronDocumentInstance, blank=True, null=True)
    mopDocumentInstance = models.ForeignKey(MopDocumentInstance, blank=True, null=True)
    
    action = models.IntegerField(choices=CHOICES_ACTION)
    node1 = models.CharField(max_length=128, blank=True, null=True)
    node2 = models.CharField(max_length=128, blank=True, null=True)
    attribute1 = models.CharField(max_length=128 ,blank=True, null=True)
    attribute2 = models.CharField(max_length=128 ,blank=True, null=True)
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    selected = models.NullBooleanField(blank=True, null=True)
    empty = models.NullBooleanField(blank=True, null=True)
    correct = models.NullBooleanField(blank=True, null=True)
    inactive = models.NullBooleanField(blank=True, null=True)
    
    def __unicode__(self):
        if self.cronDocumentInstance is not None:
            name =  "Cron: %s (%s)" % (self.cronDocumentInstance.cron.user.username, self.cronDocumentInstance.cronDocument.serial)
        elif self.mopDocumentInstance is not None:
            name = "Mop: %s (%s)" % (self.mopDocumentInstance.mop.user.username, self.mopDocumentInstance.randomizedDocument.serial)
        else:
            name = "ERROR"
        return "%s - %s (%s)" % (name, self.get_action_display(), self.createdAt)
    