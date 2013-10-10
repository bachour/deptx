from mop.models import Mail, TaskInstance, DocumentInstance, RequisitionBlank, Badge
from players.models import Mop
from assets.models import Requisition, Task, Document
from django.template import Context, loader, Template
import logging

def analyze_performance():
    output = []
    taskInstance_list = TaskInstance.objects.filter(status=TaskInstance.STATUS_ACTIVE)
    output.append('unfinished tasks: %d' % taskInstance_list.count())
    for taskInstance in taskInstance_list:
        taskInstance.status = TaskInstance.STATUS_UNSOLVED
        taskInstance.save()
        
    mop_list = Mop.objects.filter()
    output.append('MoPs under performance review: %d' % mop_list.count())
    for mop in mop_list:
        b = getBadge(mop.trust)
        badge = Badge.objects.create(mop=mop, badge=b)
        badge.save()
        mop.credit = mop.trust * 0.1
        mop.clearance = getClearance(mop.trust)
        mop.trust = 0
        mop.save()
    
    return output
        

def getClearance(trust):
    if trust >= 500:
        return Mop.CLEARANCE_3_HIGH
    elif trust >= 100:
        return Mop.CLEARANCE_2_MEDIUM
    elif trust >= 0:
        return Mop.CLEARANCE_1_LOW
    else:
        return Mop.CLEARANCE_0_NONE    

def getBadge(trust):
    if trust < 0:
        return Badge.BADGE_0
    elif trust < 10:
        return Badge.BADGE_1
    elif trust < 30:
        return Badge.BADGE_2
    elif trust < 50:
        return Badge.BADGE_3
    elif trust < 100:
        return Badge.BADGE_4
    elif trust < 150:
        return Badge.BADGE_5
    elif trust < 200:
        return Badge.BADGE_6
    elif trust < 250:
        return Badge.BADGE_7
    elif trust < 500:
        return Badge.BADGE_8
    elif trust < 750:
        return Badge.BADGE_9
    elif trust < 1000:
        return Badge.BADGE_10
    else:
        return Badge.BADGE_11
    
    