from mop.models import Mail, MopDocumentInstance, RequisitionBlank, RandomizedDocument
from assets.models import Requisition, CronDocument, Unit
import logging
from mop.clearance import Clearance

def sendReport(trustInstance):
    unit = Unit.objects.filter(type=Unit.TYPE_ADMINISTRATIVE)[0]
    Mail.objects.create(mop=trustInstance.mop, trustInstance=trustInstance, unit=unit, subject=Mail.SUBJECT_INFORMATION, type=Mail.TYPE_RECEIVED, bodyType=Mail.BODY_PERFORMANCE_REPORT)


def analyze_mail():
    output = []
    mail_list = Mail.objects.filter(processed=False).filter(type=Mail.TYPE_SENT).filter(state=Mail.STATE_NORMAL)
    #TODO add more output
    output.append("Unprocessed mails: %d" % mail_list.count())
    
    for mail in mail_list:
        newMail = prepareMail(mail)
        if mail.unit == None:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.bodyType = Mail.BODY_ERROR_MISSING_UNIT
            #if there is no unit an error is generated automatically - no need to set it manually
        elif mail.subject == Mail.SUBJECT_EMPTY:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.bodyType = Mail.BODY_ERROR_NO_SUBJECT
        elif mail.requisitionInstance == None:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.bodyType = Mail.BODY_ERROR_MISSING_FORM
        elif not mail.unit == mail.requisitionInstance.blank.requisition.unit:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.bodyType = Mail.BODY_ERROR_WRONG_UNIT
        elif not (subjectMatchesRequisition(mail)):
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.bodyType = Mail.BODY_ERROR_WRONG_FORM
        elif redundantDocument(mail):
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.bodyType = Mail.BODY_ERROR_REDUNDANT_DOCUMENT
            newMail.bodyData
        elif missingDocument(mail):
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.bodyType = Mail.BODY_ERROR_MISSING_DOCUMENT
        elif wrongDocument(mail):
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.bodyType = Mail.BODY_ERROR_WRONG_DOCUMENT
        #Now the mail should be formally correct
        #Let's see about the content!
        elif mail.subject == Mail.SUBJECT_REQUEST_FORM:
            requisition = getRequisition(mail)
            if requisition == None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_UNFOUND_FORM
            elif requisitionBlankExists(mail.mop, requisition):
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_EXISTING_FORM
            else:
                requisitionBlank = assignRequisition(mail.mop, requisition)
                newMail.requisitionBlank = requisitionBlank
                newMail.subject = Mail.SUBJECT_RECEIVE_FORM
                newMail.bodyType = Mail.BODY_ASSIGNING_FORM
        elif mail.subject == Mail.SUBJECT_REQUEST_DOCUMENT:
            #The serial inside the form could be either for a mop or for a cron 'document'
            cronDocument = getCronDocument(mail)
            randomizedDocument = getRandomizedDocument(mail)
            if cronDocument == None and randomizedDocument == None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_UNFOUND_DOCUMENT
            elif mopDocumentInstanceExists(mail.mop, cronDocument, randomizedDocument):
                #TODO what if document is used?
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_EXISTING_DOCUMENT
            elif not hasEnoughTrust(mail.mop, cronDocument, randomizedDocument):
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_LACKING_TRUST
            else:
                mopDocumentInstance = assignDocument(mail.mop, cronDocument, randomizedDocument)
                newMail.mopDocumentInstance = mopDocumentInstance
                clearance = Clearance(mopDocumentInstance.getClearance())
                newMail.trust = clearance.getTrustRequested()
                newMail.subject = Mail.SUBJECT_RECEIVE_DOCUMENT
                newMail.bodyType = Mail.BODY_ASSIGNING_DOCUMENT
        elif mail.subject == Mail.SUBJECT_SUBMIT_DOCUMENT:
            mail.mopDocumentInstance.status = MopDocumentInstance.STATUS_REPORTED
            mail.mopDocumentInstance.save()
            clearance = Clearance(mail.mopDocumentInstance.getClearance())
            newMail.subject = Mail.SUBJECT_REPORT_EVALUATION
            if mail.mopDocumentInstance.correct:
                newMail.bodyType = Mail.BODY_REPORT_SUCCESS
                newMail.trust = clearance.getTrustReportedCorrect()
            else:
                newMail.bodyType = Mail.BODY_REPORT_FAIL
                newMail.trust = clearance.getTrustReportedIncorrect()
        else:
            newMail.subject = Mail.SUBJECT_UNCAUGHT_CASE
            newMail.body = Mail.BODY_UNCAUGHT_CASE
            

        if newMail.subject == Mail.SUBJECT_ERROR:
            newMail.trust = -1
            if not mail.mopDocumentInstance == None:
                mail.mopDocumentInstance.used = False
                mail.mopDocumentInstance.save()

        mail.processed = True
        mail.save()
        newMail.replyTo = mail
        newMail.save()
        
        if newMail.trust is not None:
            mail.mop.trustTracker.addTrust(newMail.trust)

   
    return output

# def generateBody(text, data=None):
#     t = Template(text)
#     c = Context({"data": data})
#     return t.render(c)

def requisitionBlankExists(mop, requisition):
    try:
        requisitionBlank = RequisitionBlank.objects.get(mop=mop, requisition=requisition)
        return True
    except RequisitionBlank.DoesNotExist:
        return False


def mopDocumentInstanceExists(mop, cronDocument, randomizedDocument):
    if not cronDocument == None:
        try:
            mopDocumentInstance = MopDocumentInstance.objects.get(mop=mop, cronDocument=cronDocument)
            return True
        except MopDocumentInstance.DoesNotExist:
            return False
    elif not randomizedDocument == None:
        try:
            mopDocumentInstance = MopDocumentInstance.objects.get(mop=mop, randomizedDocument=randomizedDocument)
            return True
        except MopDocumentInstance.DoesNotExist:
            return False

def hasEnoughTrust(mop, cronDocument, randomizedDocument):
    if cronDocument is not None:
        document = cronDocument
    else:
        document = randomizedDocument.mopDocument
    trustCost = Clearance(document.clearance).getTrustRequested()
    if trustCost == 0:
        return True
    elif trustCost <= (mop.trustTracker.trust + mop.trustTracker.allowance):
        return True
    else:
        return False
    

def getRequisition(mail):
    try:
        requisition = Requisition.objects.get(serial=mail.requisitionInstance.data)
    except Requisition.DoesNotExist:
        requisition = None
    return requisition


def getCronDocument(mail):
    try:
        cronDocument = CronDocument.objects.get(serial=mail.requisitionInstance.data, unit=mail.unit)
    except CronDocument.DoesNotExist:
        cronDocument = None
    return cronDocument

def getRandomizedDocument(mail):
    try:
        randomizedDocument = RandomizedDocument.objects.get(serial=mail.requisitionInstance.data)
        if not randomizedDocument.mopDocument.unit == mail.unit:
            randomizedDocument = None 
    except RandomizedDocument.DoesNotExist:
        randomizedDocument = None
    return randomizedDocument

def getRequiredTrust(cronDocument, randomizedDocument):
    if cronDocument is not None:
        document = cronDocument
    else:
        document = randomizedDocument.mopDocument
    return Clearance(document.clearance).getTrustRequested() * (-1)


def subjectMatchesRequisition(mail):
    if int(mail.subject) == int(Mail.SUBJECT_REQUEST_FORM):
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_FORM:
            logging.info("subject matches request form");
            return True
    elif mail.subject == Mail.SUBJECT_REQUEST_DOCUMENT:
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_DOCUMENT:
            return True
    elif mail.subject == Mail.SUBJECT_SUBMIT_DOCUMENT:
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_SUBMISSION:
            return True
    return False

def redundantDocument(mail):
    if not mail.subject == Mail.SUBJECT_SUBMIT_DOCUMENT:
        if not mail.mopDocumentInstance == None:
            return True
    return False

def missingDocument(mail):
    if mail.subject == Mail.SUBJECT_SUBMIT_DOCUMENT:
        if mail.mopDocumentInstance == None:
            return True
    return False

def wrongDocument(mail):
    if mail.subject == Mail.SUBJECT_SUBMIT_DOCUMENT:
        cronDocument = getCronDocument(mail)
        randomizedDocument = getRandomizedDocument(mail)
        mopDocumentInstance = None
        if not cronDocument is None:
            try:
                mopDocumentInstance = MopDocumentInstance.objects.get(cronDocument=cronDocument, mop=mail.mop)
            except MopDocumentInstance.DoesNotExist:
                pass
        elif not randomizedDocument is None:
            try:
                mopDocumentInstance = MopDocumentInstance.objects.get(randomizedDocument=randomizedDocument, mop=mail.mop)
            except MopDocumentInstance.DoesNotExist:
                pass

        if not mopDocumentInstance is None:
            if not mail.mopDocumentInstance.cronDocument == mopDocumentInstance.cronDocument:
                return True
            elif not mail.mopDocumentInstance.randomizedDocument == mopDocumentInstance.randomizedDocument:
                return True
    return False

        
#TODO display attachments when viewing mails
def assignRequisition(mop, requisition):
    requisitionBlank, created = RequisitionBlank.objects.get_or_create(mop=mop, requisition=requisition)
    return requisitionBlank
       
    
def assignDocument(mop, cronDocument, randomizedDocument):
    if not cronDocument == None:
        mopDocumentInstance, created = MopDocumentInstance.objects.get_or_create(mop=mop, cronDocument=cronDocument, type=MopDocumentInstance.TYPE_CRON)
    else:
        mopDocumentInstance, created = MopDocumentInstance.objects.get_or_create(mop=mop, randomizedDocument=randomizedDocument, type=MopDocumentInstance.TYPE_MOP)
    return mopDocumentInstance

def prepareMail(mail):
    newMail = Mail()
    newMail.mop = mail.mop
    newMail.unit = mail.unit
    newMail.type = Mail.TYPE_RECEIVED
    newMail.processed = True
    return newMail
    