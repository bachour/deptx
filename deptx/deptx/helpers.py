import uuid

import datetime
from django.utils.timezone import utc  

def now():
    return datetime.datetime.utcnow().replace(tzinfo=utc)

def generateUUID():
    return str(uuid.uuid1())[:-13]

