from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from players.models import Cron
from assets.models import Mission, Case, CronDocument

  
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
    
    def isSolved(self):
        cronDocument_list = CronDocument.objects.filter(case=self.case)
        for cronDocument in cronDocument_list:
            try:
                cronDocumentInstance = CronDocumentInstance.objects.get(cronDocument=cronDocument, cron=self.cron)
            except CronDocumentInstance.DoesNotExist:
                return False
            if not cronDocumentInstance.solved:
                return False
        return True
    
    def __unicode__(self):
        if (self.isSolved):
            status = "SOLVED"
        else:
            status = "IN PROGRESS"
        return self.cron.user.username + " (" + self.case.name + ": " + status + ")"
    

class CronDocumentInstance(models.Model):
    cronDocument = models.ForeignKey(CronDocument)
    cron = models.ForeignKey(Cron)
    provenanceState = models.TextField(blank=True, null=True)
    solved = models.BooleanField(default=False)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def __unicode__(self):
        if (self.solved):
            status = "SOLVED"
        else:
            status = "IN PROGRESS"
        return self.cronDocument.serial + " / " + self.cron.user.username + " (" + status + ")"
