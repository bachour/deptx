from mop.models import Mail, MopDocumentInstance, RequisitionBlank, RandomizedDocument
from cron.models import CronDocumentInstance
from assets.models import Requisition, CronDocument
from django.template import Context, loader, Template
import logging
from provmanager.views import randomize_document

def analyze_mail():
    output = []
    mail_list = Mail.objects.filter(processed=False).filter(type=Mail.TYPE_SENT).filter(state=Mail.STATE_NORMAL)
    #TODO add more output
    output.append("Unprocessed mails: %d" % mail_list.count())
    
    for mail in mail_list:
        newMail = prepareMail(mail)
        if mail.unit == None:
            newMail.subject = Mail.SUBJECT_ERROR
            mail_tpl = loader.get_template('mop/mail/no_unit.txt')
            c = Context()
            newMail.body = mail_tpl.render(c)
        elif mail.subject == Mail.SUBJECT_EMPTY:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = generateBody(mail.unit.mail_error_no_subject)
        elif mail.requisitionInstance == None:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = generateBody(mail.unit.mail_error_missing_form)
        elif not mail.unit == mail.requisitionInstance.blank.requisition.unit:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = generateBody(mail.unit.mail_error_wrong_unit, mail.requisitionInstance.blank.requisition.serial)
        elif not (subjectMatchesRequisition(mail)):
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = generateBody(mail.unit.mail_error_wrong_form)
        elif redundantDocument(mail):
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = generateBody(mail.unit.mail_error_redundant_document, mail.requisitionInstance.data)
        elif missingDocument(mail):
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = generateBody(mail.unit.mail_error_missing_document)
        elif wrongDocument(mail):
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = generateBody(mail.unit.mail_error_wrong_document, mail.requisitionInstance.data)
        #Now the mail should be formally correct
        #Let's see about the content!
        elif mail.subject == Mail.SUBJECT_REQUEST_FORM:
            requisition = getRequisition(mail)
            if requisition == None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_unfound_form, mail.requisitionInstance.data)
            elif requisitionBlankExists(mail.mop, requisition):
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_existing_form, mail.requisitionInstance.data)
            else:
                assignRequisition(mail.mop, requisition)
                newMail.subject = Mail.SUBJECT_RECEIVE_FORM
                newMail.body = generateBody(mail.unit.mail_assigning_form, mail.requisitionInstance.data)
        elif mail.subject == Mail.SUBJECT_REQUEST_DOCUMENT:
            #The serial inside the form could be either for a mop or for a cron 'document'
            cronDocument = getCronDocument(mail)
            randomizedDocument = getRandomizedDocument(mail)
            if cronDocument == None and randomizedDocument == None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_unfound_document, mail.requisitionInstance.data)
            elif mopDocumentInstanceExists(mail.mop, cronDocument, randomizedDocument):
                #TODO what if document is used?
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_existing_document, mail.requisitionInstance.data)
            else:
                assignDocument(mail.mop, cronDocument, randomizedDocument)
                newMail.subject = Mail.SUBJECT_RECEIVE_DOCUMENT
                newMail.body = generateBody(mail.unit.mail_assigning_document, mail.requisitionInstance.data)
        elif mail.subject == Mail.SUBJECT_SUBMIT_DOCUMENT:
            mail.mopDocumentInstance.status = MopDocumentInstance.STATUS_REPORTED
            mail.mopDocumentInstance.save()
            newMail.subject = Mail.SUBJECT_REPORT_EVALUATION
            if mail.mopDocumentInstance.correct:
                newMail.body = generateBody(mail.unit.mail_report_success, mail.requisitionInstance.data)
            else:
                newMail.body = generateBody(mail.unit.mail_report_fail, mail.requisitionInstance.data)
        else:
            newMail.subject = Mail.SUBJECT_UNCAUGHT_CASE
            newMail.body = "Yo35ur ma$$@il could%#34 n#$2ot b24e del$#i%#ve%#red. Som$#et2222hing we42 nt w@$rong."

        mail.processed = True
        mail.save()
        newMail.save()
        if newMail.subject == Mail.SUBJECT_ERROR:
            if not mail.mopDocumentInstance == None:
                mail.mopDocumentInstance.used = False
                mail.mopDocumentInstance.save()
   
    return output

def generateBody(text, data=None):
    t = Template(text)
    c = Context({"data": data})
    return t.render(c)

# def solveTask(taskInstance):
#     taskInstance.status = TaskInstance.STATUS_SOLVED
#     taskInstance.save()
#     
# def failTask(taskInstance):
#     taskInstance.status = TaskInstance.STATUS_FAILED
#     taskInstance.save()

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
           

def getRequisition(mail):
    try:
        requisition = Requisition.objects.get(serial=mail.requisitionInstance.data)
    except Requisition.DoesNotExist:
        requisition = None
    return requisition

# def getTask(mail):
#     return Task.objects.filter(unit=mail.unit).order_by('?')[0]
#     #TODO filter for clearance

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
       
    
def assignDocument(mop, cronDocument, randomizedDocument):
    if not cronDocument == None:
        mopDocumentInstance, created = MopDocumentInstance.objects.get_or_create(mop=mop, cronDocument=cronDocument, type=MopDocumentInstance.TYPE_CRON)
    else:
        mopDocumentInstance, created = MopDocumentInstance.objects.get_or_create(mop=mop, randomizedDocument=randomizedDocument, type=MopDocumentInstance.TYPE_MOP)



def prepareMail(mail):
    newMail = Mail()
    newMail.mop = mail.mop
    newMail.unit = mail.unit
    newMail.type = Mail.TYPE_RECEIVED
    newMail.processed = True
    return newMail
    