from mop.models import MopTracker, TrustInstance, Mail, MopDocumentInstance
from assets.models import Unit
from mop.clearance import proposed_clearance
from deptx.helpers import now

def analyze_performance():
    mopTracker_list = MopTracker.objects.all()
    for mopTracker in mopTracker_list:
        trustInstance = TrustInstance(mop=mopTracker.mop, totalTrust=mopTracker.totalTrust, oldTrust=mopTracker.trust, oldClearance=mopTracker.clearance)
        mopTracker.check_for_demotion()
        mopTracker.check_for_promotion()
        trustInstance.newClearance = mopTracker.clearance
        trustInstance.specialStatus = mopTracker.hasSpecialStatus
        if mopTracker.trust > 0:
            mopTracker.trust = mopTracker.trust * 0.9
        else:
            mopTracker.trust = 0
        trustInstance.newTrust = mopTracker.trust
        mopTracker.save()
        trustInstance.save()




            
