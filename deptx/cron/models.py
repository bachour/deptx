from django.db import models

from players.models import Cron
from assets.models import Mission, Case, Document
  
class CronTracker(models.Model):
    cron = models.OneToOneField(Cron)
    mission = models.ForeignKey(Mission)
    progress = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.cron.user.username + " (" + self.mission.name + " " + str(self.progress) + ")"
    
    

class CaseInstance(models.Model):
    case = models.ForeignKey(Case)
    crontracker = models.ForeignKey(CronTracker)
    solved = models.BooleanField(default=False)
    
    def __unicode__(self):
        if (self.solved):
            status = "SOLVED"
        else:
            status = "IN PROGRESS"
        return self.crontracker.cron.user.username + " (" + self.case.name + ": " + status + ")"

class CronDocumentInstance(models.Model):
    document = models.ForeignKey(Document)
    cron = models.ForeignKey(Cron)
    provenanceState = models.TextField(blank=True, null=True)
    solved = models.BooleanField()
    
    def __unicode__(self):
        if (self.solved):
            status = "SOLVED"
        else:
            status = "IN PROGRESS"
        return self.document.name + " / " + self.cron.user.username + " (" + status + ")"
