from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext

from forms import PlayerForm
from django.contrib.auth.forms import UserCreationForm
from models import Cron


def register(request):
    if request.method == 'POST':
        player_form = PlayerForm(request.POST, prefix="player")
        user_form = UserCreationForm(request.POST, prefix = "user")
        
        print player_form
        print user_form
        
        if player_form.is_valid() and user_form.is_valid():
            player = player_form.save()
            user = user_form.save()
            cron = Cron()
            cron.player = player
            cron.user = user
            cron.save()
            return render_to_response('players/registration.html', {"success": True})
        else:
            return render_to_response(   'players/registration.html',
                                        {"success": False, "player_form": player_form, "user_form": user_form},
                                        context_instance=RequestContext(request)
                                        )
    
    else:
        player_form = PlayerForm(prefix='player')
        user_form = UserCreationForm(prefix='user')
        return render_to_response(  'players/registration.html',
                                    {"player_form": player_form, "user_form": user_form},
                                    context_instance=RequestContext(request)
                                )