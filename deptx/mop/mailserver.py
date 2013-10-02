from mop.models import Mail, TaskInstance, DocumentInstance, RequisitionBlank
from cron.models import CronDocumentInstance
from assets.models import Requisition, Task, Document
from django.template import Context, loader, Template
import logging

def analyze_mail(mop):
    logging.info("Running analyse mail on mop.id %s" % mop.id);
    print "checking inbox of mailserver..."
    mail_list = Mail.objects.filter(mop=mop).filter(processed=False).filter(type=Mail.TYPE_SENT).filter(state=Mail.STATE_NORMAL)
    
    print "unprocessed mails: %d" % mail_list.count()
    for mail in mail_list:
        newMail = prepareMail(mail)
        if mail.unit is None:
            newMail.subject = Mail.SUBJECT_ERROR
            mail_tpl = loader.get_template('mop/mail/no_unit.txt')
            c = Context()
            newMail.body = mail_tpl.render(c)
        elif mail.subject is Mail.SUBJECT_EMPTY:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = generateBody(mail.unit.mail_error_no_subject)
        elif mail.requisitionInstance is None:
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
        elif mail.subject is Mail.SUBJECT_REQUEST_FORM:
            requisition = getRequisition(mail)
            if requisition is None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_unfound_form, mail.requisitionInstance.data)
            elif requisitionBlankExists(mail.mop, requisition):
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_existing_form, mail.requisitionInstance.data)
            else:
                assignRequisition(mail.mop, requisition)
                newMail.subject = Mail.SUBJECT_RECEIVE_FORM
                newMail.body = generateBody(mail.unit.mail_assigning_form, mail.requisitionInstance.data)
        elif mail.subject is Mail.SUBJECT_REQUEST_TASK:
            task = getTask(mail)
            if task is None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_unfound_task, mail.requisitionInstance.data)
            elif taskInstanceExists(mail.mop, task):
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_existing_task, mail.requisitionInstance.data)
            else:
                assignTask(mail.mop, task)
                newMail.subject = Mail.SUBJECT_RECEIVE_TASK
                newMail.body = generateBody(mail.unit.mail_assigning_task, mail.requisitionInstance.data)
        elif mail.subject is Mail.SUBJECT_REQUEST_DOCUMENT:
            document = getDocument(mail)
            if document is None:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_unfound_document, mail.requisitionInstance.data)
            elif documentInstanceExists(mail.mop, document):
                #TODO what if document is used?
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = generateBody(mail.unit.mail_error_existing_document, mail.requisitionInstance.data)
            else:
                assignDocument(mail.mop, document)
                newMail.subject = Mail.SUBJECT_RECEIVE_DOCUMENT
                newMail.body = generateBody(mail.unit.mail_assigning_document, mail.requisitionInstance.data)
        elif mail.subject is Mail.SUBJECT_SUBMIT_REPORT:
            taskInstance = getTaskInstance(mail)
            if taskInstance is None:
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
        print newMail.body
        if newMail.subject is Mail.SUBJECT_ERROR:
            if not mail.documentInstance is None:
                mail.documentInstance.used = False
                mail.documentInstance.save()
    
    return mail_list.count()


def generateBody(text, data=None):
    t = Template(text)
    c = Context({"data": data})
    return t.render(c)

def solveTask(taskInstance):
    taskInstance.state = TaskInstance.STATE_SOLVED
    taskInstance.save()
    
def failTask(taskInstance):
    taskInstance.state = TaskInstance.STATE_FAILED
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

def documentInstanceExists(mop, document):
    try:
        documentInstance = DocumentInstance.objects.get(mop=mop, document=document)
        return True
    except DocumentInstance.DoesNotExist:
        return False

def getRequisition(mail):
    if not mail.unit.isAdministrative:
        return None
    try:
        requisition = Requisition.objects.get(serial=mail.requisitionInstance.data)
    except Requisition.DoesNotExist:
        requisition = None
    return requisition

def getTask(mail):
    try:
        task = Task.objects.get(serial=mail.requisitionInstance.data, unit=mail.unit)
    except Task.DoesNotExist:
        task = None
    return task

def getDocument(mail):
    try:
        document = Document.objects.get(serial=mail.requisitionInstance.data, unit=mail.unit)
    except Document.DoesNotExist:
        document = None
    return document

def getTaskInstance(mail):
    try:
        task = getTask(mail)
        if not task is None:
            taskInstance = TaskInstance.objects.get(mop=mail.mop, task=task, state=TaskInstance.STATE_ACTIVE)
            if not taskInstance.task.unit == mail.unit:
                return None
        else:
            return None
    except TaskInstance.DoesNotExist:
        taskInstance = None
    return taskInstance
    
def subjectMatchesRequisition(mail):
    logging.info("checking subjectMatchesRequisition");
    logging.info("mail.subject is Mail.SUBJECT_REQUEST_FORM ???");
    logging.info("%s is %s ???" % (mail.subject, Mail.SUBJECT_REQUEST_FORM))
    if mail.subject == Mail.SUBJECT_REQUEST_FORM:
        logging.info("mail.requisitionInstance.blank.requisition.category is Requisition.CATEGORY_FORM ???")
        logging.info("%s %s" % (mail.subject, Mail.SUBJECT_REQUEST_FORM))
        if mail.requisitionInstance.blank.requisition.category is Requisition.CATEGORY_FORM:
            logging.info("subject matches request form");
            return True
    elif mail.subject is Mail.SUBJECT_REQUEST_TASK:
        if mail.requisitionInstance.blank.requisition.category is Requisition.CATEGORY_TASK:
            return True
    elif mail.subject is Mail.SUBJECT_REQUEST_DOCUMENT:
        if mail.requisitionInstance.blank.requisition.category is Requisition.CATEGORY_DOCUMENT:
            return True
    elif mail.subject is Mail.SUBJECT_SUBMIT_REPORT:
        if mail.requisitionInstance.blank.requisition.category is Requisition.CATEGORY_SUBMISSION:
            return True
    return False

def redundantDocument(mail):
    if not mail.subject is Mail.SUBJECT_SUBMIT_REPORT:
        if not mail.documentInstance is None:
            return True
    return False

def missingDocument(mail):
    if mail.subject is Mail.SUBJECT_SUBMIT_REPORT:
        if mail.documentInstance is None:
            return True
    return False

def wrongDocument(mail):
    if mail.subject is Mail.SUBJECT_SUBMIT_REPORT:
        try:
            task = Task.objects.get(serial=mail.requisitionInstance.data)
        except Task.DoesNotExist:
            task = None
        if not task is None:
            if not mail.documentInstance.document == task.document:
                return True
    return False

        
#TODO display attachments when viewing mails
def assignRequisition(mop, requisition):
    requisitionBlank, created = RequisitionBlank.objects.get_or_create(mop=mop, requisition=requisition)
       
def assignTask(mop, task):
    taskInstance, created = TaskInstance.objects.get_or_create(mop=mop, task=task)
    
def assignDocument(mop, document):
    documentInstance, created = DocumentInstance.objects.get_or_create(mop=mop, document=document)


def prepareMail(mail):
    newMail = Mail()
    newMail.mop = mail.mop
    newMail.unit = mail.unit
    newMail.type = Mail.TYPE_RECEIVED
    newMail.processed = True
    return newMail
    