from mop.models import Mail, MopDocumentInstance, RequisitionBlank, RandomizedDocument
from assets.models import Requisition, CronDocument, Unit
import logging
from mop.clearance import Clearance
import tutorial
from django.template import Context, loader
from django.core.mail import EmailMessage
from deptx.helpers import now
from random import getrandbits
from logger.models import ActionLog
from logger import logging 
from mop.models import MopTracker


try:
    from deptx.settings_production import TO_ALL
except:
    TO_ALL = ["1@localhost.com", "2@localhost.com"]

DELAY_SHORT = 0 * 60
DELAY_MEDIUM = 1 * 60
DELAY_LONG = 3 * 60 
DELAY_SUPERLONG = 57 * 60

SPECIAL_STATUS_HACK_1 = "agent"
SPECIAL_STATUS_HACK_2 = "entity"
SPECIAL_STATUS_HACK_3 = "actitivy"

def delayedEnough(mail, delay):
    if mail.mop.mopTracker.tutorial < MopTracker.TUTORIAL_6_DONE:
        print "tutorial so no delay"
        return True
    elif mail.mop.user.is_staff:
        print "staff so no delay"
        return True
    
    difference = (now() - mail.sentAt).total_seconds()
    if difference >= delay:
        if getrandbits(1):
            print "coin win"
            return True
        else:
            print "coin loss"
            return False
    else:
        print "too fresh"
        return False
    

def getUnprocessedMails():
    return Mail.objects.filter(processed=False).filter(type=Mail.TYPE_SENT).order_by('?')

def analyze_mail():
    output = []
    mail_list = getUnprocessedMails()
    #TODO add more output
    output.append("Unprocessed mails: %d" % mail_list.count())
    for mail in mail_list:
        check_mail(mail)
    return output

def check_mail(mail):
        if mail.requisitionInstance is not None and mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_HELP:
            subject = "[MoP] %s: Help Request (Cron: %s)" % (mail.mop.user.username, mail.mop.cron.user.username)
            create_player_email(mail, subject)
            return
        elif mail.requisitionInstance is not None and mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_SPECIAL_REPORT:
            subject = "[MoP] %s: MOPAIN Report (Cron: %s)" % (mail.mop.user.username, mail.mop.cron.user.username)
            create_player_email(mail, subject)
            return    
        else:    
            newMail = prepareMail(mail)    
            if mail.requisitionInstance is not None and mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_SPECIAL_APPLY:
                if not delayedEnough(mail, DELAY_SUPERLONG):
                    return
                #deny because already
                if mail.mop.mopTracker.specialStatusAllowed:
                    newMail.subject = Mail.SUBJECT_SPECIAL_DENIED
                    newMail.bodyType = Mail.BODY_SPECIAL_ALREADY
                    newMail.trust = -100
                else:
                    #deny because shit
                    if not check_special_hack(mail.requisitionInstance.data) or not mail.mop.mopTracker.clearance >= Clearance.CLEARANCE_RED:
                        newMail.subject = Mail.SUBJECT_SPECIAL_DENIED
                        newMail.bodyType = Mail.BODY_SPECIAL_DENIED
                        newMail.trust = -250
                    #grant
                    else:
                        newMail.subject = Mail.SUBJECT_SPECIAL_GRANTED
                        newMail.bodyType = Mail.BODY_SPECIAL_GRANTED
                        newMail.trust = 500
                        mail.mop.mopTracker.specialStatusAllowed = True
                        mail.mop.mopTracker.save()
            
            elif mail.unit == None:
                if not delayedEnough(mail, DELAY_SHORT):
                    return
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_MISSING_UNIT
                #if there is no unit an error is generated automatically - no need to set it manually
            elif mail.subject == Mail.SUBJECT_EMPTY:
                if not delayedEnough(mail, DELAY_SHORT):
                    return
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_NO_SUBJECT
            elif mail.requisitionInstance == None:
                if not delayedEnough(mail, DELAY_SHORT):
                    return
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_MISSING_FORM
            elif not mail.unit == mail.requisitionInstance.blank.requisition.unit:
                if not delayedEnough(mail, DELAY_SHORT):
                    return
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_WRONG_UNIT
            elif not (subjectMatchesRequisition(mail)):
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_WRONG_FORM
            elif redundantDocument(mail):
                if not delayedEnough(mail, DELAY_SHORT):
                    return
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_REDUNDANT_DOCUMENT
            elif missingDocument(mail):
                if not delayedEnough(mail, DELAY_SHORT):
                    return
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_MISSING_DOCUMENT
            elif wrongDocument(mail):
                if not delayedEnough(mail, DELAY_SHORT):
                    return
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.bodyType = Mail.BODY_ERROR_WRONG_DOCUMENT
            #Now the mail should be formally correct
            #Let's see about the content!
            elif mail.subject == Mail.SUBJECT_REQUEST_FORM:
                requisition = getRequisition(mail)
                if requisition == None:
                    if not delayedEnough(mail, DELAY_SHORT):
                        return
                    newMail.subject = Mail.SUBJECT_ERROR
                    newMail.bodyType = Mail.BODY_ERROR_UNFOUND_FORM
                elif requisitionBlankExists(mail.mop, requisition):
                    if not delayedEnough(mail, DELAY_SHORT):
                        return
                    newMail.subject = Mail.SUBJECT_ERROR
                    newMail.bodyType = Mail.BODY_ERROR_EXISTING_FORM
                else:
                    if not delayedEnough(mail, DELAY_MEDIUM):
                        return
                    requisitionBlank = assignRequisition(mail.mop, requisition)
                    newMail.requisitionBlank = requisitionBlank
                    newMail.subject = Mail.SUBJECT_RECEIVE_FORM
                    newMail.bodyType = Mail.BODY_ASSIGNING_FORM
            elif mail.subject == Mail.SUBJECT_REQUEST_DOCUMENT:
                #The serial inside the form could be either for a mop or for a cron 'document'
                cronDocument = getCronDocument(mail)
                randomizedDocument = getRandomizedDocument(mail)
                if cronDocument == None and randomizedDocument == None:
                    if not delayedEnough(mail, DELAY_SHORT):
                        return
                    newMail.subject = Mail.SUBJECT_ERROR
                    newMail.bodyType = Mail.BODY_ERROR_UNFOUND_DOCUMENT
                elif mopDocumentInstanceExists(mail.mop, cronDocument, randomizedDocument):
                    if not delayedEnough(mail, DELAY_SHORT):
                        return
                    #TODO what if document is used?
                    newMail.subject = Mail.SUBJECT_ERROR
                    newMail.bodyType = Mail.BODY_ERROR_EXISTING_DOCUMENT
                elif not hasEnoughTrust(mail.mop, cronDocument, randomizedDocument):
                    if not delayedEnough(mail, DELAY_SHORT):
                        return
                    newMail.subject = Mail.SUBJECT_ERROR
                    newMail.bodyType = Mail.BODY_ERROR_LACKING_TRUST
                else:
                    if not delayedEnough(mail, DELAY_MEDIUM):
                        return
                    mopDocumentInstance = assignDocument(mail.mop, cronDocument, randomizedDocument)
                    newMail.mopDocumentInstance = mopDocumentInstance
                    clearance = Clearance(mopDocumentInstance.getClearance())
                    newMail.trust = clearance.getTrustRequested()
                    newMail.subject = Mail.SUBJECT_RECEIVE_DOCUMENT
                    newMail.bodyType = Mail.BODY_ASSIGNING_DOCUMENT
            elif mail.subject == Mail.SUBJECT_SUBMIT_DOCUMENT:
                clearance = Clearance(mail.mopDocumentInstance.getClearance())
                newMail.subject = Mail.SUBJECT_REPORT_EVALUATION
                newMail.mopDocumentInstance = mail.mopDocumentInstance
                if mail.mopDocumentInstance.correct:
                    if not delayedEnough(mail, DELAY_LONG):
                        return
                    newMail.bodyType = Mail.BODY_REPORT_SUCCESS
                    newMail.trust = clearance.getTrustReportedCorrect()
                    tutorial.submitDocument(mail.mop.mopTracker)
                else:
                    if not delayedEnough(mail, DELAY_LONG):
                        return
                    newMail.bodyType = Mail.BODY_REPORT_FAIL
                    newMail.trust = clearance.getTrustReportedIncorrect()
                mail.mopDocumentInstance.status = MopDocumentInstance.STATUS_REPORTED
                mail.mopDocumentInstance.save()
            else:
                if not delayedEnough(mail, DELAY_SHORT):
                    return
                newMail.subject = Mail.SUBJECT_UNCAUGHT_CASE
                newMail.body = Mail.BODY_UNCAUGHT_CASE
                
    
            if newMail.subject == Mail.SUBJECT_ERROR:
                newMail.trust = -1
                
                if not mail.mopDocumentInstance == None:
                    mail.mopDocumentInstance.status = MopDocumentInstance.STATUS_ACTIVE
                    mail.mopDocumentInstance.save()
                    newMail.mopDocumentInstance = mail.mopDocumentInstance
               
    
            mail.processed = True
            mail.save()
            newMail.save()
            
            if newMail.trust is not None:
                forTotal = True
                if newMail.subject == Mail.SUBJECT_RECEIVE_DOCUMENT:
                    forTotal = False
                mail.mop.mopTracker.addTrust(newMail.trust, forTotal)
                
            if newMail.subject == Mail.SUBJECT_ERROR:
                logging.log_action(ActionLog.ACTION_MOP_RECEIVE_MAIL_ERROR, mop=mail.mop, mail=newMail)
            elif newMail.subject == Mail.SUBJECT_RECEIVE_DOCUMENT:
                logging.log_action(ActionLog.ACTION_MOP_RECEIVE_MAIL_DOCUMENT, mop=mail.mop, mail=newMail)
            elif newMail.subject == Mail.SUBJECT_RECEIVE_FORM:
                logging.log_action(ActionLog.ACTION_MOP_RECEIVE_MAIL_FORM, mop=mail.mop, mail=newMail)
            elif newMail.subject == Mail.SUBJECT_REPORT_EVALUATION:
                logging.log_action(ActionLog.ACTION_MOP_RECEIVE_MAIL_REPORT, mop=mail.mop, mail=newMail)
            elif newMail.subject == Mail.SUBJECT_SPECIAL_DENIED:
                logging.log_action(ActionLog.ACTION_MOP_RECEIVE_MAIL_SPECIAL_DENIED, mop=mail.mop, mail=newMail)
            elif newMail.subject == Mail.SUBJECT_SPECIAL_GRANTED:
                logging.log_action(ActionLog.ACTION_MOP_RECEIVE_MAIL_SPECIAL_GRANTED, mop=mail.mop, mail=newMail)
           

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
    elif mop.mopTracker.trust + trustCost >=0:
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
            return True
    elif mail.subject == Mail.SUBJECT_REQUEST_DOCUMENT:
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_DOCUMENT:
            return True
    elif mail.subject == Mail.SUBJECT_SUBMIT_DOCUMENT:
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_SUBMISSION:
            return True
    elif mail.subject == Mail.SUBJECT_EMPTY:
        if mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_SPECIAL_APPLY:
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
    tutorial.assignForm(mop.mopTracker)
    return requisitionBlank
       
    
def assignDocument(mop, cronDocument, randomizedDocument):
    if not cronDocument == None:
        mopDocumentInstance, created = MopDocumentInstance.objects.get_or_create(mop=mop, cronDocument=cronDocument, type=MopDocumentInstance.TYPE_CRON)
    else:
        mopDocumentInstance, created = MopDocumentInstance.objects.get_or_create(mop=mop, randomizedDocument=randomizedDocument, type=MopDocumentInstance.TYPE_MOP)
        tutorial.assignDocument(mop.mopTracker)
    return mopDocumentInstance

def prepareMail(mail):
    newMail = Mail()
    newMail.mop = mail.mop
    newMail.unit = mail.unit
    newMail.type = Mail.TYPE_RECEIVED
    newMail.processed = True
    newMail.replyTo = mail
    return newMail

def create_player_email(mail, subject):
    email_tpl = loader.get_template('mop/mail/message_from_player.txt')
    c = Context({'body':mail.requisitionInstance.data})
    email = EmailMessage(subject=subject, body=email_tpl.render(c), to=TO_ALL)
    email.send(fail_silently=False)
    mail.unit = mail.requisitionInstance.blank.requisition.unit
    mail.subject = Mail.SUBJECT_HELP
    mail.processed = True
    mail.needsReply = True
    mail.save()


def check_special_hack(data):
    data = data.lower()
    if SPECIAL_STATUS_HACK_1 in data and SPECIAL_STATUS_HACK_2 in data and SPECIAL_STATUS_HACK_3 in data:
        return True
    else:
        return False

    