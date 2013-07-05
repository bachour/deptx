from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    address = models.CharField(max_length=256)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    
    def __unicode__(self):
        return self.firstName + " " + self.lastName

  
class Cron(models.Model):
    player = models.OneToOneField(Player)
    user = models.OneToOneField(User)
    
    episode = models.IntegerField(default = 0)
    progress = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return self.user.username + " (" + self.player.firstName + " " + self.player.lastName + ")"


GENDER_CHOICES = ( 
('M', 'male'), 
('F', 'female'), 
) 

MARITAL_CHOICES = (
('S', 'single'),
('M', 'married'),
('D', 'divorced'),
('W', 'widowed'),
)

HAIR_CHOICES = (
('BLO', 'blonde'),
('BRO', 'brown'),
('BLA', 'black'),
('GRE', 'grey'),
('WHI', 'white'),
('RED', 'red'),
('AUB', 'auburn'),
('CHE', 'chestnut'),
)

EYES_CHOICES = (
('AMB', 'amber'),
('BLU', 'blue'),
('BRO', 'brown'),
('GRA', 'gray'),
('GRE', 'green'),
('HAZ', 'hazel'),
('RED', 'red'),
('VIO', 'violet'),
)
    
class Mop(models.Model):
    player = models.ForeignKey(Player)
    user = models.OneToOneField(User)
    active = models.BooleanField(default=True)
    
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    weight = models.IntegerField()
    height = models.IntegerField()
    marital = models.CharField(max_length=1, choices=MARITAL_CHOICES)
    hair = models.CharField(max_length=3, choices=HAIR_CHOICES)
    eyes = models.CharField(max_length=3, choices=EYES_CHOICES)
    
    trust = models.IntegerField(default=30)

    
    
    def __unicode__(self):
        return self.user.username + " (" + self.player.firstName + " " + self.player.lastName + " / active: " + self.active.__str__() + ")"
    
      
    
