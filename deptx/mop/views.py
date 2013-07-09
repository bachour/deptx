from django.shortcuts import render, render_to_response, redirect

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect

from players.models import Player, Mop
from django.contrib.auth.models import User

from models import Task, TaskState, Document, Mail, Requisition
from forms import MailForm

def isMop(user):
    if user:
        for mop in Mop.objects.filter(user=user):
            if mop.active:
                return True
    return False

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def index(request):
    activeMops = Mop.objects.filter(active=True)
    inactiveMops = Mop.objects.filter(active=False)
    
    #MAIL MANAGING
    inbox_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
    outbox_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_SENT).filter(read=False).count()
    trash_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_TRASHED).filter(read=False).count()
    draft_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_DRAFT).filter(read=False).count()
    
    context = {'activeMops': activeMops, 'inactiveMops': inactiveMops, 'user': request.user, 'inbox_unread': inbox_unread, 'outbox_unread': outbox_unread, 'trash_unread': trash_unread, 'draft_unread': draft_unread}
    return render(request, 'mop/index.html', context)

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        
        # this is used to check if the user is a cron user or a mop user
        # (also in if-clause
        # TODO: at the moment there is no proper error message when trying to login with a non-cron account
        # TODO: Code is almost identical to CRON-code
        if user is not None and user.is_active and isMop(user):
            auth.login(request, user)
            return HttpResponseRedirect(reverse('mop_index'))
            
        else:
            return render_to_response('mop/login.html', {'form' : form,}, context_instance=RequestContext(request))
        
    else:
        form =  AuthenticationForm()
        return render_to_response('mop/login.html', {'form' : form,}, context_instance=RequestContext(request))

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def rules(request):
    return render(request, 'mop/rules.html')

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def tasks(request):
    taskState_accessible_list = TaskState.objects.filter(mop=request.user.mop).filter(state=TaskState.STATE_ACCESSIBLE)
    taskState_active_list = TaskState.objects.filter(mop=request.user.mop).filter(state=TaskState.STATE_ACTIVE)
    return render(request, 'mop/tasks.html', {"taskState_accessible_list": taskState_accessible_list, "taskState_active_list": taskState_active_list})
# def tasks(request):
#     if request.method == 'POST':
#         task_id = request.POST.get('task')
#         task = Task.objects.get(id=task_id)
#         mop = request.user.mop
#         taskStatus = TaskStatus()
#         taskStatus.task = task
#         taskStatus.mop = mop
#         taskStatus.status = TaskStatus.STATUS_CURRENT
#         taskStatus.save()
#         return render(request, 'mop/tasks_current.html', {"task": task })
#     
#     else:
#         try:
#             taskStatus = TaskStatus.objects.get(mop=request.user.mop, status=TaskStatus.STATUS_CURRENT)
#         except TaskStatus.DoesNotExist:
#             taskStatus = None
#         if (taskStatus is not None):
#             task = taskStatus.task
#             return render(request, 'mop/tasks_current.html', {"task": task })
#         else:
#             #TODO should the generic tasks be filtered by trust level?
#             generic_task_list = Task.objects.filter(episode=-1).filter(trust__lte=request.user.mop.trust)
#             #TODO should the episode specific tasks be filtered by trust level?
#             episode_task_list = Task.objects.filter(episode=request.user.mop.player.cron.episode)
#             task_list = generic_task_list | episode_task_list
#             return render(request, 'mop/tasks.html', {"task_list": task_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def documents(request):
    return render(request, 'mop/documents.html')

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_inbox(request):
    mail_list = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).order_by('-date')
    return render(request, 'mop/mail_inbox.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_outbox(request):
    mail_list = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_SENT).order_by('-date')
    return render(request, 'mop/mail_outbox.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_draft(request):
    mail_list = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_DRAFT).order_by('-date')
    return render(request, 'mop/mail_draft.html', {"mail_list": mail_list})


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_trash(request):
    mail_list = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_TRASHED).order_by('-date')
    return render(request, 'mop/mail_trash.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_view(request, mail_id):
    try:
        mail = Mail.objects.get(id=mail_id, mop=request.user.mop)
        mail.read = True
        mail.save()
    except Mail.DoesNotExist:
        mail = None
    return render(request, 'mop/mail_view.html', {'mail': mail})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_trashing(request, mail_id):
    try:
        mail = Mail.objects.get(id=mail_id, mop=request.user.mop, state=Mail.STATE_NORMAL)
    except Mail.DoesNotExist:
        #TODO Error handling
        return redirect('mop_index')
    mail.read = True
    mail.state = Mail.STATE_TRASHED
    mail.save()
    if mail.type is Mail.TYPE_RECEIVED:
        return redirect('mop_mail_inbox')
    elif mail.type is Mail.TYPE_SENT:
        return redirect('mop_mail_outbox')
    elif mail.type is Mail.TYPE_DRAFT:
        return redirect('mop_mail_draft')
    

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_untrashing(request, mail_id):
    try:
        mail = Mail.objects.get(id=mail_id, mop=request.user.mop, state=Mail.STATE_TRASHED)
    except Mail.DoesNotExist:
        return redirect('mop_index')
    mail.read = True
    mail.state = Mail.STATE_NORMAL
    mail.save()
    return redirect('mop_mail_trash')

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_deleting(request, mail_id):
    try:
        mail = Mail.objects.get(id=mail_id, mop=request.user.mop, state=Mail.STATE_TRASHED)
    except Mail.DoesNotExist:
        #TODO Error handling
        return redirect('mop_index')
    mail.read = True
    mail.state = Mail.STATE_DELETED
    mail.save()
    return redirect('mop_mail_trash')

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_compose(request):
    if request.method == 'POST':
        mail = Mail(mop=request.user.mop, type=Mail.TYPE_SENT, read=True)
        if 'send' in request.POST:
            mail.type = Mail.TYPE_SENT
        elif 'draft' in request.POST:
            mail.type = Mail.TYPE_DRAFT
        form = MailForm(data=request.POST, instance=mail)
        
        if form.is_valid():
            mail = form.save()
            analyzeMail(mail)
            return redirect('mop_mail_outbox')
        else:
            form.fields["requisition"].queryset = Requisition.objects.filter(mop=request.user.mop)
            return render_to_response('mop/mail_compose.html', {'form' : form,}, context_instance=RequestContext(request))
        
    else:
        form =  MailForm()
        form.fields["requisition"].queryset = Requisition.objects.filter(mop=request.user.mop)
        return render_to_response('mop/mail_compose.html', {'form' : form,}, context_instance=RequestContext(request))
    
@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_edit(request, mail_id):
    try:
        mail = Mail.objects.get(id=mail_id)
    except mail.DoesNotExist:
        #TODO error handling
        return redirect('mop_mail_index')
    
    if request.method == 'POST':
        if 'send' in request.POST:
            mail.type = Mail.TYPE_SENT
        elif 'draft' in request.POST:
            mail.type = Mail.TYPE_DRAFT
        form = MailForm(data=request.POST, instance=mail)
        
        if form.is_valid():
            mail = form.save()
            analyzeMail(mail)
            return redirect('mop_mail_outbox')
        else:
            form.fields["requisition"].queryset = Requisition.objects.filter(mop=request.user.mop)
            return render_to_response('mop/mail_compose.html', {'form' : form,}, context_instance=RequestContext(request))
        
    else:
        form =  MailForm(instance=mail)
        #TODO same with documents at all occurences
        form.fields["requisition"].queryset = Requisition.objects.filter(mop=request.user.mop)
        return render_to_response('mop/mail_compose.html', {'form' : form,}, context_instance=RequestContext(request))

def analyzeMail(mail):
    
    newMail = Mail()
    newMail.type = Mail.TYPE_RECEIVED
    newMail.unit = mail.unit
    newMail.mop = mail.mop
    
    #Check if task was requested properly
    if mail.subject is Mail.SUBJECT_SEND_FORM and mail.unit is Mail.UNIT_ADMINISTRATION and mail.requisition is not None:
        try:
            taskState = TaskState.objects.get(serial=mail.requisition.data, mop=mail.mop)
        except TaskState.DoesNotExist:
            taskState = None
        #TODO set requisition to used
        if taskState is not None:
            #TODO also check for trust level
            newMail.subject = Mail.SUBJECT_ASSIGNED_TASK
            newMail.body = "You have been assigned task " + taskState.serial + "."
            newMail.save()
            taskState.state = TaskState.STATE_ACTIVE
            taskState.save()
        else:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = "There was an error in your form."
            newMail.save()
    else:
        newMail.subject = Mail.SUBJECT_ERROR
        newMail.body = "Please rewrite your message."
        newMail.save()
        
            
            
        

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_task(request):
    if request.method == 'POST':
        serial = request.POST['serial']
        try:
            taskState = TaskState.objects.get(serial=serial)
        except TaskState.DoesNotExist:
            #TODO error handling
            taskState = None
        if taskState is not None:
            req = Requisition()
            req.type = Requisition.TYPE_TASK
            req.mop = request.user.mop
            req.data = serial
            req.save()
            return redirect('mop_forms')
            
    return render_to_response('mop/forms_task.html', {"mop": request.user.mop}, context_instance=RequestContext(request))

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms(request):
    req_list = Requisition.objects.filter(mop=request.user.mop).order_by('-date')
    return render(request, 'mop/forms.html', {"req_list": req_list})