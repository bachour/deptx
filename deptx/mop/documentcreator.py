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
    mopDocument_blue_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_BLUE)
    mopDocument_green_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_GREEN)
    mopDocument_yellow_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_YELLOW)
    mopDocument_orange_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_ORANGE)
    mopDocument_red_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_RED)
    
    blue = 5 + randrange(5)
    green = 4 + randrange(4)
    yellow = 3 + randrange(3)
    orange = 2 + randrange(2)
    red = 1 + randrange(1)
    
    for x in range(0, blue):
        output.append(create_random_from_list(mopDocument_blue_list))
    for x in range(0, green):
        output.append(create_random_from_list(mopDocument_green_list))
    for x in range(0, yellow):
        output.append(create_random_from_list(mopDocument_yellow_list))
    for x in range(0, orange):
        output.append(create_random_from_list(mopDocument_orange_list))
    for x in range(0, red):
        output.append(create_random_from_list(mopDocument_red_list))
    return output

def create_random_from_list(mopDocument_list):
    if mopDocument_list:
        mopDocument = mopDocument_list.order_by('?')[0]
        return create_single_document(mopDocument)
    else:
        return None

def create_single_document(mopDocument):
    return randomize_document(mopDocument).serial
    

    

        
