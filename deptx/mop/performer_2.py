from mop.models import MopTracker, TrustInstance, Mail, MopDocumentInstance
from assets.models import Unit
from mop.clearance import proposed_clearance
from deptx.helpers import now
from datetime import timedelta

def analyze_performance():
    mopTracker_list = MopTracker.objects.all()
    for mopTracker in mopTracker_list:
        trustInstance = TrustInstance(mop=mopTracker.mop, totalTrust=mopTracker.totalTrust, oldTrust=mopTracker.trust, oldClearance=mopTracker.clearance)
        mopTracker.check_for_demotion()
        mopTracker.check_for_promotion()
        trustInstance.newClearance = mopTracker.clearance
        trustInstance.specialStatus = mopTracker.hasSpecialStatus
        try:
            mopDocumentInstance = MopDocumentInstance.objects.filter(mop=mopTracker.mop, correct=True, status=MopDocumentInstance.STATUS_REPORTED).order_by('-modifiedAt')[0]
        except:
            mopDocumentInstance = None
        if not mopDocumentInstance == None:
            age = now() - mopDocumentInstance.modifiedAt
            if age > timedelta(days=3):
                if mopTracker.trust > 0:
                    mopTracker.trust = mopTracker.trust * 0.9
                else:
                    mopTracker.trust = 0
        trustInstance.newTrust = mopTracker.trust
        mopTracker.save()
        trustInstance.save()




            
