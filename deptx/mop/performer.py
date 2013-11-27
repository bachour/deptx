
from players.models import Mop
from mop.clearance import Clearance, getAdjustedClearance
from mop.models import MopDocumentInstance, TrustInstance, Mail
from mop.mailserver import sendReport

def analyze_performance():
    output = []
    
    mopDocumentInstance_list = MopDocumentInstance.objects.filter(status=MopDocumentInstance.STATUS_ACTIVE).filter(type=MopDocumentInstance.TYPE_MOP)
    output.append('unfinished documents: %d' % mopDocumentInstance_list.count())
    
    for mopDocumentInstance in mopDocumentInstance_list:
        mopDocumentInstance.status = mopDocumentInstance.STATUS_REVOKED
        mopDocumentInstance.save()
        trust = mopDocumentInstance.getTrustFinal()
        mopDocumentInstance.mop.mopTracker.addTrust(trust)
        mopDocumentInstance.mop.mopTracker.save()
        
    mop_list = Mop.objects.filter()
    output.append('MoPs under performance review: %d' % mop_list.count())
    for mop in mop_list:
        trustInstance = TrustInstance.objects.create(mop=mop, trust=mop.mopTracker.trust)
        #TODO add more statistics
        mop.mopTracker.totalTrust += mop.mopTracker.trust 
        mop.mopTracker.clearance = getAdjustedClearance(mop.mopTracker.clearance, mop.mopTracker.trust)
        mop.mopTracker.trust = 0
        mop.mopTracker.credit = trustInstance.credit()
        mop.mopTracker.save()
        sendReport(trustInstance)
        
    
    return output
        
