from django.template import Context, loader
from django.core.mail import EmailMessage

def mopTutorialDone(cron):
    email_tpl = loader.get_template('cron/mail/mopTutorialDone.txt')
    c = Context({
        'cron': cron,
        })
     
    email = EmailMessage(
        subject='[cr0n] Report to HQ',
        body= email_tpl.render(c), 
        to=[cron.email,],
    )
    #in settings.py you can configure console backend for displaying emails instead of sending them - great for testing!
    email.send(fail_silently=True)