from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import Context, loader

from django.core.mail import EmailMessage
from forms import PlayerForm, CronForm
from django.contrib.auth.forms import UserCreationForm

from deptx.secrets import registration_passcode
from provmanager.provlogging import provlog_add_cron_register
from players.models import Cron


#TODO: Move registration over to CRON
#TODO: Request new activation link in case old one was lost
#TODO: Password reset
def register(request):
    if request.method == 'POST':
        cron_form = CronForm(request.POST, prefix="cron")
        user_form = UserCreationForm(request.POST, prefix = "user")
         
        passcode = request.POST.get('registration_passcode', '')
         
        if passcode == registration_passcode and cron_form.is_valid() and user_form.is_valid():
            user = user_form.save()
            cron = cron_form.save(commit=False)
            cron.user = user
            cron.save()
            
            provlog_add_cron_register(cron)
            
            email_tpl = loader.get_template('players/activation.txt')
            url_study = request.build_absolute_uri(reverse('players_activation_study', args=[cron.activationCode]))
            url_nostudy = request.build_absolute_uri(reverse('players_activation_nostudy', args=[cron.activationCode]))
            c = Context({
                'cron': cron, 'url_study':url_study, 'url_nostudy':url_nostudy
                })
             
            email = EmailMessage(
                subject='[cr0n] Activate your account',
                body= email_tpl.render(c), 
                to=[cron.email,],
            )
            #in settings.py you can configure console backend for displaying emails instead of sending them - great for testing!
            email.send(fail_silently=False)

            
             
            return render(request, 'players/registration.html', {"registered": True, "cron":cron})
        else:
            return render(request, 'players/registration.html', {"cron_form": cron_form, "user_form": user_form})
     
    else:
        cron_form = CronForm(prefix='cron')
        user_form = UserCreationForm(prefix='user')
        return render(request, 'players/registration.html', {"cron_form": cron_form, "user_form": user_form})
        
        
def activate_study(request, code):
    
    try:
        cron = Cron.objects.get(activationCode=code)
    except Cron.DoesNotExist:
        cron = None
    
    if cron == None:
        return render(request, 'players/registration.html', {"wrongCode": True})
    elif cron.activated:
        return render(request, 'players/registration.html', {"alreadyActivated": True})
    else:
        if request.method == 'POST':
            form = PlayerForm(request.POST, prefix="player")
             
            if form.is_valid():
                player = form.save()
                cron.player = player
                cron.activated = True
                cron.save()
                return render(request, 'players/registration.html', {"cron": player.cron, "study":True})
            else:
                return render(request, 'players/study.html', {"form": form, "code":code})
         
        else:
            form = PlayerForm(prefix='player')
            return render(request, 'players/study.html', {"form": form, "code":code})


def activate_nostudy(request, code):
    try:
        cron = Cron.objects.get(activationCode=code)
    except Cron.DoesNotExist:
        cron = None
    
    if cron == None:
        return render(request, 'players/registration.html', {"wrongCode": True})
    elif cron.activated:
        return render(request, 'players/registration.html', {"alreadyActivated": True})
    else:
        cron.activated = True
        cron.save()
        return render(request, 'players/registration.html', {"cron": cron}) 

