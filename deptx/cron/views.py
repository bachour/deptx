from django.shortcuts import render, render_to_response

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect

from players.models import Player, Cron, Mop
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from players.forms import MopForm


def isCron(user):
    if user:
        return Cron.objects.filter(user=user).exists()
    return False

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        
        # this is used to check if the user is a cron user
        # TODO: at the moment there is no proper error message when trying to login with a non-cron account
        if user is not None and user.is_active and isCron(user):
            auth.login(request, user)
            return HttpResponseRedirect(reverse('cron_index'))
            
        else:
            return render_to_response('cron/login.html', {'form' : form,}, context_instance=RequestContext(request))
        
    else:
        form =  AuthenticationForm()
        return render_to_response('cron/login.html', {'form' : form,}, context_instance=RequestContext(request))

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def index(request):
    user = request.user
    cron = user.cron
    context = { "cron": cron, "user":user }
    
    
    
    if (cron.episode==0 and cron.progress==0):
        return render(request, 'cron/episode0.html', context)
    elif (cron.episode==0 and cron.progress==1):
        return render(request, 'cron/index.html', context)
    else:
        return render(request, 'cron/index.html', context)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mopmaker(request):
    if request.method == 'POST':
        mop_form = MopForm(request.POST, prefix="mop")
        user_form = UserCreationForm(request.POST, prefix="user")
        
        if mop_form.is_valid() and user_form.is_valid():
            #TODO check if all saves work and catch the error if they don't
            new_user = user_form.save()
            player = request.user.cron.player
            mop = mop_form.save(commit=False)
            mop.player = player
            mop.user = new_user
            mop.save()
            
            cron = request.user.cron
            cron.progress = 1
            cron.save()
            return render_to_response('cron/mopmaker_created.html', {"user": request.user})
        else:
            return render_to_response(   'cron/mopmaker.html',
                                        {"mop_form": mop_form, "user_form": user_form, "user": request.user},
                                        context_instance=RequestContext(request)
                                        )
    
    else:
        mop_form = MopForm(prefix="mop")
        user_form = UserCreationForm(prefix="user")
        return render_to_response(  'cron/mopmaker.html',
                                    {"mop_form": mop_form, "user_form": user_form, "user": request.user},
                                    context_instance=RequestContext(request)
                                )
