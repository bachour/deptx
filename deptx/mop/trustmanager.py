from datetime import date, timedelta

def tm_getTotalTrust(mop):
    from mop.models import WeekTrust
    trust = 0
    weekTrust_list = WeekTrust.objects.filter(mop=mop)
    for weekTrust in weekTrust_list:
        trust += weekTrust.trust
    return trust

def tm_getCurrentTrust(mop):
    from mop.models import WeekTrust
    trust = 0
    year, week, day = date.today().isocalendar()
    weekTrust, created = WeekTrust.objects.get_or_create(mop=mop, year=year, week=week)
    return weekTrust.trust

def tm_getCurrentTrustCredit(mop):
    from mop.models import WeekTrust
    lastWeek = tm_getPreviousWeekTrust(mop)
    credit = lastWeek.trust * 0.1
    return credit
    
def tm_getPreviousWeekTrust(mop):
    from mop.models import WeekTrust
    d = date.today() - timedelta(days=7)
    year, week, day = d.isocalendar()
    try:
        weekTrust = WeekTrust.objects.get(mop=mop, year=year, week=week)
    except WeekTrust.DoesNotExist:
        weekTrust = 0
    return weekTrust

def tm_getCurrentClearance(mop):
    from mop.models import WeekTrust
    lastWeek = tm_getPreviousWeekTrust(mop)
    return lastWeek.getClearance()
        
    
    
    
    