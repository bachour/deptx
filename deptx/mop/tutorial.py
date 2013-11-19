from assets.models import Unit
from mop.models import Mail, TrustTracker, RandomizedDocument

def getUnitComm():
    return Unit.objects.get(type=Unit.TYPE_COMMUNICATIVE)

def createMail(bodyType, mop):
    mopco = getUnitComm()
    Mail.objects.create(bodyType=bodyType, mop=mop, unit=mopco, subject=Mail.SUBJECT_HELP, type=Mail.TYPE_RECEIVED, processed=True)

def hide(trustTracker, created):
    hide = {}
    
    if not trustTracker.tutorial == TrustTracker.TUTORIAL_6_DONE:
        mopco_mails = Mail.objects.filter(mop=trustTracker.mop).filter(unit=getUnitComm()).filter(type=Mail.TYPE_RECEIVED)
        
        hide['performance'] = True
        hide['guidebook'] = True
        hide['documentsArchive'] = True
        hide['formsArchive'] = True
        hide['mail'] = True

        if (created):
            createMail(Mail.BODY_TUTORIAL_1_INTRO, trustTracker.mop)
            trustTracker.tutorial = TrustTracker.TUTORIAL_1_SENT_HOW_TO_REQUEST_FORM
            trustTracker.save()
            
        if mopco_mails.filter(bodyType=Mail.BODY_TUTORIAL_5_CONCLUSION).filter(read=True):
            trustTracker.tutorial = TrustTracker.TUTORIAL_6_DONE
            trustTracker.save()
            hide = []
        elif mopco_mails.filter(bodyType=Mail.BODY_TUTORIAL_4c_CORRECT_MODIFICATION).filter(read=True):
            hide['guidebook'] = False
            hide['documentsPool'] = True
        elif mopco_mails.filter(bodyType=Mail.BODY_TUTORIAL_4b_INCORRECT_MODIFICATION_2).filter(read=True):
            hide['compose'] = True
            hide['formsBlank'] = True
            hide['formsSigned'] = True
            hide['documentsPool'] = True
        elif mopco_mails.filter(bodyType=Mail.BODY_TUTORIAL_4a_INCORRECT_MODIFICATION).filter(read=True):
            hide['compose'] = True
            hide['formsBlank'] = True
            hide['formsSigned'] = True
            hide['documentsPool'] = True
        elif mopco_mails.filter(bodyType=Mail.BODY_TUTORIAL_3_TASK_COMPLETION).filter(read=True):
            hide['compose'] = True
            hide['formsBlank'] = True
            hide['formsSigned'] = True
            hide['documentsPool'] = True
        elif mopco_mails.filter(bodyType=Mail.BODY_TUTORIAL_2_DOCUMENT_REQUEST).filter(read=True):
            hide['documentsDrawer'] = True 
        elif mopco_mails.filter(bodyType=Mail.BODY_TUTORIAL_1_INTRO).filter(read=True):
            hide['documentsDrawer'] = True
            hide['documentsPool'] = True
        else:
            hide['compose'] = True
            hide['formsBlank'] = True
            hide['formsSigned'] = True
            hide['documentsDrawer'] = True
            hide['documentsPool'] = True
    
    return hide

def assignForm(trustTracker):
    if trustTracker.tutorial == TrustTracker.TUTORIAL_1_SENT_HOW_TO_REQUEST_FORM:
        createMail(Mail.BODY_TUTORIAL_2_DOCUMENT_REQUEST, trustTracker.mop)
        trustTracker.tutorial = TrustTracker.TUTORIAL_2_SENT_HOW_TO_REQUEST_DOCUMENT
        trustTracker.save()
        
def assignDocument(trustTracker):
    if trustTracker.tutorial == TrustTracker.TUTORIAL_2_SENT_HOW_TO_REQUEST_DOCUMENT:
        createMail(Mail.BODY_TUTORIAL_3_TASK_COMPLETION, trustTracker.mop)
        trustTracker.tutorial = TrustTracker.TUTORIAL_3_SENT_HOW_TO_CHECK_PROVENANCE
        trustTracker.save()
        
def checkProvenance(trustTracker, correct):
    if trustTracker.tutorial == TrustTracker.TUTORIAL_3_SENT_HOW_TO_CHECK_PROVENANCE:
        if correct:
            createMail(Mail.BODY_TUTORIAL_4c_CORRECT_MODIFICATION, trustTracker.mop)
            trustTracker.tutorial = TrustTracker.TUTORIAL_4_SENT_HOW_TO_SUBMIT_DOCUMENT
            trustTracker.save()
        else:
            trustTracker.tutorialProvErrors += 1
            trustTracker.save()
            if trustTracker.tutorialProvErrors > 1:
                createMail(Mail.BODY_TUTORIAL_4b_INCORRECT_MODIFICATION_2, trustTracker.mop)
            else:
                createMail(Mail.BODY_TUTORIAL_4a_INCORRECT_MODIFICATION, trustTracker.mop)
                
def submitDocument(trustTracker):
    if trustTracker.tutorial == TrustTracker.TUTORIAL_4_SENT_HOW_TO_SUBMIT_DOCUMENT:
        createMail(Mail.BODY_TUTORIAL_5_CONCLUSION, trustTracker.mop)
        trustTracker.tutorial = TrustTracker.TUTORIAL_5_SENT_CONCLUSION
        trustTracker.save()

def getTutorialDocument(trustTracker):
    if not trustTracker.tutorial == TrustTracker.TUTORIAL_6_DONE:
        return RandomizedDocument.objects.filter(isTutorial=True)
    else:
        return None 
