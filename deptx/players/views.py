from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader

from django.core.mail import EmailMessage
from forms import PlayerForm
from django.contrib.auth.forms import UserCreationForm
from models import Cron

from deptx.secrets import registration_passcode
from provmanager.provlogging import provlog_add_cron_register

#TODO: Move registration over to CRON
def register(request):
    if request.method == 'POST':
        player_form = PlayerForm(request.POST, prefix="player")
        user_form = UserCreationForm(request.POST, prefix = "user")
         
        passcode = request.POST.get('registration_passcode', '')
         
        if passcode == registration_passcode and player_form.is_valid() and user_form.is_valid():
            player = player_form.save()
            user = user_form.save()
            cron = Cron()
            cron.player = player
            cron.user = user
            #TODO remove after AHM
            cron.activated = True
            cron.save()
            
            provlog_add_cron_register(cron)
            
#             email_tpl = loader.get_template('players/activation.txt')
#             url = request.build_absolute_uri(reverse('players_activation', args=[cron.activationCode]))
#             c = Context({
#                 'cron': cron, 'url':url
#                 })
#             
#             email = EmailMessage(
#                 subject='[cr0n] Activate your account',
#                 body= email_tpl.render(c), 
#                 to=[cron.player.email,],
#             )
#             #in settings.py you can configure console backend for displaying emails instead of sending them - great for testing!
#             email.send(fail_silently=False)

            
             
            return render_to_response('players/registration.html', {"registered": True, "cron":cron})
        else:
            return render_to_response(   'players/registration.html',
                                        {"player_form": player_form, "user_form": user_form},
                                        context_instance=RequestContext(request)
                                        )
     
    else:
        player_form = PlayerForm(prefix='player')
        user_form = UserCreationForm(prefix='user')
        return render_to_response(  'players/registration.html',
                                    {"player_form": player_form, "user_form": user_form},
                                    context_instance=RequestContext(request)
                                )
        
        
def activate(request, code):
    try:
        cron = Cron.objects.get(activationCode=code, activated=False)
    except Cron.DoesNotExist:
        cron = None
    
    if not cron is None:
        cron.activated = True
        cron.save()
        return render_to_response('players/registration.html', {"cron": cron})
    else:
        return render_to_response('players/registration.html', {"wrongCode": True})

