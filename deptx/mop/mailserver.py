from mop.models import Mail, TaskInstance, DocumentInstance, RequisitionBlank
from cron.models import CronDocumentInstance
from assets.models import Requisition, Task, Document
from django.template import Context, loader, Template
import logging
from provmanager.views import randomize_task

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
        elif mail.subject == Mail.SUBJECT_REQUEST_TASK:
            #TODO check for clearance etc. Tasks can no longer be 'unfound'
            task = getTask(mail)
            if task == None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_unfound_task, mail.requisitionInstance.data)
#            #no longer needed as each 'task' is unique
#             elif taskInstanceExists(mail.mop, task):
#                 newMail.subject = Mail.SUBJECT_ERROR
#                 newMail.body = generateBody(mail.unit.mail_error_existing_task, mail.requisitionInstance.data)
            else:
                serial = assignTask(mail.mop, task)
                newMail.subject = Mail.SUBJECT_RECEIVE_TASK
                newMail.body = generateBody(mail.unit.mail_assigning_task, serial)
        elif mail.subject == Mail.SUBJECT_REQUEST_DOCUMENT:
            #The serial inside the form could be either for a mop or for a cron 'document'
            cronDocument = getCronDocument(mail)
            mopDocumentInstance = getMopDocumentInstance(mail)
            if cronDocument == None and mopDocumentInstance == None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_unfound_document, mail.requisitionInstance.data)
            elif documentInstanceExists(mail.mop, cronDocument, mopDocumentInstance):
                #TODO what if document is used?
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_existing_document, mail.requisitionInstance.data)
            else:
                assignDocument(mail.mop, cronDocument, mopDocumentInstance)
                newMail.subject = Mail.SUBJECT_RECEIVE_DOCUMENT
                newMail.body = generateBody(mail.unit.mail_assigning_document, mail.requisitionInstance.data)
        elif mail.subject == Mail.SUBJECT_SUBMIT_REPORT:
            taskInstance = getTaskInstance(mail)
            if taskInstance == None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_unassigned_task, mail.requisitionInstance.data)
            else:
                newMail.subject = Mail.SUBJECT_REPORT_EVALUATION
                if mail.documentInstance.correct:
                    solveTask(taskInstance)
                    newMail.body = generateBody(mail.unit.mail_report_success, mail.requisitionInstance.data)
                else:
                    failTask(taskInstance)
                    newMail.body = generateBody(mail.unit.mail_report_fail, mail.requisitionInstance.data)
        else:
            newMail.subject = Mail.SUBJECT_UNCAUGHT_CASE
            newMail.body = "Yo35ur ma$$@il could%#34 n#$2ot b24e del$#i%#ve%#red. Som$#et2222hing we42 nt w@$rong."
        

        mail.processed = True
        mail.save()
        newMail.save()
        if newMail.subject == Mail.SUBJECT_ERROR:
            if not mail.documentInstance == None:
                mail.documentInstance.used = False
                mail.documentInstance.save()
    
    return output

def generateBody(text, data=None):
    t = Template(text)
    c = Context({"data": data})
    return t.render(c)

def solveTask(taskInstance):
    taskInstance.status = TaskInstance.STATUS_SOLVED
    taskInstance.save()
    
def failTask(taskInstance):
    taskInstance.status = TaskInstance.STATUS_FAILED
    taskInstance.save()

def requisitionBlankExists(mop, requisition):
    try:
        requisitionBlank = RequisitionBlank.objects.get(mop=mop, requisition=requisition)
        return True
    except RequisitionBlank.DoesNotExist:
        return False

def taskInstanceExists(mop, task):
    try:
        taskInstance = TaskInstance.objects.get(mop=mop, task=task)
        return True
    except TaskInstance.DoesNotExist:
        return False

def documentInstanceExists(mop, cronDocument, mopDocumentInstance):
    if not cronDocument == None:
        try:
            documentInstance = DocumentInstance.objects.get(mop=mop, document=cronDocument)
            return True
        except DocumentInstance.DoesNotExist:
            return False
    return mopDocumentInstance.acquired
            

def getRequisition(mail):
    try:
        requisition = Requisition.objects.get(serial=mail.requisitionInstance.data)
    except Requisition.DoesNotExist:
        requisition = None
    return requisition

def getTask(mail):
    return Task.objects.filter(unit=mail.unit).order_by('?')[0]
    #TODO filter for clearance
    

def getCronDocument(mail):
    try:
        document = Document.objects.get(serial=mail.requisitionInstance.data)
    except Document.DoesNotExist:
        document = None
    return document

def getMopDocumentInstance(mail):
    try:
        documentInstance = DocumentInstance.objects.get(serial=mail.requisitionInstance.data, mop=mail.mop)
    except DocumentInstance.DoesNotExist:
        documentInstance = None
    return documentInstance

def getTaskInstance(mail):
    try:
        task = getTask(mail)
        if not task == None:
            taskInstance = TaskInstance.objects.get(mop=mail.mop, task=task, status=TaskInstance.STATUS_ACTIVE)
            if not taskInstance.task.unit == mail.unit:
                return None
        else:
            return None
    except TaskInstance.DoesNotExist:
        taskInstance = None
    return taskInstance
    
def subjectMatchesRequisition(mail):
    if int(mail.subject) == int(Mail.SUBJECT_REQUEST_FORM):
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_FORM:
            logging.info("subject matches request form");
            return True
    elif mail.subject == Mail.SUBJECT_REQUEST_TASK:
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_TASK:
            return True
    elif mail.subject == Mail.SUBJECT_REQUEST_DOCUMENT:
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_DOCUMENT:
            return True
    elif mail.subject == Mail.SUBJECT_SUBMIT_REPORT:
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_SUBMISSION:
            return True
    return False

def redundantDocument(mail):
    if not mail.subject == Mail.SUBJECT_SUBMIT_REPORT:
        if not mail.documentInstance == None:
            return True
    return False

def missingDocument(mail):
    if mail.subject == Mail.SUBJECT_SUBMIT_REPORT:
        if mail.documentInstance == None:
            return True
    return False

def wrongDocument(mail):
    if mail.subject == Mail.SUBJECT_SUBMIT_REPORT:
        try:
            task = Task.objects.get(serial=mail.requisitionInstance.data)
        except Task.DoesNotExist:
            task = None
        if not task == None:
            if not mail.documentInstance.document == task.document:
                return True
    return False

        
#TODO display attachments when viewing mails
def assignRequisition(mop, requisition):
    requisitionBlank, created = RequisitionBlank.objects.get_or_create(mop=mop, requisition=requisition)
       
def assignTask(mop, task):
    taskInstance = randomize_task(task, mop)
    return taskInstance.serial
    
def assignDocument(mop, cronDocument, mopDocumentInstance):
    if not cronDocument == None:
        documentInstance, created = DocumentInstance.objects.get_or_create(mop=mop, document=cronDocument)
    else:
        mopDocumentInstance.acquired = True
        mopDocumentInstance.save()



def prepareMail(mail):
    newMail = Mail()
    newMail.mop = mail.mop
    newMail.unit = mail.unit
    newMail.type = Mail.TYPE_RECEIVED
    newMail.processed = True
    return newMail
    