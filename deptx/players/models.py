from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    address = models.CharField(max_length=256)
    phone = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.firstName + " " + self.lastName

  
class Cron(models.Model):
    player = models.OneToOneField(Player)
    user = models.OneToOneField(User)
    
    credits = models.IntegerField()
    
    def __unicode__(self):
        return self.user.username + " (" + self.player.firstName + " " + self.player.lastName + ")"
    
class Mop(models.Model):
    player = models.ForeignKey(Player)
    user = models.OneToOneField(User)
    active = models.BooleanField()
    
    score = models.IntegerField()
    
    def __unicode__(self):
        return self.user.username + " (" + self.player.firstName + " " + self.player.lastName + " / active: " + self.active.__str__() + ")"
    
      
    
