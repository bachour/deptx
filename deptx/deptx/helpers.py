import uuid

import datetime
from django.utils.timezone import utc  

import string
import random

def now():
    return datetime.datetime.utcnow().replace(tzinfo=utc)

def generateUUID():
    return str(uuid.uuid1())[:-13]

def random_chars(size=4, chars=string.ascii_uppercase+string.digits):
    return ''.join(random.choice(chars) for x in range(size))

class Clearance():

    CLEARANCE_LOW = 0
    CLEARANCE_MEDIUM = 10
    CLEARANCE_HIGH = 20
    CLEARANCE_MAX = 100
    
    CHOICES_CLEARANCE_MOPDOCUMENT = (
        (CLEARANCE_LOW, "BLUE"),
        (CLEARANCE_MEDIUM, "ORANGE"),
        (CLEARANCE_HIGH, "RED"),
    )
    
    CHOICES_CLEARANCE_CRONDOCUMENT = (
        (CLEARANCE_MAX, "ULTRAVIOLET"),
    )
    
    CHOICES_CLEARANCE_ALL = CHOICES_CLEARANCE_MOPDOCUMENT + CHOICES_CLEARANCE_CRONDOCUMENT

    

