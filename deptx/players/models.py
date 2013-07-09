from django.db import models
from django.contrib.auth.models import User

from deptx.helpers import generateUUID

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



    
class Mop(models.Model):
    
    GENDER_MALE = 0
    GENDER_FEMALE = 1
        
    GENDER_CHOICES = ( 
        (GENDER_MALE, 'male'), 
        (GENDER_FEMALE, 'female'), 
    ) 
    
    MARITAL_SINGLE = 0
    MARITAL_MARRIED = 1
    MARITAL_DIVORCED = 2
    MARITAL_WIDOWED = 3
    
    MARITAL_CHOICES = (
        (MARITAL_SINGLE, 'single'),
        (MARITAL_MARRIED, 'married'),
        (MARITAL_DIVORCED, 'divorced'),
        (MARITAL_WIDOWED, 'widowed'),
    )
    
    HAIR_BLONDE = 0
    HAIR_BROWN = 1
    HAIR_BLACK = 2
    HAIR_GREY = 3
    HAIR_WHITE = 4
    HAIR_RED = 5
    HAIR_AUBURN = 6
    HAIR_CHESTNUT = 7
    
    HAIR_CHOICES = (
        (HAIR_BLONDE, 'blonde'),
        (HAIR_BROWN, 'brown'),
        (HAIR_BLACK, 'black'),
        (HAIR_GREY, 'grey'),
        (HAIR_WHITE, 'white'),
        (HAIR_RED, 'red'),
        (HAIR_AUBURN, 'auburn'),
        (HAIR_CHESTNUT, 'chestnut'),
    )
    
    EYE_BLUE = 0
    EYE_BROWN = 1
    EYE_GREEN = 2
    EYE_GREY = 3
    EYE_AMBER = 4
    EYE_HAZEL = 5
    EYE_RED = 6
    EYE_VIOLET = 7
    
    EYES_CHOICES = (
        (EYE_BLUE, 'blue'),
        (EYE_BROWN, 'brown'),
        (EYE_GREEN, 'green'),
        (EYE_GREY, 'grey'),
        (EYE_AMBER, 'amber'),
        (EYE_HAZEL, 'hazel'),
        (EYE_RED, 'red'),
        (EYE_VIOLET, 'violet'),
    )
    
    player = models.ForeignKey(Player)
    user = models.OneToOneField(User)
    active = models.BooleanField(default=True)
    
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.IntegerField(choices=GENDER_CHOICES)
    weight = models.IntegerField()
    height = models.IntegerField()
    marital = models.IntegerField(choices=MARITAL_CHOICES)
    hair = models.IntegerField(choices=HAIR_CHOICES)
    eyes = models.IntegerField(choices=EYES_CHOICES)
    
    trust = models.IntegerField(default=30)
    serial = models.CharField(max_length=36, default=generateUUID)

    
    
    def __unicode__(self):
        return self.user.username + " (" + self.player.firstName + " " + self.player.lastName + " / active: " + self.active.__str__() + ")"
    
      
    
