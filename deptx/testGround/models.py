from django.db import models

class Dude(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    
    def __unicode__(self):
        return self.name

class Car(models.Model):
    owner = models.ForeignKey(Dude)
    make = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.owner.name + "\'s " + self.color + " " + self.make
