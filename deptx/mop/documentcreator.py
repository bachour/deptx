from mop.models import RandomizedDocument, MopDocumentInstance, Mail
from assets.models import MopDocument
from provmanager.views import randomize_document
from mop.clearance import Clearance
from deptx.helpers import now
from datetime import timedelta
from random import randrange

def remove_old_documents():
    output = []
    randomizedDocument_list = RandomizedDocument.objects.filter(active=True)
    for randomizedDocument in randomizedDocument_list:
        if randomizedDocument.dueAt and randomizedDocument.dueAt < now():
            randomizedDocument.active = False
            randomizedDocument.save()
            output.append(randomizedDocument.serial)
            
            mopDocumentInstance_list = MopDocumentInstance.objects.filter(randomizedDocument=randomizedDocument).filter(status=MopDocumentInstance.STATUS_ACTIVE)
            for mopDocumentInstance in mopDocumentInstance_list:
                mopDocumentInstance.status = MopDocumentInstance.STATUS_REVOKED
                mopDocumentInstance.save()
                
                mail = Mail()
                mail.mop = mopDocumentInstance.mop
                mail.type = Mail.TYPE_RECEIVED
                mail.processed = True
                mail.unit = mopDocumentInstance.randomizedDocument.unit
                mail.subject = Mail.SUBJECT_REVOKE_DOCUMENT
                mail.bodyType = Mail.BODY_REVOKING_DOCUMENT
                mail.mopDocumentInstance = mopDocumentInstance
                mail.trust = mopDocumentInstance.getTrustFinal()
                mail.save()
                
                mopDocumentInstance.mop.mopTracker.addTrust(mopDocumentInstance.getTrustFinal(), True)
                mopDocumentInstance.mop.mopTracker.save()
                
    return output

def create_documents():
    output = []
    mopDocument_list = MopDocument.objects.filter(active=True)
    mopDocument_blue_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_BLUE)
    mopDocument_green_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_GREEN)
    mopDocument_yellow_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_YELLOW)
    mopDocument_orange_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_ORANGE)
    mopDocument_red_list = mopDocument_list.filter(clearance=Clearance.CLEARANCE_RED)

    #which document to create?
    selector = randrange(20)
    if selector <= 5:
        output.append(create_random_from_list(mopDocument_blue_list))
    elif selector <= 10:
        output.append(create_random_from_list(mopDocument_green_list))
    elif selector <= 14:
        output.append(create_random_from_list(mopDocument_yellow_list))
    elif selector <= 17:
        output.append(create_random_from_list(mopDocument_orange_list))
    else:
        output.append(create_random_from_list(mopDocument_red_list))


# old document generation systen    
#     blue = 5 + randrange(5)
#     green = 4 + randrange(4)
#     yellow = 3 + randrange(3)
#     orange = 2 + randrange(2)
#     red = 1 + randrange(1)
#     
#     for x in range(0, blue):
#         output.append(create_random_from_list(mopDocument_blue_list))
#     for x in range(0, green):
#         output.append(create_random_from_list(mopDocument_green_list))
#     for x in range(0, yellow):
#         output.append(create_random_from_list(mopDocument_yellow_list))
#     for x in range(0, orange):
#         output.append(create_random_from_list(mopDocument_orange_list))
#     for x in range(0, red):
#         output.append(create_random_from_list(mopDocument_red_list))
#    return output

def create_random_from_list(mopDocument_list):
    if mopDocument_list:
        mopDocument = mopDocument_list.order_by('?')[0]
        return create_single_document(mopDocument)
    else:
        return None

def create_single_document(mopDocument):
    randomizedDocument = randomize_document(mopDocument)
    randomizedDocument.appearAt = now()
    randomizedDocument.dueAt = now() + timedelta(days=2)
    randomizedDocument.save()
    return randomizedDocument.serial
    

    

        
