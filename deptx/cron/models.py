from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from players.models import Cron
from assets.models import Mission, Case, CronDocument, CaseQuestion
from django.template import Context, loader
from django.core.mail import EmailMessage, mail_admins

try:
    from deptx.settings_production import TO_ALL
except:
    TO_ALL = ["1@localhost.com", "2@localhost.com"]
  
  
class MissionInstance(models.Model):
    
    PROGRESS_0_INTRO = 0
    PROGRESS_1_BRIEFING = 1
    PROGRESS_2_CASES = 2
    PROGRESS_3_DEBRIEFING = 3
    PROGRESS_4_OUTRO = 4
    PROGRESS_5_DONE = 5
    
    CHOICES_PROGRESS = (
        (PROGRESS_0_INTRO, "intro"),
        (PROGRESS_1_BRIEFING, "briefing"),
        (PROGRESS_2_CASES, "cases"),
        (PROGRESS_3_DEBRIEFING, "debriefing"),
        (PROGRESS_4_OUTRO, "outro"),
        (PROGRESS_5_DONE, "done")
    )
    
    cron = models.ForeignKey(Cron)
    mission = models.ForeignKey(Mission)
    progress = models.IntegerField(choices=CHOICES_PROGRESS, default=PROGRESS_0_INTRO)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def makeProgress(self):
        if not self.progress == self.PROGRESS_5_DONE:
            self.progress += 1
            self.save()
    
    def isIntroAllowed(self):
        return self.progress >= self.PROGRESS_0_INTRO
    
    def isBriefingAllowed(self):
        return self.progress >= self.PROGRESS_1_BRIEFING
    
    def isCasesAllowed(self):
        return self.progress >= self.PROGRESS_2_CASES
    
    def isDebriefingAllowed(self):
        return self.progress >= self.PROGRESS_3_DEBRIEFING
    
    def isOutroAllowed(self):
        return self.progress >= self.PROGRESS_4_OUTRO
    
    def __unicode__(self):
        return "%s - %s (%s)" % (self.cron.user.username, self.mission.name, self.get_progress_display())
    
    

class CaseInstance(models.Model):
    case = models.ForeignKey(Case)
    cron = models.ForeignKey(Cron)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def allQuestionsSolved(self):
        question_list = CaseQuestion.objects.filter(case=self.case)
        for question in question_list:
            try:
                questionInstance = CaseQuestionInstance.objects.get(question=question, cron=self.cron)
            except CaseQuestionInstance.DoesNotExist:
                return False
            if not questionInstance.correct:
                return False
        return True
    
    def allDocumentsSolved(self):
        cronDocument_list = CronDocument.objects.filter(case=self.case)
        for cronDocument in cronDocument_list:
            try:
                cronDocumentInstance = CronDocumentInstance.objects.get(cronDocument=cronDocument, cron=self.cron)
            except CronDocumentInstance.DoesNotExist:
                return False
            if not cronDocumentInstance.solved:
                return False
        return True
    
    def isSolved(self):
        if self.allDocumentsSolved() and self.allQuestionsSolved():
            return True
        else:
            return False
    
    def __unicode__(self):
        if (self.isSolved()):
            status = "SOLVED"
        elif (self.allDocumentsSolved()):
            status = "QUESTIONS NOT SOLVED"
        else:
            status = "DOCUMENTS NOT SOLVED"
        return "%s (%s: %s)" % (self.cron.user.username, self.case.name, status)

class CaseQuestionInstance(models.Model):
    cron = models.ForeignKey(Cron)
    question = models.ForeignKey(CaseQuestion)
    correct = models.BooleanField(default=False)
    failedAttempts = models.IntegerField(default=0)
    
    answer1 = models.CharField(max_length=256, blank=True, null=True)
    answer2 = models.CharField(max_length=256, blank=True, null=True)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def increaseFailedAttempts(self):
        self.failedAttempts += 1
        self.save()
    
    def __unicode__(self):
        return "%s - %s - %s - %s - %s" % (self.cron.user.username, self.question.case.serial, self.question.id, self.correct, self.failedAttempts)

class CronDocumentInstance(models.Model):
    cronDocument = models.ForeignKey(CronDocument)
    cron = models.ForeignKey(Cron)
    provenanceState = models.TextField(blank=True, null=True)
    solved = models.BooleanField(default=False)
    failedAttempts = models.IntegerField(default=0)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def increaseFailedAttempts(self):
        self.failedAttempts += 1
        self.save()
        
    def getStars(self):
        if self.failedAttempts <= 1:
            return 3
        elif self.failedAttempts <= 5:
            return 2
        else:
            return 1
    
    def getStarsForTemplate(self):
        stars = self.getStars()
        output = ""
        for i in range(stars):
            output = output + "i"
        return output

    
    def __unicode__(self):
        if (self.solved):
            status = "SOLVED"
        else:
            status = "IN PROGRESS"
        return "%s - %s - %s - wrong tries: %s - %s" % (self.cronDocument.serial, self.cron.user.username, status, self.failedAttempts, self.modifiedAt)
    

class HelpMail(models.Model):
    
    TYPE_FROM_PLAYER = 1
    TYPE_TO_PLAYER = 2
    
    CHOICES_TYPE = (
        (TYPE_FROM_PLAYER, "message sent by player"),
        (TYPE_TO_PLAYER, "message sent by us"),
    )
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    
    cron = models.ForeignKey(Cron)
    type = models.IntegerField(choices=CHOICES_TYPE)
    body = models.TextField()
    isReply = models.BooleanField(default=False)
    isRead = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            if self.type == self.TYPE_FROM_PLAYER:
                subject = "[cr0n] %s: Field Communication" % (self.cron.user.username)
                email_tpl = loader.get_template('cron/mail/message_from_player.txt')
                c = Context({'body':self.body})
                email = EmailMessage(subject=subject, body=email_tpl.render(c), to=TO_ALL)
                email.send(fail_silently=False)
        super(HelpMail, self).save(*args, **kwargs)
    
    
    def __unicode__(self):
        if self.type == self.TYPE_FROM_PLAYER:
            fromto = "From"
        else:
            fromto = "To"
        return "%s: %s - %s" % (fromto, self.cron.user.username, self.createdAt)
    
