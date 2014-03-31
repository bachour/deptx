from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.http import Http404

from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

from players.models import Cron, Mop
from django.contrib.auth.forms import UserCreationForm
from django.template import Context, Template, loader

from players.forms import MopForm

from assets.models import Case, Mission, CronDocument, CaseQuestion, Riddle, Operation
from cron.models import CaseInstance, CronDocumentInstance, MissionInstance, HelpMail, CaseQuestionInstance, ChatMessage, RiddleAttempt, OperationTracker
from mop.models import Mail, MopDocumentInstance
from cron.forms import HelpMailForm, ControlHelpMailForm, ChatForm, RiddleAttemptForm

from logger.models import ProvLog
from deptx.settings import MEDIA_URL, STATIC_URL
from deptx.helpers import now

from logger.models import ActionLog
from logger import logging
from copy import deepcopy
from django.core.mail import EmailMessage, send_mass_mail
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.html import escape
import time


try:
    from deptx.settings_production import DEFAULT_FROM_EMAIL
except:
    DEFAULT_FROM_EMAIL = 'admin@localhost'

try:
    from deptx.settings_production import TO_ALL
except:
    TO_ALL = ["1@localhost.com", "2@localhost.com"]

def isCron(user):
    if user:
        try:
            cron = Cron.objects.get(user=user, activated=True, cancelled=False)
            return True
        except Cron.DoesNotExist:
            pass
    return False

def custom_404_view(request):
    return render(request, 'cron/404.html')

def custom_500_view(request):
    return render(request, 'cron/500.html')

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        
        # this is used to check if the user is a cron user
        # TODO: at the moment there is no proper error message when trying to login with a non-cron account
        if not user == None:
            if user.is_active and isCron(user):
                auth.login(request, user)
                logging.log_action(ActionLog.ACTION_CRON_LOGIN, cron=request.user.cron)
                return HttpResponseRedirect(reverse('cron_index'))
            else:
                return render(request, 'cron/login.html', {'form' : form, 'wrong':True})
            
        else:
            return render(request, 'cron/login.html', {'form' : form,})
        
    else:
        form =  AuthenticationForm()
        return render(request, 'cron/login.html', {'form' : form,})

def logout_view(request):
    if not request.user == None and request.user.is_active and isCron(request.user):
        logging.log_action(ActionLog.ACTION_CRON_LOGOUT, cron=request.user.cron)
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
        
        mop_list = Mop.objects.filter(cron=request.user.cron)
        oneMopHasPassedTutorial = False
        for mop in mop_list:
            try:
                if not mop.mopTracker.isTutorial():
                    oneMopHasPassedTutorial = True
                    break
            except:
                pass

        missionInstance = getCurrentMissionInstance(request.user.cron)
        mission_url = None
        
        if missionInstance is not None:
            if missionInstance.mission.category == Mission.CATEGORY_MOPMAKER or oneMopHasPassedTutorial:
                mission_url = None
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
            else:
                missionInstance = None
        unread_count = HelpMail.objects.filter(cron=request.user.cron, isRead=False).count()
        logging.log_action(ActionLog.ACTION_CRON_VIEW_INDEX, cron=request.user.cron)         
        context = { "cron": request.user.cron, "user":request.user, "missionInstance":missionInstance, "mission_url":mission_url, "unread_count":unread_count }
        return render(request, 'cron/index.html', context)
    else:
        return login(request)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mopmaker(request, missionInstance):
    mop_list = Mop.objects.filter(cron=request.user.cron)
    if mop_list:
        return render(request, 'cron/mopmaker_exists.html', {"mop_list":mop_list, "missionInstance":missionInstance})
    
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
            logging.log_action(ActionLog.ACTION_MOP_CREATED, cron=request.user.cron, mop=mop)

            missionInstance.makeProgress()

            return redirect('cron_mission_debriefing', missionInstance.mission.serial)
        else:
            if request.user.username == user_form.data['user-username']:
                usedCronUsername = True
            else:
                usedCronUsername = False
            return render(request, 'cron/mopmaker.html', {"mop_form": mop_form, "user_form": user_form, "user": request.user, 'name':request.user.username, 'missionInstance':missionInstance, 'usedCronUsername':usedCronUsername})
    
    else:
        mop_form = MopForm(prefix="mop")
        user_form = UserCreationForm(prefix="user")
        return render(request, 'cron/mopmaker.html',{"mop_form": mop_form, "user_form": user_form, "user": request.user, 'name':request.user.username, 'missionInstance':missionInstance})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_intro(request, serial):
    needed_progress = MissionInstance.PROGRESS_0_INTRO
    
    mission, missionInstance = getMissionAndInstanceFromSerial(request.user.cron, serial)
    logging.log_action(ActionLog.ACTION_CRON_VIEW_MISSION_INTRO, cron=request.user.cron, mission=mission, missionState=missionInstance.progress)
    
    context = getMissionOutput(request.user.cron, serial, needed_progress)   
    return render(request, 'cron/mission.html', context)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_briefing(request, serial):
    needed_progress = MissionInstance.PROGRESS_1_BRIEFING
    
    mission, missionInstance = getMissionAndInstanceFromSerial(request.user.cron, serial)
    logging.log_action(ActionLog.ACTION_CRON_VIEW_MISSION_BRIEFING, cron=request.user.cron, mission=mission, missionState=missionInstance.progress)
    
    context = getMissionOutput(request.user.cron, serial, needed_progress)   
    return render(request, 'cron/mission.html', context)

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
        text = renderContent(mission.activity, request.user)
        
        logging.log_action(ActionLog.ACTION_CRON_VIEW_MISSION_CASES, cron=request.user.cron, mission=mission, missionState=missionInstance.progress)
        
    return render(request, 'cron/case_list.html', {'user':request.user, 'cron':request.user.cron, 'text':text, 'missionInstance':missionInstance, 'caseInstance_list':caseInstance_list, 'unpublished':unpublished, 'finished':finished, 'MEDIA_URL': MEDIA_URL})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_debriefing(request, serial):
    needed_progress = MissionInstance.PROGRESS_3_DEBRIEFING
    
    mission, missionInstance = getMissionAndInstanceFromSerial(request.user.cron, serial)
    logging.log_action(ActionLog.ACTION_CRON_VIEW_MISSION_DEBRIEFING, cron=request.user.cron, mission=mission, missionState=missionInstance.progress)
    
    context = getMissionOutput(request.user.cron, serial, needed_progress)   
    return render(request, 'cron/mission.html', context)

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def mission_outro(request, serial):
    needed_progress = MissionInstance.PROGRESS_4_OUTRO
    
    mission, missionInstance = getMissionAndInstanceFromSerial(request.user.cron, serial)
    logging.log_action(ActionLog.ACTION_CRON_VIEW_MISSION_OUTRO, cron=request.user.cron, mission=mission, missionState=missionInstance.progress)
    
    context = getMissionOutput(request.user.cron, serial, needed_progress)   
    return render(request, 'cron/mission.html', context)

def getMissionAndInstanceFromSerial(cron, serial):
    try:
        mission = Mission.objects.get(serial=serial)
        missionInstance = MissionInstance.objects.get(cron=cron, mission=mission)
    except:
        return None, None
    return mission, missionInstance


def getMissionOutput(cron, serial, needed_progress):
    text = None
    next_url = None
    label = "Continue"
    mission = None
    missionInstance = None
    
    mission, missionInstance = getMissionAndInstanceFromSerial(cron, serial)
    
    if not mission == None and not missionInstance == None:
        if needed_progress <= missionInstance.progress:
            if needed_progress == MissionInstance.PROGRESS_0_INTRO:
                content = mission.intro
                next_url = reverse('cron_mission_briefing', args=(serial,))
                label = "Proceed to Briefing"
            elif needed_progress == MissionInstance.PROGRESS_1_BRIEFING:
                content = mission.briefing
                next_url = reverse('cron_mission_cases', args=(serial,))
                label = "Start Mission"
            elif needed_progress == MissionInstance.PROGRESS_2_CASES:
                pass
            elif needed_progress == MissionInstance.PROGRESS_3_DEBRIEFING:
                content = mission.debriefing
                next_url = reverse('cron_mission_outro', args=(serial,))
                label = "Proceed to Aftermath"
            elif needed_progress == MissionInstance.PROGRESS_4_OUTRO:
                content = mission.outro
                next_url = reverse('cron_index')
                label = "Back to HQ"
        else:
            return None

        text = renderContent(content, cron.user)
        
        if needed_progress == missionInstance.progress:
            missionInstance.makeProgress()

    else:
        return None
    
     
    context = {'user':cron.user, 'cron':cron, 'mission':mission, 'missionInstance':missionInstance, 'text':text, 'next_url':next_url, 'label':label}        
    return context
    
@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def archive(request):
    missionInstance_list = MissionInstance.objects.filter(cron=request.user.cron).exclude(progress=MissionInstance.PROGRESS_0_INTRO).order_by('mission__rank')
    logging.log_action(ActionLog.ACTION_CRON_VIEW_ARCHIVE, cron=request.user.cron)
    return render(request, 'cron/archive.html', {"missionInstance_list": missionInstance_list})

def renderContent(content, user):
    try:
        name = user.username
    except:
        name = None
    
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
        raise Http404
    
    good_mop, mop_list = accessMopServer(request.user.cron, cronDocument, mop_list)

    output_tpl = loader.get_template('cron/hack_document_output.txt')
    c = Context({"cronDocument":cronDocument, "good_mop":good_mop, "mop_list":mop_list})
    output = output_tpl.render(c).replace("\n", "\\n")
    return render(request, 'cron/hack_document.html', {'user':request.user, "cron": request.user.cron, "cronDocument":cronDocument, "output":output})

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
                        mail.mopDocumentInstance.status = MopDocumentInstance.STATUS_HACKED
                        mail.mopDocumentInstance.save()
                        #Mail gets deleted
                        mail.state = Mail.STATE_DELETED
                        mail.save()
                        logging.log_action(ActionLog.ACTION_CRON_HACK_DOCUMENT, cron=cron, cronDocument=cronDocument, cronDocumentInstance=cronDocumentInstance, successfulHack=True, mop=mop, mail=mail, mopDocumentInstance=mail.mopDocumentInstance)
                        return mop, checked_mop_list
            logging.log_action(ActionLog.ACTION_CRON_HACK_DOCUMENT, cron=cron, cronDocument=cronDocument, successfulHack=False, mop=mop)
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
    
    logging.log_action(ActionLog.ACTION_CRON_VIEW_CASE_INTRO, cron=request.user.cron, case=case, caseSolved=caseInstance.isSolved)
    
    return render(request, 'cron/case_intro.html', {"user": request.user, "mission": mission, "case":case, "missionInstance":missionInstance, "caseInstance":caseInstance, "cronDocument_list": requiredDocuments, "text":text })

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def case_report(request, mission_serial, case_serial):
    try:
        mission = Mission.objects.get(serial=mission_serial, isPublished=True)
        case = Case.objects.get(serial=case_serial, isPublished=True)
        caseInstance = CaseInstance.objects.get(cron=request.user.cron, case=case)
    except:
        return
    
    if caseInstance.allDocumentsSolved():
        question_list = CaseQuestion.objects.filter(case=case).order_by('rank')
        for question in question_list:
            questionInstance = CaseQuestionInstance.objects.get_or_create(cron=request.user.cron, question=question)
            
        questionInstance_list = CaseQuestionInstance.objects.filter(cron=request.user.cron, question__case=case)
        
        text = renderContent(case.report, request.user)
        
        if request.method == 'POST':
            hasGuessed = True
            for questionInstance in questionInstance_list:
                if not questionInstance.correct:
                    makeLog = True
                    if questionInstance.question.questionType == CaseQuestion.TYPE_MULTIPLE_CHOICE:
                        questionInstance.answer1 = request.POST.get('%s_answer1' % questionInstance.question.id, None)
                        questionInstance.answer2 = request.POST.get('%s_answer2' % questionInstance.question.id, None)
                        if questionInstance.question.isAllCorrect(questionInstance.answer1, questionInstance.answer2):
                            questionInstance.correct = True
                            questionInstance.submitted = True
                        else:
                            questionInstance.increaseFailedAttempts()
                        questionInstance.save()
                        data = json.dumps({'correct':questionInstance.correct, 'failedAttempts':questionInstance.failedAttempts, 'answer1':questionInstance.answer1, 'answer2':questionInstance.answer2})
                    elif questionInstance.question.questionType == CaseQuestion.TYPE_OPEN:
                        questionInstance.answer1 = request.POST.get('%s_answer1' % questionInstance.question.id, None)
                        if questionInstance.question.isCorrect1(questionInstance.answer1):
                            questionInstance.correct = True
                            questionInstance.submitted = True
                        else:
                            questionInstance.increaseFailedAttempts()
                        questionInstance.save()
                        data = json.dumps({'correct':questionInstance.correct, 'failedAttempts':questionInstance.failedAttempts, 'answer1':questionInstance.answer1})
                    elif questionInstance.question.questionType == CaseQuestion.TYPE_ESSAY:
                        answerLong = request.POST.get('%s_answerLong' % questionInstance.question.id, None)
                        if not questionInstance.answerLong == answerLong:
                            questionInstance.answerLong = answerLong
                            if len(questionInstance.answerLong) > 140:
                                questionInstance.submitted = True
                                subject = "[cr0n] %s: Report Answer Submitted" % (questionInstance.cron.user.username)
                                email_tpl = loader.get_template('cron/mail/message_from_player.txt')
                                body = "%s \n\n%s" % (questionInstance.question.question, questionInstance.answerLong)
                                c = Context({'body':body})
                                email = EmailMessage(subject=subject, body=email_tpl.render(c), to=TO_ALL)
                                email.send(fail_silently=False)
                            else:
                                questionInstance.submitted = False
                                questionInstance.increaseFailedAttempts()
                            questionInstance.save()
                            data = json.dumps({'correct':questionInstance.correct, 'failedAttempts':questionInstance.failedAttempts, 'answerLong':questionInstance.answerLong})
                        else:
                            makeLog = False
                    elif questionInstance.question.questionType == CaseQuestion.TYPE_FILE:
                        try:
                            upload = request.FILES['%s_upload' % questionInstance.question.id]
                        except:
                            upload = None 
                        if not upload == None:
                            questionInstance.upload = upload
                            questionInstance.submitted = True
                            subject = "[cr0n] %s: Report Answer Submitted" % (questionInstance.cron.user.username)
                            email_tpl = loader.get_template('cron/mail/message_from_player.txt')
                            c = Context({'body':questionInstance.filename})
                            email = EmailMessage(subject=subject, body=email_tpl.render(c), to=TO_ALL)
                            email.send(fail_silently=False)
                        elif not questionInstance.filename == "":
                            questionInstance.submitted = True
                            makeLog = False
                        else:
                            questionInstance.increaseFailedAttempts()
                        questionInstance.save()
                        try:
                            filename = questionInstance.filename
                        except:
                            filename = None
                        data = json.dumps({'correct':questionInstance.correct, 'failedAttempts':questionInstance.failedAttempts, 'upload':filename})
                    if makeLog:        
                        logging.log_action(ActionLog.ACTION_CRON_REPORT_SUBMIT, cron=request.user.cron, case=case, caseSolved=caseInstance.isSolved(), caseDocumentsSolved=caseInstance.allDocumentsSolved(), caseQuestionsSolved=caseInstance.allQuestionsSolved(), questionInstance=questionInstance, questionInstanceCorrect=questionInstance.correct, data=data)
        else:
            hasGuessed = False

        logging.log_action(ActionLog.ACTION_CRON_VIEW_CASE_REPORT, cron=request.user.cron, case=case, caseSolved=caseInstance.isSolved(), caseDocumentsSolved=caseInstance.allDocumentsSolved(), caseQuestionsSolved=caseInstance.allQuestionsSolved())
        return render(request, 'cron/case_report.html', {'text':text, 'questionInstance_list':questionInstance_list, 'mission':mission, 'case':case, 'hasGuessed':hasGuessed, 'caseInstance':caseInstance})
    else:
        return
    
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
    
    if caseInstance.isSolved():
        content = case.outro
        text = renderContent(content, request.user)
        
        requiredDocuments = getAllDocumentStates(request.user.cron, case)
        
        logging.log_action(ActionLog.ACTION_CRON_VIEW_CASE_OUTRO, cron=request.user.cron, case=case)
        
        return render(request, 'cron/case_outro.html', {"user": request.user, "mission": mission, "case":case, "missionInstance":missionInstance, "caseInstance":caseInstance, "document_list": requiredDocuments, "text":text })
    else: 
        return HttpResponseRedirect(reverse('cron_case_intro', args=(mission_serial, case_serial,)))
    

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
#TODO: Has user access to case and document?
def provenance(request, mission_serial, case_serial, document_serial):
    
    mission = Mission.objects.get(serial=mission_serial)
    case = Case.objects.get(serial=case_serial)
    cronDocument = CronDocument.objects.get(serial=document_serial)
    cronDocumentInstance = CronDocumentInstance.objects.get(cronDocument=cronDocument, cron=request.user.cron)

    logging.log_action(ActionLog.ACTION_CRON_VIEW_PROVENANCE, cron=request.user.cron, cronDocumentInstance=cronDocumentInstance, cronDocumentInstanceCorrect=cronDocumentInstance.solved)
    logging.log_prov(action=ProvLog.ACTION_OPEN, cronDocumentInstance=cronDocumentInstance)
    
    return render(request, 'cron/provenance.html', {"user": request.user, 'mission':mission, 'case':case, "cronDocumentInstance": cronDocumentInstance })
    

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
#TODO: Has user access to case and document?
def no_provenance(request, mission_serial, case_serial, document_serial):
    
    mission = Mission.objects.get(serial=mission_serial)
    case = Case.objects.get(serial=case_serial)
    cronDocument = CronDocument.objects.get(serial=document_serial)
    cronDocumentInstance = CronDocumentInstance.objects.get(cronDocument=cronDocument, cron=request.user.cron)
    cronDocumentInstance.solved = True
    cronDocumentInstance.save()
    caseInstance = CaseInstance.objects.get(cron=request.user.cron, case=case)

    logging.log_action(ActionLog.ACTION_CRON_VIEW_NO_PROVENANCE, cron=request.user.cron, cronDocumentInstance=cronDocumentInstance)
    
    return render(request, 'cron/no_provenance.html', {"user": request.user, 'caseInstance': caseInstance, 'mission':mission, 'case':case, "cronDocumentInstance": cronDocumentInstance })



@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def profile(request):
    if request.user.is_staff:
        missionInstance_list = MissionInstance.objects.filter(cron=request.user.cron)
    else:
        missionInstance_list = None
    
    cronDocumentInstance_list = CronDocumentInstance.objects.filter(cron=request.user.cron).order_by('-modifiedAt')
    mop_list = Mop.objects.filter(cron=request.user.cron)
    
    logging.log_action(ActionLog.ACTION_CRON_VIEW_PROFILE, cron=request.user.cron)
    return render(request, 'cron/profile.html', {"cron": request.user.cron, 'missionInstance_list': missionInstance_list, "mop_list":mop_list, "cronDocumentInstance_list":cronDocumentInstance_list })

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def message_compose(request):

    if request.method == 'POST':
        helpMail = HelpMail(cron=request.user.cron, type=HelpMail.TYPE_FROM_PLAYER)
        form = HelpMailForm(data=request.POST, instance=helpMail)
        if form.is_valid():
            message = form.save()
            logging.log_action(ActionLog.ACTION_CRON_MESSAGE_SEND, cron=request.user.cron, message=message)
            return render(request, 'cron/message_sent.html', {})
        else:
            logging.log_action(ActionLog.ACTION_CRON_VIEW_MESSAGES_COMPOSE, cron=request.user.cron)
            return render(request, 'cron/message_compose.html', {"form": form})
            
    else:
        form = HelpMailForm()
        logging.log_action(ActionLog.ACTION_CRON_VIEW_MESSAGES_COMPOSE, cron=request.user.cron)
        return render(request, 'cron/message_compose.html', {"form": form})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def messages(request):
    message_list = HelpMail.objects.filter(cron=request.user.cron).order_by('-createdAt')
    for message in message_list:
        if not message.isRead:
            message.isRead = True
            message.save()
    logging.log_action(ActionLog.ACTION_CRON_VIEW_MESSAGES, cron=request.user.cron)
    return render(request, 'cron/messages.html', {"message_list": message_list})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def terminate(request):
    cron = request.user.cron
    cron.cancelled = True
    cron.save()
    logout(request)
    logging.log_action(ActionLog.ACTION_CRON_TERMINATE, cron=cron)
    return render(request, 'cron/termination.html', {"cron": cron, "terminated":True})

def terminate_remote(request, serial):
    cron = Cron.objects.get(activationCode=serial)
    if request.method == 'POST':
        cron.cancelled = True
        cron.save()
        try:
            logout(request)
        except:
            pass
        logging.log_action(ActionLog.ACTION_CRON_TERMINATE, cron=cron)
        return render(request, 'cron/termination.html', {"cron": cron, "terminated":True})
    else:
        return render(request, 'cron/termination.html', {"cron": cron})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def operation_cluster_mine(request):
    currentRiddle = None
    riddleAttemptForm = None
    remainingSeconds = None
    output = None
    
    
    operation, riddle_list = get_cluster_mine_basics()
    
    operationTracker, created = OperationTracker.objects.get_or_create(cron=request.user.cron, operation=operation)
    
    if operation.hasStarted:
        currentRiddle = get_current_riddle(operation, riddle_list)  
        remainingSeconds = get_seconds_til_next_hour()
        
        if request.method == 'POST':
            riddleAttempt = RiddleAttempt(riddle=currentRiddle, cron=request.user.cron)
            form = RiddleAttemptForm(data=request.POST, instance=riddleAttempt)
            currentRiddleAttempt_list = RiddleAttempt.objects.filter(cron=request.user.cron).filter(riddle=currentRiddle).filter(correct=True)
            if form.is_valid() and currentRiddleAttempt_list.count() < 1:
                riddleAttempt = form.save()
                if riddleAttempt.attempt.lower() == riddleAttempt.riddle.solution.lower():
                    riddleAttempt.correct = True
                    riddleAttempt.save()
                    correct = True
                    if riddleAttempt.riddle.solved == False:
                        riddleAttempt.riddle.solved = True
                        riddleAttempt.riddle.save()
                else:
                    correct = False
                output_tpl = loader.get_template('cron/operation_cluster_mine_submit.txt')
                c = Context({"attempt":riddleAttempt.attempt, "riddle":currentRiddle, "correct":correct, "cron":request.user.cron})
                output = output_tpl.render(c).replace("\n", "\\n")
                logging.log_action(ActionLog.ACTION_CRON_SUBMIT_OPERATION, cron=request.user.cron, operation=operation, riddleAttempt=riddleAttempt)         
        
        for riddle in riddle_list:
            riddle.hasSolved = False
            riddleAttempt_list = RiddleAttempt.objects.filter(cron=request.user.cron).filter(riddle=riddle).filter(correct=True)
            if riddleAttempt_list.count() > 0:
                riddle.hasSolved = True
            
            if not riddle.solved:
                if riddle.rank < currentRiddle.rank:
                    riddle.solved = True
                    riddle.save()
                elif riddle.rank == currentRiddle.rank:
                    if remainingSeconds <= riddle.secondsForAutosolve:
                        currentRiddle.solved = True
                        riddle.solved = True
                        riddle.save()
            
        currentRiddleAttempt_list = RiddleAttempt.objects.filter(cron=request.user.cron).filter(riddle=currentRiddle).filter(correct=True)
        if currentRiddleAttempt_list.count() > 0:
                currentRiddle.hasSolved = True
        riddleAttemptForm = RiddleAttemptForm()

    logging.log_action(ActionLog.ACTION_CRON_VIEW_OPERATION, cron=request.user.cron, operation=operation)
    return render(request, 'cron/operation_cluster_mine.html', {"operationTracker":operationTracker, "output":output, "remainingSeconds":remainingSeconds, "operation":operation, "riddleAttemptForm":riddleAttemptForm, "riddle_list":riddle_list, "currentRiddle":currentRiddle})

def get_cluster_mine_basics():
    operation = Operation.objects.get(serial='cluster-mine')
    riddle_list = Riddle.objects.filter(operation=operation).order_by('rank')
    return operation, riddle_list

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def operation_cluster_mine_infiltration(request):
    firstLook = False
    operation = Operation.objects.get(serial='cluster-mine')
    
    riddleAttempt_list = RiddleAttempt.objects.filter(riddle__operation=operation, cron=request.user.cron).filter(correct=True).filter(riddle__rank=24)
    if operation.hasStopped or riddleAttempt_list.count() >= 1: 
        operationTracker, created = OperationTracker.objects.get_or_create(cron=request.user.cron, operation=operation)
        if not operationTracker.hasInfiltrated:
            firstLook = True
            operationTracker.hasInfiltrated = True
            operationTracker.save()
        output_tpl = loader.get_template('cron/operation_cluster_mine_infiltration.txt')
        c = Context({})
        output = output_tpl.render(c)#.replace("\n", "\\n")
        logging.log_action(ActionLog.ACTION_CRON_VIEW_OPERATION_INFILTRATE, cron=request.user.cron, operation=operation)
        return render(request, 'cron/operation_cluster_mine_infiltration.html', {"operation":operation, "output":output, "firstLook":firstLook})
    else:
        raise Http404

@csrf_exempt
def operation_cluster_mine_sync(request):
    data = json.dumps({'connectionError':True})
    if not request.user == None and request.user.is_active and isCron(request.user):
        if request.method == 'POST' and request.is_ajax():
            operation, riddle_list = get_cluster_mine_basics()
            currentRiddle = get_current_riddle(operation, riddle_list)
            remainingSeconds = get_seconds_til_next_hour()
            if currentRiddle.solved:
                forceReload = True
            elif remainingSeconds <= currentRiddle.secondsForAutosolve:
                currentRiddle.solved = True
                currentRiddle.save()
                forceReload = True
            else:
                forceReload = False
            data = json.dumps({'reload':forceReload})
    return HttpResponse(data, mimetype='application/json')


def get_current_riddle(operation, riddle_list):
    elapsedTime = now() - operation.startTime
    elapsedSeconds = elapsedTime.seconds
    elapsedHours = elapsedSeconds / 3600
    currentRiddle = riddle_list[elapsedHours]
    return currentRiddle

def get_seconds_til_next_hour():
    currentTime = now()
    minutes = currentTime.minute
    seconds = currentTime.second
    remainingSeconds = (60 - minutes) * 60 - seconds
    return remainingSeconds 

# @login_required(login_url='cron_login')
# @user_passes_test(isCron, login_url='cron_login')
# def operation_waterdrill(request):
#     operation = Operation.objects.get(serial='cluster-mine')
#     
#     falseAttempt = None
#     currentRiddle = get_current_riddle()
#     
#     riddle_list = Riddle.objects.all().order_by('rank')
#     for riddle in riddle_list:
#         riddleTracker, created = RiddleTracker.objects.get_or_create(riddle=riddle)
#         if created and riddleTracker.riddle.rank < currentRiddle.rank and not riddleTracker.solved:
#             riddleTracker.solved = True
#             riddleTracker.save()
#      
#     allSolved = False
#     
#     if currentRiddle is None:
# #         for riddle in riddle_list:
# #             if not riddle == currentRiddle:
# #                 if not riddle.riddleTracker.solved:
# #                     riddle.riddleTracker.solved = True
# #                     riddle.riddleTracker.save()
#         allSolved = True
#         logging.log_action(ActionLog.ACTION_CRON_VIEW_OPERATION, cron=request.user.cron, operation=operation)
#         return render(request, 'cron/operation_waterdrill.html', {"allSolved":allSolved, "oldRiddle_list": riddle_list, "riddle_list": riddle_list})
#     else:
#         oldRiddle_list = Riddle.objects.filter(rank__lt=currentRiddle.rank).order_by('-rank')
#         for riddle in oldRiddle_list:
#             if not riddle.riddleTracker.solved:
#                 riddle.riddleTracker.solved = True
#                 riddle.riddleTracker.save()
#     
# #         solvedRiddle_list = Riddle.objects.filter(riddleTracker__solved=True)
# #         if riddle_list.count() == solvedRiddle_list.count():
# #             allSolved = True
# #         else:
# #             allSolved = False        
#                 
#         
#         if request.method == 'POST':
#             riddleAttempt = RiddleAttempt(riddle=currentRiddle, cron=request.user.cron)
#             form = RiddleAttemptForm(data=request.POST, instance=riddleAttempt)
#             if form.is_valid():
#                 riddleAttempt = form.save()
#                 if riddleAttempt.attempt == riddleAttempt.riddle.solution:
#                     riddleAttempt.correct = True
#                     riddleAttempt.save()
#                     riddleTracker = riddleAttempt.riddle.riddleTracker
#                     if riddleTracker.solved == False:
#                         riddleTracker.solved = True
#                         riddleTracker.save()
#                 else:
#                     falseAttempt = riddleAttempt.attempt
#                 logging.log_action(ActionLog.ACTION_CRON_HACK_OPERATION, cron=request.user.cron, operation=operation, riddleAttempt=riddleAttempt)
#         
#         correctRiddleAttempts = RiddleAttempt.objects.filter(riddle=currentRiddle).filter(cron=request.user.cron).filter(correct=True).count()
#         if correctRiddleAttempts > 0:
#             hasSolved = True
#         else:
#             hasSolved = False
#         
#         riddleAttemptForm = RiddleAttemptForm()
#         minutes, seconds = remaining_time()
#         logging.log_action(ActionLog.ACTION_CRON_VIEW_OPERATION, cron=request.user.cron, operation=operation)
#         return render(request, 'cron/operation_waterdrill.html', {"minutes":minutes, "seconds":seconds, "allSolved":allSolved, "hasSolved": hasSolved, "falseAttempt":falseAttempt, "riddle_list": riddle_list, "oldRiddle_list": oldRiddle_list, "currentRiddle": currentRiddle, "riddleAttemptForm":riddleAttemptForm})

# @login_required(login_url='cron_login')
# @user_passes_test(isCron, login_url='cron_login')
# def operation_waterdrill_send(request):
#     data = False
#     print "hoho"
#     if request.method == 'POST' and request.is_ajax():
#         riddle = get_current_riddle()
#         riddleAttempt = RiddleAttempt(riddle=riddle, cron=request.user.cron)
#         form = RiddleAttemptForm(data=request.POST, instance=riddleAttempt)
#         if form.is_valid():
#             riddleAttempt = form.save()
#             if riddleAttempt.attempt == riddleAttempt.riddle.solution:
#                 riddleAttempt.correct = True
#                 riddleAttempt.save()
#                 riddleTracker = riddleAttempt.riddle.riddleTracker
#                 if riddleTracker.solved == False:
#                     riddleTracker.solved = True
#                     riddleTracker.cron = request.user.cron
#                     riddleTracker.save()
#             data = json.dumps({'correct':riddleAttempt.correct})
#             print data
#             logging.log_action(ActionLog.ACTION_CRON_HACK_WATERDRILL, cron=request.user.cron, riddleAttempt=riddleAttempt)
#     return HttpResponse(data, mimetype='application/json')

# @login_required(login_url='cron_login')
# @user_passes_test(isCron, login_url='cron_login')
# @csrf_exempt
# def operation_waterdrill_sync(request):
#     forceReload = False
#     if request.method == 'POST' and request.is_ajax():
#         riddle_id = request.POST.get('riddle', None)
#         solved = json.loads(request.POST.get('solved', False))
#         oldRiddle = Riddle.objects.get(id=riddle_id)
#         currentRiddle = get_current_riddle()
#         if currentRiddle is None:
#             forceReload = True
#         elif not oldRiddle.id == currentRiddle.id:
#             forceReload = True
#         else:
#             if not solved:
#                 if currentRiddle.riddleTracker.solved:
#                     forceReload = True
#     minutes, seconds = remaining_time()
#     if currentRiddle.riddleTracker.solved == False and (minutes * 60 + seconds) < currentRiddle.secondsForAutosolve:
#         currentRiddle.riddleTracker.solved = True
#         currentRiddle.riddleTracker.save()
#         forceReload = True
#     data = json.dumps({'reload':forceReload, 'minutes':minutes, 'seconds':seconds})
#     return HttpResponse(data, mimetype='application/json')




def remaining_time():
    minutes = 60 - int(time.strftime("%M"))
    seconds = 60 - int(time.strftime("%S"))
    return minutes, seconds

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def intelligence_report_gc8(request):
    logging.log_action(ActionLog.ACTION_CRON_VIEW_FLUFF, cron=request.user.cron, fluff='cr0n-report-gc8.html')
    return render(request, 'cron/pages/cr0n-report-gc8.html', {})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def intelligence_bunker(request):
    logging.log_action(ActionLog.ACTION_CRON_VIEW_FLUFF, cron=request.user.cron, fluff='inside-the-bunker.html')
    return render(request, 'cron/pages/inside-the-bunker.html', {})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def intelligence_mop_message(request):
    logging.log_action(ActionLog.ACTION_CRON_VIEW_FLUFF, cron=request.user.cron, fluff='mop-message.html')
    return render(request, 'cron/pages/mop-message.html', {})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def intelligence_dr_moreau(request):
    logging.log_action(ActionLog.ACTION_CRON_VIEW_FLUFF, cron=request.user.cron, fluff='dr-moreau.html')
    return render(request, 'cron/pages/dr-moreau.html', {})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def intelligence_bunker_image(request, image_name):
    image_url = STATIC_URL + 'cron/images/bunker/' + image_name
    logging.log_action(ActionLog.ACTION_CRON_VIEW_FLUFF, cron=request.user.cron, fluff=image_name)
    return render(request, 'cron/pages/bunker_image.html', {'image_url': image_url})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def intelligence_jean_baker_message(request):
    logging.log_action(ActionLog.ACTION_CRON_VIEW_FLUFF, cron=request.user.cron, fluff='jean-baker-message.html')
    return render(request, 'cron/pages/jean-baker-message.html', {})



@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def chat(request):
    chat_list = ChatMessage.objects.all()
    latest = chat_list.latest('id')
    #chat_list = ChatMessage.objects.filter(id__gt=latest.id-100)
    form = ChatForm()
    return render(request, 'cron/chat.html', {'chat_list': chat_list, 'form':form, 'latest':latest})

@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
def chat_send(request):
    data = False
    if request.method == 'POST' and request.is_ajax():
        chat = ChatMessage(cron=request.user.cron)
        form = ChatForm(data=request.POST, instance=chat)
        if form.is_valid():
            chat = form.save()
            data = json.dumps({'success':True})
    return HttpResponse(data, mimetype='application/json')
    
@login_required(login_url='cron_login')
@user_passes_test(isCron, login_url='cron_login')
@csrf_exempt
def chat_sync(request):
    data = False
    if request.method == 'POST' and request.is_ajax():
        latest_id = request.POST.get('latest_id', None)
        html = ""
        if latest_id is not None:
            chat_list = ChatMessage.objects.filter(id__gt=latest_id)
            for chat in chat_list:
                html += escape("%s: %s" % (chat.cron.user.username, chat.message)) + "<br/>"
            try:
                latest_id = chat_list.latest('id').id
            except:
                pass
        data = json.dumps({'success':True, 'html':html, 'latest_id':latest_id})
    return HttpResponse(data, mimetype='application/json')

def getAllDocumentStates(cron, case):
    requiredDocuments = case.crondocument.all()
    availableDocumentInstances = CronDocumentInstance.objects.filter(cron=cron)

                
    for required in requiredDocuments:
        required.available = False
        for available in availableDocumentInstances:
            if (required==available.cronDocument):
                required.available = True
                required.solved = available.solved
                required.getStars = available.getStars()
                required.getStarsForTemplate = available.getStarsForTemplate()
    
    requiredDocuments.allAvailable = True
    requiredDocuments.allMissing = True
    
    for required in requiredDocuments:
        if required.available:
            requiredDocuments.allMissing = False
        else:
            requiredDocuments.allAvailable = False
    
    
    return requiredDocuments


@staff_member_required
def hq(request):
    mission_list = Mission.objects.all().order_by('rank')
    case_list = Case.objects.all().order_by('rank')
    return render(request, 'cron/hq.html', {'mission_list':mission_list, 'case_list':case_list})

@staff_member_required
def hq_mission_intro(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.intro
    text = renderContent(content, request.user)
    return render(request, 'cron/mission.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_mission_briefing(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.briefing
    text = renderContent(content, request.user)
    return render(request, 'cron/mission.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_mission_debriefing(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.debriefing
    text = renderContent(content, request.user)
    return render(request, 'cron/mission.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_mission_outro(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.outro
    text = renderContent(content, request.user)
    return render(request, 'cron/mission.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_cases(request, id):
    mission = Mission.objects.get(id=id)
    content = mission.activity
    text = renderContent(content, request.user)
    return render(request, 'cron/case_list.html', {'text':text, 'mission':mission})

@staff_member_required
def hq_case_intro(request, id):
    case = Case.objects.get(id=id)
    content = case.intro
    text = renderContent(content, request.user)
    requiredDocuments = case.crondocument.all()
    return render(request, 'cron/case_intro.html', {'text':text, 'mission':case.mission, 'case':case, 'cronDocument_list':requiredDocuments, 'cheat':True})

@staff_member_required
def hq_case_report(request, id):
    case = Case.objects.get(id=id)
    question_list = CaseQuestion.objects.filter(case=case)
    text = renderContent(case.report, request.user)
    return render(request, 'cron/case_report.html', {'text':text, 'question_list':question_list, 'case':case, 'cheat':True})


@staff_member_required
def hq_case_outro(request, id):
    case = Case.objects.get(id=id)
    content = case.outro
    text = renderContent(content, request.user)
    return render(request, 'cron/case_outro.html', {'text':text, 'mission':case.mission, 'case':case })

@staff_member_required
def hq_answers(request):
    caseQuestionInstance_list = CaseQuestionInstance.objects.filter(submitted=True).exclude(question__questionType=CaseQuestion.TYPE_MULTIPLE_CHOICE).exclude(question__questionType=CaseQuestion.TYPE_OPEN).order_by('-modifiedAt')
    return render(request, 'cron/hq_answers.html', {'caseQuestionInstance_list':caseQuestionInstance_list })

@staff_member_required
def hq_mail_outstanding(request):
    helpMail_list = HelpMail.objects.filter(needsReply=True)
    return render(request, 'cron/hq_mail_outstanding.html', {'helpMail_list':helpMail_list })

@staff_member_required
def hq_mail_noreply(request, id):
    helpMail = HelpMail.objects.get(id=id)
    helpMail.needsReply = False
    helpMail.save()
    return HttpResponseRedirect(reverse('cron_hq_mail_outstanding'))

@staff_member_required
def hq_mail_reply(request, id):
    helpMail = HelpMail.objects.get(id=id)
    helpMail.needsReply = False
    helpMail.save()
    return hq_mail(request, helpMail.cron)

@staff_member_required
def hq_mail(request, cron=None):
    if request.method == 'POST':
        form = ControlHelpMailForm(request.POST)
        if form.is_valid():
            mail = form.save(commit=False)
            mail.type = HelpMail.TYPE_TO_PLAYER
            mail.isRead = False
            text = mail.body
            if 'preview' in request.POST:
                c = Context({"cron": mail.cron})    
                t = Template(text)
                mail.body = t.render(c)
                return render(request, 'cron/hq_mail.html', {'form':form, 'mail':mail})
            elif 'send' in request.POST:
                c = Context({"cron": mail.cron})    
                t = Template(text)
                mail.body = t.render(c)
                mail.save()

                to = mail.cron.email
                email_tpl = loader.get_template('cron/mail/message_to_player.txt')
                email = EmailMessage(subject='[cr0n] New Message', body = email_tpl.render(c), to=[to,])
                email.send(fail_silently=False)
                
                subject = "[cr0n] %s: Field Communication (sent to player)" % (mail.cron.user.username)
                email_tpl = loader.get_template('cron/mail/message_from_player.txt')
                c = Context({'body':mail.body})
                email = EmailMessage(subject=subject, body=email_tpl.render(c), to=TO_ALL)
                email.send(fail_silently=False)
                

                logging.log_action(ActionLog.ACTION_CRON_MESSAGE_RECEIVE, cron=mail.cron, message=mail)
                return render(request, 'cron/hq_mail.html', {'mail':mail})
            elif 'bulk' in request.POST:
                if 'spam' in request.POST:
                    email_list = []
                    cron_list = Cron.objects.exclude(cancelled=True).exclude(activated=False)
                    for cron in cron_list:
                        new_mail = deepcopy(mail)
                        new_mail.id = None
                        new_mail.cron = cron
                        c = Context({"cron": new_mail.cron})    
                        t = Template(text)
                        new_mail.body = t.render(c)
                        new_mail.save()

                        to = new_mail.cron.email
                        email_tpl = loader.get_template('cron/mail/message_to_player.txt')
                        email = ('[cr0n] New Message', email_tpl.render(c), DEFAULT_FROM_EMAIL, [to])
                        email_list.append(email) 

                        logging.log_action(ActionLog.ACTION_CRON_MESSAGE_RECEIVE, cron=cron, message=new_mail)
                    send_mass_mail(tuple(email_list), fail_silently=False)
                    
                    subject = "[cr0n] Field Communication (sent to all players)"
                    email_tpl = loader.get_template('cron/mail/message_from_player.txt')
                    c = Context({'body':mail.body})
                    email = EmailMessage(subject=subject, body=email_tpl.render(c), to=TO_ALL)
                    email.send(fail_silently=False)
                    
                    return render(request, 'cron/hq_mail.html', {'mail':mail, 'cron_list':cron_list})
                else:
                    return render(request, 'cron/hq_mail.html', {'form':form, 'mail':mail, 'nospam':True})
                
        else:
            return render(request, 'cron/hq_mail.html', {'form':form})
    else:
        form = ControlHelpMailForm(initial={'cron':cron})
    return render(request, 'cron/hq_mail.html', {'form':form})

