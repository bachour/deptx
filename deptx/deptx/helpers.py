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



