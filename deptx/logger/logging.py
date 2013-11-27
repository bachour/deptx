# from logger.models import Log

from logger.models import ProvLog

def log_cron(cron, action, data=''):
    pass
    #log = Log(cron=cron, action=action, data=data)
    #log.save()
     
def log_mop(mop, action, data=''):
    pass
    #cron = mop.cron
    #log = Log(cron=cron, mop=mop, action=action, data=data)
    #log.save()
    
    
def log_prov(action, cronDocumentInstance=None, mopDocumentInstance=None, node1=None, node2=None, attribute1=None, attribute2=None, x=None, y=None, selected=None, empty=None, correct=None):
    ProvLog.objects.create(action=action, cronDocumentInstance=cronDocumentInstance, mopDocumentInstance=mopDocumentInstance, node1=node1, node2=node2, attribute1=attribute1, attribute2=attribute2, x=x, y=y, selected=selected, empty=empty, correct=correct)