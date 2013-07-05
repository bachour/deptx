from django.db import models

from players.models import Mop

class Task(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    episode = models.IntegerField(default=-1)
    trust = models.IntegerField(default=20)
    value = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name

STATUS_CHOICES = (
("A", "accessible"),
("O", "open"),
("S", "solved"),
("F", "failed"),
)

class TaskStatus(models.Model):
    task = models.ForeignKey(Task)
    mop = models.ForeignKey(Mop)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    
    def __unicode__(self):
        return self.task.name + " / " + self.mop.user.username
