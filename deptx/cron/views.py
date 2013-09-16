from django.shortcuts import render, render_to_response, redirect

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect

from players.models import Player, Cron, Mop
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template import Context, Template

from players.forms import MopForm

from assets.models import Case, Mission, Document
from cron.models import CaseInstance, CronDocumentInstance, CronTracker

from provmanager.views import getProvJson, getProvSvg, MODE_CRON

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

def logout_view(request):
    logout(request)
    return redirect('cron_index')

#@login_required(login_url='cron_login')
#@user_passes_test(isCron, login_url='cron_login')
def index(request):
    
    if request.user is not None and request.user.is_active and isCron(request.user):
        user = request.user
        cron = user.cron
        try:
            crontracker = CronTracker.objects.get(cron=request.user.cron)
        except CronTracker.DoesNotExist:
            firstMission = Mission.objects.get(rank=0)
            crontracker = CronTracker(cron=request.user.cron, progress=0, mission=firstMission)
            crontracker.save()
            
        context = { "cron": cron, "user":user, "mission":crontracker.mission }
        return render(request, 'cron/index.html', context)
    else:
        return login(request)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mopmaker(request):
    if request.method == 'POST' and 'proceed' not in request.POST:
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

            crontracker = request.user.cron.crontracker
            crontracker.progress = crontracker.progress + 1
            crontracker.save()
            return redirect('cron_mission')
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


@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission(request):
    
    crontracker = CronTracker.objects.get(cron=request.user.cron)
       
    #TODO remove magic numbers
    if request.method == 'POST':
        #progress 2 means the player needs to solve the cases and cannot progress just by pressing a button
        if (crontracker.progress == 2):
            pass
        else:
            crontracker.progress = crontracker.progress + 1
            crontracker.save()
    
    #progress 2 means we should show the list of all the cases
    if (crontracker.progress == 2):
        #do something unusual in case we are in the tutorial mission
        if (crontracker.mission.rank == 0):
            return mopmaker(request)
        
        case_list = Case.objects.filter(mission=crontracker.mission).order_by("rank")
        unfinished = False
        for case in case_list:
            try:
                caseInstance = CaseInstance.objects.get(case=case, crontracker=crontracker)
                case.solved = caseInstance.solved
                if not case.solved:
                    unfinished = True
            except CaseInstance.DoesNotExist:
                unfinished = True
        
        if unfinished:
            return render_to_response('cron/case_list.html', {"user": request.user, "mission": crontracker.mission, "case_list": case_list},
                                        context_instance=RequestContext(request)
                                )
        else:
            crontracker.progress = 3
            crontracker.save()
            return redirect('cron_mission')
        
    elif (crontracker.progress == 5):
        finishMission(crontracker)
        return redirect('cron_index')
    else:
        if crontracker.progress == 0:
            content = crontracker.mission.intro
        elif crontracker.progress == 1:
            content = crontracker.mission.briefing
        elif crontracker.progress == 3:
            content = crontracker.mission.debriefing
        elif crontracker.progress == 4:
            content = crontracker.mission.outro
        
        text = renderContent(content, request.user)
                   
        return render_to_response('cron/mission.html', {"user": request.user, "mission": crontracker.mission, "text":text},
                                         context_instance=RequestContext(request)
                                 )

#TODO only if staff
def mission_reset(request):
    try:
        crontracker = CronTracker.objects.get(cron=request.user.cron)
    except CronTracker.DoesNotExist:
        crontracker = None
    
    if not crontracker is None:
        crontracker.progress = 0
        crontracker.save()
        case_list = Case.objects.filter(mission=crontracker.mission)
        for case in case_list:
            caseInstance_list = CaseInstance.objects.filter(case=case).filter(crontracker=crontracker)
            for caseInstance in caseInstance_list:
                caseInstance.solved = False
                caseInstance.save()
            document_list = Document.objects.filter(case=case)
            for document in document_list:
                cronDocumentInstance_list = CronDocumentInstance.objects.filter(document=document).filter(cron=request.user.cron)
                for cronDocumentInstance in cronDocumentInstance_list:
                    cronDocumentInstance.solved = False
                    cronDocumentInstance.save()
    
    return HttpResponseRedirect(reverse('cron_profile'))

def mission_redo(request, mission_id):
    try:
        crontracker = CronTracker.objects.get(cron=request.user.cron)
    except CronTracker.DoesNotExist:
        crontracker = None
    
    if not crontracker is None:
        mission = Mission.objects.get(id=mission_id)
        crontracker.mission = mission
        crontracker.save()
        
    return HttpResponseRedirect(reverse('cron_profile'))


def renderContent(content, user):

    name = user.cron.user.username
    
    t = Template(content)
    c = Context({"name":name})
    
    return t.render(c)

def finishMission(crontracker):
    currentMission = crontracker.mission
    newRank = currentMission.rank + 1
    newMission = Mission.objects.get(rank=newRank)
    crontracker.mission = newMission
    crontracker.progress = 0
    crontracker.save()

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
#TODO: Has user access to case?
def case(request, serial):
    case = Case.objects.get(serial=serial)
    crontracker = request.user.cron.crontracker
    caseInstance, created = CaseInstance.objects.get_or_create(case=case, crontracker=crontracker)

    
    if not (isSolved(caseInstance)):
        content = case.intro
        text = renderContent(content, request.user)
        
        requiredDocuments = getAllDocumentStates(request.user.cron, case)

        return render_to_response('cron/case_intro.html', {"user": request.user, "case": case, "document_list": requiredDocuments, "text":text },
                                        context_instance=RequestContext(request))
    else:
        content = case.outro
        text = renderContent(content, request.user)

        return render_to_response('cron/case_outro.html', {"user": request.user, "case": case, "text": text},
                                        context_instance=RequestContext(request))
    
    
def isSolved(caseInstance):
    document_list = Document.objects.filter(case=caseInstance.case)
    for document in document_list:
        try:
            documentInstance = CronDocumentInstance.objects.get(document=document, cron=caseInstance.crontracker.cron)
        except CronDocumentInstance.DoesNotExist:
            return False
        if not documentInstance.solved:
            return False
    #TODO remove caseInstance.solved from everywhere
    caseInstance.solved = True
    caseInstance.save()
    return True
    

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
#TODO: Has user access to case and document?
def provenance(request, serial):
    
    document = Document.objects.get(serial=serial)
    documentInstance = CronDocumentInstance.objects.get(document=document, cron=request.user.cron)
    
    return render_to_response('cron/provenance.html', {"user": request.user, "documentInstance": documentInstance, "mode":MODE_CRON },
                                         context_instance=RequestContext(request)
                                 )
    

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def profile(request):
    
    crontracker = CronTracker.objects.get(cron=request.user.cron)
    currentMission = crontracker.mission
    solved_mission_list = Mission.objects.filter(rank__lt=currentMission.rank).order_by("rank")
    
    mop_list = Mop.objects.filter(player=request.user.cron.player)
    return render_to_response('cron/profile.html', {"cron": request.user.cron, "player": request.user.cron.player, "currentMission":currentMission, "solved_mission_list": solved_mission_list,"mop_list":mop_list },
                                         context_instance=RequestContext(request)
                                 )


def getAllDocumentStates(cron, case):
    requiredDocuments = case.document_set.all()
    #TODO when document is put in draft, add it to CronDocumentInstance
    availableDocumentInstances = CronDocumentInstance.objects.filter(cron=cron)
            
    for required in requiredDocuments:
        required.available = False
        for available in availableDocumentInstances:
            if (required==available.document):
                required.available = True

    return requiredDocuments