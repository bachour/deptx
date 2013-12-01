from assets.models import Unit
from mop.models import Mail, MopTracker, RandomizedDocument, Mop
from cron import mailer

def getUnitComm():
    return Unit.objects.get(type=Unit.TYPE_COMMUNICATIVE)

def createMail(bodyType, mop):
    mopco = getUnitComm()
    Mail.objects.create(bodyType=bodyType, mop=mop, unit=mopco, subject=Mail.SUBJECT_HELP, type=Mail.TYPE_RECEIVED, processed=True)

def hide(mopTracker, created):
    hide = {}
    
    if not mopTracker.tutorial == MopTracker.TUTORIAL_6_DONE:
        mopco_mails = Mail.objects.filter(mop=mopTracker.mop).filter(unit=getUnitComm()).filter(type=Mail.TYPE_RECEIVED)
        
        hide['performance'] = True
        hide['guidebook'] = True
        hide['documentsArchive'] = True
        hide['formsArchive'] = True
        hide['mail'] = True

        if (created):
            createMail(Mail.BODY_TUTORIAL_1_INTRO, mopTracker.mop)
            mopTracker.tutorial = MopTracker.TUTORIAL_1_SENT_HOW_TO_REQUEST_FORM
            mopTracker.save()
            
        if mopco_mails.filter(bodyType=Mail.BODY_TUTORIAL_5_CONCLUSION).filter(read=True):
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

def assignForm(mopTracker):
    if mopTracker.tutorial == MopTracker.TUTORIAL_1_SENT_HOW_TO_REQUEST_FORM:
        createMail(Mail.BODY_TUTORIAL_2_DOCUMENT_REQUEST, mopTracker.mop)
        mopTracker.tutorial = MopTracker.TUTORIAL_2_SENT_HOW_TO_REQUEST_DOCUMENT
        mopTracker.save()
        
def assignDocument(mopTracker):
    if mopTracker.tutorial == MopTracker.TUTORIAL_2_SENT_HOW_TO_REQUEST_DOCUMENT:
        createMail(Mail.BODY_TUTORIAL_3_TASK_COMPLETION, mopTracker.mop)
        mopTracker.tutorial = MopTracker.TUTORIAL_3_SENT_HOW_TO_CHECK_PROVENANCE
        mopTracker.save()
        
def checkProvenance(mopTracker, correct):
    if mopTracker.tutorial == MopTracker.TUTORIAL_3_SENT_HOW_TO_CHECK_PROVENANCE:
        if correct:
            createMail(Mail.BODY_TUTORIAL_4c_CORRECT_MODIFICATION, mopTracker.mop)
            mopTracker.tutorial = MopTracker.TUTORIAL_4_SENT_HOW_TO_SUBMIT_DOCUMENT
            mopTracker.save()
        else:
            mopTracker.tutorialProvErrors += 1
            mopTracker.save()
            if mopTracker.tutorialProvErrors > 1:
                createMail(Mail.BODY_TUTORIAL_4b_INCORRECT_MODIFICATION_2, mopTracker.mop)
            else:
                createMail(Mail.BODY_TUTORIAL_4a_INCORRECT_MODIFICATION, mopTracker.mop)
                
def submitDocument(mopTracker):
    if mopTracker.tutorial == MopTracker.TUTORIAL_4_SENT_HOW_TO_SUBMIT_DOCUMENT:
        createMail(Mail.BODY_TUTORIAL_5_CONCLUSION, mopTracker.mop)
        mopTracker.tutorial = MopTracker.TUTORIAL_5_SENT_CONCLUSION
        mopTracker.save()

def getTutorialDocument(mopTracker):
    if not mopTracker.tutorial == MopTracker.TUTORIAL_6_DONE:
        return RandomizedDocument.objects.filter(isTutorial=True)
    else:
        return None 

def cronMail(mopTracker, mail):
    if mopTracker.tutorial == MopTracker.TUTORIAL_5_SENT_CONCLUSION and mail.bodyType == Mail.BODY_TUTORIAL_5_CONCLUSION:
        mopTracker.tutorial = MopTracker.TUTORIAL_6_DONE
        mopTracker.save()
        mailer.mopTutorialDone(mopTracker.mop.cron)
#         mop_list = Mop.objects.filter(cron=mopTracker.mop.cron)
#         oneMopHasPassedTutorial = False
#         for mop in mop_list:
#             try:
#                 if not mop.mopTracker.isTutorial():
#                     oneMopHasPassedTutorial = True
#                     break
#             except:
#                 pass
#         if oneMopHasPassedTutorial:
#             mailer.mopTutorialDone(mopTracker.mop.cron)
