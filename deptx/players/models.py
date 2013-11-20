from django.db import models
from django.contrib.auth.models import User

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from deptx.helpers import generateUUID
from mop.clearance import Clearance


#TODO move Player into CRON
#TODO move Cron and Mop into appropriate apps
class Player(models.Model):
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_OTHER = 2
        
    GENDER_CHOICES = ( 
        (GENDER_FEMALE, 'female'),
        (GENDER_MALE, 'male'), 
        (GENDER_OTHER, 'other'), 
    ) 
    
    name = models.CharField(max_length=128)
    gender = models.IntegerField(choices=GENDER_CHOICES)
    age = models.IntegerField()
    town = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def __unicode__(self):
        return self.name

  
class Cron(models.Model):
    email = models.EmailField()
    overSixteen = models.BooleanField()
    user = models.OneToOneField(User)
    
    player = models.OneToOneField(Player, blank=True, null=True)
    activated = models.BooleanField(default=False)
    activationCode = models.CharField(max_length=36, default=generateUUID)
    
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    def __unicode__(self):
        return self.user.username



    
class Mop(models.Model):
    
    GENDER_MALE = 0
    GENDER_FEMALE = 1
    GENDER_OTHER = 2
        
    GENDER_CHOICES = ( 
        (GENDER_MALE, 'male'), 
        (GENDER_FEMALE, 'female'),
        (GENDER_OTHER, 'other'), 
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
    
    cron = models.ForeignKey(Cron)
    user = models.OneToOneField(User)
    active = models.BooleanField(default=True)
    createdAt = CreationDateTimeField()
    modifiedAt = ModificationDateTimeField()
    
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.IntegerField(choices=GENDER_CHOICES)
    weight = models.IntegerField()
    height = models.IntegerField()
    marital = models.IntegerField(choices=MARITAL_CHOICES)
    hair = models.IntegerField(choices=HAIR_CHOICES)
    eyes = models.IntegerField(choices=EYES_CHOICES)
    serial = models.CharField(max_length=36, default=generateUUID)
    
    def __unicode__(self):
        return "%s (cron: %s)" % (self.user.username, self.cron.user.username)
