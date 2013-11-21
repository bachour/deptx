from django.shortcuts import render, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

from players.models import Cron, Mop
from django.contrib.auth.forms import UserCreationForm
from django.template import Context, Template, loader

from players.forms import MopForm

from assets.models import Case, Mission, CronDocument
from cron.models import CaseInstance, CronDocumentInstance, MissionInstance
from mop.models import Mail

from deptx.settings import MEDIA_URL, STATIC_URL

from logger.logging import log_cron, log_mop
from provmanager.provlogging import provlog_add_cron_login, provlog_add_cron_logout, provlog_add_mop_register


import json

def isCron(user):
    if user:
        try:
            cron = Cron.objects.get(user=user, activated=True)
            return True
        except Cron.DoesNotExist:
            pass
    return False

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        
        # this is used to check if the user is a cron user
        # TODO: at the moment there is no proper error message when trying to login with a non-cron account
        if not user == None and user.is_active and isCron(user):
            auth.login(request, user)
            log_cron(request.user.cron, 'login')
            provlog_add_cron_login(request.user.cron, request.session.session_key)
            return HttpResponseRedirect(reverse('cron_index'))
            
        else:
            return render_to_response('cron/login.html', {'form' : form,}, context_instance=RequestContext(request))
        
    else:
        form =  AuthenticationForm()
        return render_to_response('cron/login.html', {'form' : form,}, context_instance=RequestContext(request))

def logout_view(request):
    log_cron(request.user.cron, 'logout')
    provlog_add_cron_logout(request.user.cron, request.session.session_key)
    logout(request)    
    return redirect('cron_index')

def getCurrentMissionInstance(cron):
    mission_list = Mission.objects.filter(isPublished=True).order_by('rank')
    for mission in mission_list:
        missionInstance, created = MissionInstance.objects.get_or_create(cron=cron, mission=mission)
        if created:
            return missionInstance
        if not missionInstance.progress == MissionInstance.PROGRESS_5_DONE:
            return missionInstance
    return None


def index(request):
    if not request.user == None and request.user.is_active and isCron(request.user):
        user = request.user
        cron = user.cron
        
        missionInstance = getCurrentMissionInstance(request.user.cron)
        mission_url = None
        if not missionInstance == None:
            if missionInstance.progress == MissionInstance.PROGRESS_0_INTRO:
                mission_url = reverse('cron_mission_intro', args=(missionInstance.mission.serial,))
            elif missionInstance.progress == MissionInstance.PROGRESS_1_BRIEFING:
                mission_url = reverse('cron_mission_briefing', args=(missionInstance.mission.serial,))
            elif missionInstance.progress == MissionInstance.PROGRESS_2_CASES:
                mission_url = reverse('cron_mission_cases', args=(missionInstance.mission.serial,))
            elif missionInstance.progress == MissionInstance.PROGRESS_3_DEBRIEFING:
                mission_url = reverse('cron_mission_debriefing', args=(missionInstance.mission.serial,))
            elif missionInstance.progress == MissionInstance.PROGRESS_4_OUTRO:
                mission_url = reverse('cron_mission_outro', args=(missionInstance.mission.serial,))
         
        context = { "cron": cron, "user":user, "missionInstance":missionInstance, "mission_url":mission_url }
        return render(request, 'cron/index.html', context)
    else:
        return login(request)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mopmaker(request, missionInstance):
    if request.method == 'POST' and 'proceed' not in request.POST:
        mop_form = MopForm(request.POST, prefix="mop")
        user_form = UserCreationForm(request.POST, prefix="user")
        
        if mop_form.is_valid() and user_form.is_valid():
            #TODO check if all saves work and catch the error if they don't
            new_user = user_form.save()
            mop = mop_form.save(commit=False)
            mop.cron = request.user.cron
            mop.user = new_user
            mop.save()

            missionInstance.makeProgress()
            
            log_mop(mop, 'mop account created')
            provlog_add_mop_register(request.user.cron, mop, request.session.session_key)
            return redirect('cron_mission_debriefing', missionInstance.mission.serial)
        else:
            return render_to_response(   'cron/mopmaker.html',
                                        {"mop_form": mop_form, "user_form": user_form, "user": request.user, 'name':request.user.username, 'missionInstance':missionInstance},
                                        context_instance=RequestContext(request)
                                        )
    
    else:
        mop_form = MopForm(prefix="mop")
        user_form = UserCreationForm(prefix="user")
        return render_to_response(  'cron/mopmaker.html',
                                    {"mop_form": mop_form, "user_form": user_form, "user": request.user, 'name':request.user.username, 'missionInstance':missionInstance},
                                    context_instance=RequestContext(request)
                                )

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_intro(request, serial):
    needed_progress = MissionInstance.PROGRESS_0_INTRO
    context = getMissionOutput(request.user.cron, serial, needed_progress)   
    return render_to_response('cron/mission.html', context)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_briefing(request, serial):
    needed_progress = MissionInstance.PROGRESS_1_BRIEFING
    context = getMissionOutput(request.user.cron, serial, needed_progress)   
    return render_to_response('cron/mission.html', context)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_cases(request, serial):
    text = None
    mission = None
    missionInstance = None
    try:
        mission = Mission.objects.get(serial=serial)
        missionInstance = MissionInstance.objects.get(cron=request.user.cron, mission=mission)
    except:
        return
    
    if missionInstance.isCasesAllowed:
        if mission.category == Mission.CATEGORY_MOPMAKER:
            return mopmaker(request, missionInstance)
        
        case_list = Case.objects.filter(mission=mission).order_by('rank')
        caseInstance_list = []
        finished = True
        unpublished = False
        for case in case_list:
            if case.isPublished:
                try:
                    preCase = Case.objects.get(preCase=case)
                    preCaseInstance, created = CaseInstance.objects.get_or_create(cron=request.user.cron, case=preCase)
                    preCaseCondition = preCaseInstance.isSolved()
                except Case.DoesNotExist:
                    preCase = None
                    preCaseInstance = None
                    preCaseCondition = True
                if preCaseCondition:
                    caseInstance, created = CaseInstance.objects.get_or_create(cron=request.user.cron, case=case)
                    if not caseInstance.isSolved():
                        finished = False
                    caseInstance_list.append(caseInstance)        
            else:
                unpublished = True
        if (finished and not unpublished):
            missionInstance.makeProgress()
        text = renderContent(mission.activity, request.user.cron)
    return render_to_response('cron/case_list.html', {'user':request.user, 'cron':request.user.cron, 'text':text, 'missionInstance':missionInstance, 'caseInstance_list':caseInstance_list, 'unpublished':unpublished, 'finished':finished, 'MEDIA_URL': MEDIA_URL})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_debriefing(request, serial):
    needed_progress = MissionInstance.PROGRESS_3_DEBRIEFING
    context = getMissionOutput(request.user.cron, serial, needed_progress)   
    return render_to_response('cron/mission.html', context)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_outro(request, serial):
    needed_progress = MissionInstance.PROGRESS_4_OUTRO
    context = getMissionOutput(request.user.cron, serial, needed_progress)   
    return render_to_response('cron/mission.html', context)

def getMissionOutput(cron, serial, needed_progress):
    text = None
    next_url = None
    mission = None
    missionInstance = None
    
    try:
        mission = Mission.objects.get(serial=serial)
        missionInstance = MissionInstance.objects.get(cron=cron, mission=mission)
    except:
        pass
    
    if not mission == None and not missionInstance == None:
        if needed_progress <= missionInstance.progress:
            if needed_progress == MissionInstance.PROGRESS_0_INTRO:
                content = mission.intro
                next_url = reverse('cron_mission_briefing', args=(serial,))
            elif needed_progress == MissionInstance.PROGRESS_1_BRIEFING:
                content = mission.briefing
                next_url = reverse('cron_mission_cases', args=(serial,))
            elif needed_progress == MissionInstance.PROGRESS_2_CASES:
                pass
            elif needed_progress == MissionInstance.PROGRESS_3_DEBRIEFING:
                content = mission.debriefing
                next_url = reverse('cron_mission_outro', args=(serial,))
            elif needed_progress == MissionInstance.PROGRESS_4_OUTRO:
                content = mission.outro
                next_url = reverse('cron_index')

        text = renderContent(content, cron)
        
        if needed_progress == missionInstance.progress:
            missionInstance.makeProgress()

    else:
        text = None
    
     
    context = {'user':cron.user, 'cron':cron, 'mission':mission, 'missionInstance':missionInstance, 'text':text, 'next_url':next_url}        
    return context
    
@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def archive(request):
    #TODO: Sort by mission.rank
    missionInstance_list = MissionInstance.objects.filter(cron=request.user.cron)
    return render_to_response('cron/archive.html', {'user':request.user, "cron": request.user.cron, "missionInstance_list": missionInstance_list})

def renderContent(content, cron):
    try:
        name = cron.user.username
    except:
        name = 'ANONYMOUS_AGENT'
    
    t = Template(content)
    c = Context({"name":name, "MEDIA_URL":MEDIA_URL})
    
    return t.render(c)

@staff_member_required
def missionInstance_reset(request, serial):
    mission = None
    missionInstance = None
    try:
        mission = Mission.objects.get(serial=serial)
        missionInstance = MissionInstance.objects.get(cron=request.user.cron, mission=mission)
    except:
        pass
    
    if not missionInstance == None:
        missionInstance.progress = MissionInstance.PROGRESS_0_INTRO
        missionInstance.save()
        unsolveDocuments(request.user.cron, mission)
    return HttpResponseRedirect(reverse('cron_profile'))

@staff_member_required
def missionInstance_delete(request, serial):
    try:
        mission = Mission.objects.get(serial=serial)
        unsolveDocuments(request.user.cron, mission)
        missionInstance = MissionInstance.objects.get(cron=request.user.cron, mission=mission)
        missionInstance.delete()
    except:
        pass
    
    return HttpResponseRedirect(reverse('cron_profile'))
        

def unsolveDocuments(cron, mission):
    case_list = Case.objects.filter(mission=mission)
    for case in case_list:
        cronDocument_list = CronDocument.objects.filter(case=case)
        for cronDocument in cronDocument_list:
            cronDocumentInstance_list = CronDocumentInstance.objects.filter(cronDocument=cronDocument).filter(cron=cron)
            for cronDocumentInstance in cronDocumentInstance_list:
                cronDocumentInstance.solved = False
                cronDocumentInstance.save()

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def hack_document(request, serial):
    mop_list = Mop.objects.filter(cron=request.user.cron).filter(active=True)
    try:
        cronDocument = CronDocument.objects.get(serial=serial)    
    except CronDocument.DoesNotExist:
        return
    
    good_mop, mop_list = accessMopServer(request.user.cron, cronDocument, mop_list)

    output_tpl = loader.get_template('cron/hack_document_output.txt')
    c = Context({"cronDocument":cronDocument, "good_mop":good_mop, "mop_list":mop_list})
    output = output_tpl.render(c).replace("\n", "\\n")
    return render_to_response('cron/hack_document.html', {'user':request.user, "cron": request.user.cron, "cronDocument":cronDocument, "output":output})

def accessMopServer(cron, cronDocument, mop_list):
        checked_mop_list = []
        for mop in mop_list:
            mail_list = Mail.objects.filter(type=Mail.TYPE_DRAFT).filter(mop=mop).filter(state=Mail.STATE_NORMAL)
            checked_mop_list.append(mop)
            for mail in mail_list:
                if not mail.mopDocumentInstance == None:
                    if mail.mopDocumentInstance.cronDocument == cronDocument:
                        cronDocumentInstance, created = CronDocumentInstance.objects.get_or_create(cron=cron, cronDocument=cronDocument)
                        #Document gets removed
                        mail.mopDocumentInstance.used = True
                        mail.mopDocumentInstance.save()
                        #Mail gets deleted
                        mail.state = Mail.STATE_DELETED
                        mail.save()
                        return mop, checked_mop_list
                        
        return None, checked_mop_list

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def case_intro(request, mission_serial, case_serial):
    try:
        mission = Mission.objects.get(serial=mission_serial, isPublished=True)
        case = Case.objects.get(serial=case_serial, isPublished=True)
        missionInstance = MissionInstance.objects.get(cron=request.user.cron, mission=mission)
        caseInstance = CaseInstance.objects.get(cron=request.user.cron, case=case)
    except:
        return

    content = case.intro
    text = renderContent(content, request.user)
    
    requiredDocuments = getAllDocumentStates(request.user.cron, case)

    return render_to_response('cron/case_intro.html', {"user": request.user, "mission": mission, "case":case, "missionInstance":missionInstance, "caseInstance":caseInstance, "cronDocument_list": requiredDocuments, "text":text },
                                    context_instance=RequestContext(request))
    
@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')    
def case_outro(request, mission_serial, case_serial):        
    try:
        mission = Mission.objects.get(serial=mission_serial, isPublished=True)
        case = Case.objects.get(serial=case_serial, isPublished=True)
        missionInstance = MissionInstance.objects.get(cron=request.user.cron, mission=mission)
        caseInstance = CaseInstance.objects.get(cron=request.user.cron, case=case)
    except:
        return

    content = case.outro
    text = renderContent(content, request.user)
    
    requiredDocuments = getAllDocumentStates(request.user.cron, case)

    return render_to_response('cron/case_outro.html', {"user": request.user, "mission": mission, "case":case, "missionInstance":missionInstance, "caseInstance":caseInstance, "document_list": requiredDocuments, "text":text },
                                    context_instance=RequestContext(request))
    

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
#TODO: Has user access to case and document?
def provenance(request, mission_serial, case_serial, document_serial):
    
    mission = Mission.objects.get(serial=mission_serial)
    case = Case.objects.get(serial=case_serial)
    cronDocument = CronDocument.objects.get(serial=document_serial)
    cronDocumentInstance = CronDocumentInstance.objects.get(cronDocument=cronDocument, cron=request.user.cron)
    
    doc ={}
    doc['id'] = cronDocument.id
    doc['serial'] = cronDocument.serial
    doc['store_id'] = cronDocument.provenance.store_id    
    log_cron(request.user.cron, 'view provenance', json.dumps(doc))
    
    return render_to_response('cron/provenance.html', {"user": request.user, 'mission':mission, 'case':case, "cronDocumentInstance": cronDocumentInstance },
                                         context_instance=RequestContext(request)
                                 )
    

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def profile(request):
    if request.user.is_staff:
        missionInstance_list = MissionInstance.objects.filter(cron=request.user.cron)
    else:
        missionInstance_list = None
    
    cronDocumentInstance_list = CronDocumentInstance.objects.filter(cron=request.user.cron).order_by('-modifiedAt')
    mop_list = Mop.objects.filter(cron=request.user.cron)

    return render_to_response('cron/profile.html', {"cron": request.user.cron, 'missionInstance_list': missionInstance_list, "mop_list":mop_list, "cronDocumentInstance_list":cronDocumentInstance_list })

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def bunker_image(request, image_name):
    image_url = STATIC_URL + 'cron/images/bunker/' + image_name
    return render_to_response('cron/pages/bunker_image.html', {'image_url': image_url})



def getAllDocumentStates(cron, case):
    requiredDocuments = case.crondocument_set.all()
    availableDocumentInstances = CronDocumentInstance.objects.filter(cron=cron)
            
    for required in requiredDocuments:
        required.available = False
        for available in availableDocumentInstances:
            if (required==available.cronDocument):
                required.available = True
                required.solved = available.solved
                required.getStars = available.getStars()
                required.getStarsForTemplate = available.getStarsForTemplate()

    return requiredDocuments


@staff_member_required
def hq(request):
    mission_list = Mission.objects.all().order_by('rank')
    case_list = Case.objects.all().order_by('rank')
    
    return render_to_response('cron/hq.html', {'mission_list':mission_list, 'case_list':case_list})

@staff_member_required
def hq_mission_intro(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.intro
    text = renderContent(content, request.user)
    return render_to_response('cron/mission.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_mission_briefing(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.briefing
    text = renderContent(content, request.user)
    return render_to_response('cron/mission.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_mission_debriefing(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.debriefing
    text = renderContent(content, request.user)
    return render_to_response('cron/mission.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_mission_outro(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.outro
    text = renderContent(content, request.user)
    return render_to_response('cron/mission.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_cases(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.activity
    text = renderContent(content, request.user)
    return render_to_response('cron/case_list.html', {'text':text, 'mission':mission})


@staff_member_required
def hq_case_intro(request, id):
    case = Case.objects.get(id=id)
    content = case.intro
    text = renderContent(content, request.user)
    requiredDocuments = case.crondocument_set.all()
    return render_to_response('cron/case_intro.html', {'text':text, 'mission':case.mission, 'case':case, 'cronDocument_list':requiredDocuments, 'cheat':True})

@staff_member_required
def hq_case_outro(request, id):
    case = Case.objects.get(id=id)
    content = case.outro
    text = renderContent(content, request.user)
    return render_to_response('cron/case_outro.html', {'text':text, 'mission':case.mission, 'case':case })