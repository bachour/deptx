# from logger.models import Log

from logger.models import ActionLog, ProvLog

def log_action(action, cron=None, fluff=None, mission=None, missionState=None, case=None, caseSolved=None, cronDocumentInstance=None, cronDocumentInstanceCorrect=None, message=None, successfulHack=None, mop=None, mail=None, mopDocumentInstance=None, mopDocumentInstanceCorrect=None, requisitionInstance=None, tutorialProgress=None):
    ActionLog.objects.create(action=action, cron=cron, fluff=fluff, mission=mission, missionState=missionState, case=case, caseSolved=caseSolved, cronDocumentInstance=cronDocumentInstance, cronDocumentInstanceCorrect=cronDocumentInstanceCorrect, message=message, successfulHack=successfulHack, mop=mop, mail=mail, mopDocumentInstance=mopDocumentInstance, mopDocumentInstanceCorrect=mopDocumentInstanceCorrect, requisitionInstance=requisitionInstance, tutorialProgress=tutorialProgress)
    
def log_prov(action, cronDocumentInstance=None, mopDocumentInstance=None, node1=None, node2=None, attribute1=None, attribute2=None, x=None, y=None, selected=None, empty=None, correct=None, inactive=None):
    ProvLog.objects.create(action=action, cronDocumentInstance=cronDocumentInstance, mopDocumentInstance=mopDocumentInstance, node1=node1, node2=node2, attribute1=attribute1, attribute2=attribute2, x=x, y=y, selected=selected, empty=empty, correct=correct, inactive=inactive)