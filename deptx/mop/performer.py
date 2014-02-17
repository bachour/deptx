
from players.models import Mop
from mop.clearance import Clearance, convertTrustIntoClearance
from mop.models import MopDocumentInstance, PerformanceInstance, Mail, PerformancePeriod, MopTracker
from assets.models import Unit
from logger.models import ActionLog
from logger import logging
from deptx.helpers import now
import datetime


def doPerformance(mop, thisPeriod, days):
    performanceInstance = PerformanceInstance(mop=mop, trust=mop.mopTracker.trust, period=thisPeriod)
    performanceInstance.performance, performanceInstance.result, performanceInstance.type = checkPromotion(mop.mopTracker, days)
    output = '%s gained %s TRUST. Rating: %s. Old Level: %s. New Level: %s. Result: %s' %(performanceInstance.mop.user.username, performanceInstance.trust, performanceInstance.get_performance_display(), mop.mopTracker.get_clearance_display(), performanceInstance.get_result_display(), performanceInstance.get_type_display())
    return performanceInstance, output        

def getPeriods():
    lastPeriod = PerformancePeriod.objects.filter(processed=True).order_by('-reviewDate')[0]
    thisPeriod = PerformancePeriod.objects.filter(processed=False).order_by('reviewDate')[0]
    days = (thisPeriod.reviewDate - lastPeriod.reviewDate).days
    return lastPeriod, thisPeriod, days
    
def analyze_performance(simulation=False):
    output = []
    
    if simulation:
        output.append('RUNNING SIMULATION')
    
    #if not simulation:
    #    revokeDocuments()
       
    mopTracker_list = MopTracker.objects.all().order_by('trust')
    output.append('MoPs under performance review: %d' % mopTracker_list.count())
    lastPeriod, thisPeriod, days = getPeriods()
    today = now().date()

    if not simulation:
        if not thisPeriod.reviewDate == today:
            output.append('No review scheduled for today (%s). Next review scheduled for %s' % (today, thisPeriod.reviewDate))
            return output
        output.append('Last review: %s, This review: %s, Days since last review: %s' % (lastPeriod.reviewDate, thisPeriod.reviewDate, days))
        if days == 0:
            output.append('No performance review possible.')
            return output
    else:
        output.append('Last review: %s, This review: %s, Days since last review: %s' % (lastPeriod.reviewDate, thisPeriod.reviewDate, days))

    for mopTracker in mopTracker_list:    
        performanceInstance, out = doPerformance(mopTracker.mop, thisPeriod, days)
        output.append(out)
        if simulation:
            continue
        performanceInstance.save()
        
        mopTracker.clearance = performanceInstance.result
        mopTracker.totalTrust += mopTracker.trust 
        mopTracker.trust = 0
        mopTracker.credit = performanceInstance.credit
        mopTracker.save()
        
        unit = Unit.objects.filter(type=Unit.TYPE_ADMINISTRATIVE)[0]
        
        mail = Mail(mop=mopTracker.mop, performanceInstance=performanceInstance, unit=unit, subject=Mail.SUBJECT_INFORMATION, type=Mail.TYPE_RECEIVED)
        if performanceInstance.type == PerformanceInstance.TYPE_PROMOTION:
            mail.bodyType=Mail.BODY_PERFORMANCE_REPORT_PROMOTION
        elif performanceInstance.type == PerformanceInstance.TYPE_DEMOTION:
            mail.bodyType=Mail.BODY_PERFORMANCE_REPORT_DEMOTION
        else:
            mail.bodyType=Mail.BODY_PERFORMANCE_REPORT_NEUTRAL 
        mail.save()
        logging.log_action(ActionLog.ACTION_MOP_RECEIVE_MAIL_PERFORMANCE, mop=mopTracker.mop, mail=mail)
    if not simulation:
        thisPeriod.processed = True
        thisPeriod.reviewTime = now().time()
        thisPeriod.save()
        if not PerformancePeriod.objects.filter(processed=False):
            newPeriod = PerformancePeriod()
            newDate = thisPeriod.reviewDate + datetime.timedelta(days=14)
            newPeriod.reviewDate = newDate
            newPeriod.save()
    return output
 
def checkPromotion(mopTracker, days):
    proposedClearance = convertTrustIntoClearance(mopTracker.trust, days)
    
    newClearance = mopTracker.clearance
    if proposedClearance > mopTracker.clearance:
        if mopTracker.clearance == Clearance.CLEARANCE_BLUE:
            newClearance = Clearance.CLEARANCE_GREEN
        elif mopTracker.clearance == Clearance.CLEARANCE_GREEN:
            newClearance = Clearance.CLEARANCE_YELLOW
        elif mopTracker.clearance == Clearance.CLEARANCE_YELLOW:
            newClearance = Clearance.CLEARANCE_ORANGE
        elif mopTracker.clearance == Clearance.CLEARANCE_ORANGE:
            newClearance = Clearance.CLEARANCE_RED
    elif proposedClearance < mopTracker.clearance:
        if mopTracker.clearance == Clearance.CLEARANCE_RED:
            newClearance = Clearance.CLEARANCE_ORANGE
        elif mopTracker.clearance == Clearance.CLEARANCE_ORANGE:
            newClearance = Clearance.CLEARANCE_YELLOW
        elif mopTracker.clearance == Clearance.CLEARANCE_YELLOW:
            newClearance = Clearance.CLEARANCE_GREEN
        elif mopTracker.clearance == Clearance.CLEARANCE_GREEN:
            newClearance = Clearance.CLEARANCE_BLUE
    
    if newClearance > mopTracker.clearance:
        type = PerformanceInstance.TYPE_PROMOTION
    elif newClearance < mopTracker.clearance:
        type = PerformanceInstance.TYPE_DEMOTION
    else:
        type = PerformanceInstance.TYPE_NEUTRAL
    
    return proposedClearance, newClearance, type
    
    
     
def revokeDocuments():
    mopDocumentInstance_list = MopDocumentInstance.objects.filter(status=MopDocumentInstance.STATUS_ACTIVE).filter(type=MopDocumentInstance.TYPE_MOP)
    #output = 'unfinished documents: %d' % mopDocumentInstance_list.count()
    
    for mopDocumentInstance in mopDocumentInstance_list:
        #TODO generate emails for revoking
        mopDocumentInstance.status = mopDocumentInstance.STATUS_REVOKED
        mopDocumentInstance.save()
        trust = mopDocumentInstance.getTrustFinal()
        mopDocumentInstance.mop.mopTracker.addTrust(trust)
        mopDocumentInstance.mop.mopTracker.save()
    #return output 

    
            
