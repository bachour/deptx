from mop.models import RandomizedDocument
from assets.models import MopDocument
from provmanager.views import randomize_document
from mop.clearance import Clearance
from deptx.helpers import now
from datetime import timedelta
from random import randrange

def remove_old_documents():
    output = []
    randomizedDocument_list = RandomizedDocument.objects.filter(active=True)
    old = now() - timedelta(days=3) + timedelta(hours=2)
    for randomizedDocument in randomizedDocument_list:
        if randomizedDocument.createdAt < old:
            randomizedDocument.active = False
            randomizedDocument.save()
            output.append(randomizedDocument.serial)
    return output

def create_daily_documents():
    output = []
    mopDocument_list = MopDocument.objects.filter(active=True)
    mopDocument_low_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_LOW)
    mopDocument_guarded_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_GUARDED)
    mopDocument_elevated_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_ELEVATED)
    mopDocument_high_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_HIGH)
    mopDocument_severe_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_SEVERE)
    
    low = 5 + randrange(5)
    guarded = 4 + randrange(4)
    elevated = 3 + randrange(3)
    high = 2 + randrange(2)
    severe = 1 + randrange(1)
    
    for x in range(0, low):
        output.append(create_random_from_list(mopDocument_low_list))
    for x in range(0, guarded):
        output.append(create_random_from_list(mopDocument_guarded_list))
    for x in range(0, elevated):
        output.append(create_random_from_list(mopDocument_elevated_list))
    for x in range(0, high):
        output.append(create_random_from_list(mopDocument_high_list))
    for x in range(0, severe):
        output.append(create_random_from_list(mopDocument_severe_list))
    return output

def create_random_from_list(mopDocument_list):
    if mopDocument_list:
        mopDocument = mopDocument_list.order_by('?')[0]
        return create_single_document(mopDocument)
    else:
        return None

def create_single_document(mopDocument):
    return randomize_document(mopDocument).serial
    

    

        
