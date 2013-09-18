from logger.models import Log

def log_cron(cron, action, data=''):
    log = Log(cron=cron, action=action, data=data)
    log.save()
    
def log_mop(mop, action, data=''):
    cron = mop.player.cron
    log = Log(cron=cron, mop=mop, action=action, data=data)
    log.save()