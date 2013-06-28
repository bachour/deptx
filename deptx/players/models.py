from django.db import models
from django.contrib.auth.models import User

#TODO: Every player should probably be able to create more than just one mop user

class Player(models.Model):
    cron_user = models.OneToOneField(User, related_name="cron_player")
    mop_user = models.OneToOneField(User, related_name="mop_player")
    
    color = models.CharField(max_length=100)
    level = models.IntegerField()
    
    def __unicode__(self):
        return self.cron_user.username + " / " + self.mop_user.username
    