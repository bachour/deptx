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

from assets.models import Task, Requisition
from mop.models import TaskInstance, Mail, RequisitionInstance, RequisitionBlank
from mop.forms import MailForm, RequisitionInstanceForm


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
    requisition_list = Requisition.objects.all()
    return render(request, 'mop/rules.html', {"requisition_list": requisition_list})


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def tasks(request):

    #TODO handle the other states of the task instances as well
    active_taskInstance_list = TaskInstance.objects.filter(mop=request.user.mop, state=TaskInstance.STATE_ACTIVE)
    
    new_task_list = []
    tasks = Task.objects.all()
    
    for task in tasks:
        try:
            taskInstance = TaskInstance.objects.get(task=task, mop=request.user.mop)
        except TaskInstance.DoesNotExist:
            taskInstance = None
        
        if taskInstance is None:
            new_task_list.append(task)
       
    return render(request, 'mop/tasks.html', {"active_taskInstance_list": active_taskInstance_list, "new_task_list": new_task_list})

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
        mail = Mail(mop=request.user.mop, type=Mail.TYPE_SENT)
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
            form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop)
            return render_to_response('mop/mail_compose.html', {'form' : form,}, context_instance=RequestContext(request))
        
    else:
        form =  MailForm()
        form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop)
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
            form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop)
            return render_to_response('mop/mail_compose.html', {'form' : form,}, context_instance=RequestContext(request))
        
    else:
        form =  MailForm(instance=mail)
        #TODO same with documents at all occurences
        form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop)
        return render_to_response('mop/mail_compose.html', {'form' : form,}, context_instance=RequestContext(request))


def analyzeMail(mail):
    
    newMail = Mail()
    newMail.type = Mail.TYPE_RECEIVED
    newMail.unit = mail.unit
    newMail.mop = mail.mop
   
    #TODO Send proper error messages for all potential errors. 
    if mail.requisitionInstance is not None and mail.unit == mail.requisitionInstance.blank.requisition.unit:
        if mail.subject is Mail.SUBJECT_REQUEST_FORM and mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_FORM:
            #Check if requested requisition exists
            #TODO check more conditions (e.g. trust level)
            try:
                requisition = Requisition.objects.get(serial=mail.requisitionInstance.data)
            except Requisition.DoesNotExist:
                requisition = None
            if requisition is not None and mail.unit.isAdministrative:
                newMail.subject = Mail.SUBJECT_RECEIVE_FORM
                newMail.body = "Here is a magnificient form for you: " + requisition.serial + "."
                newMail.save()
                requisitionBlank = RequisitionBlank(requisition=requisition, mop=mail.mop)
                requisitionBlank.save()
            else:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = "We cannot help you with requesting form " + mail.requisitionInstance.data
                newMail.save()
        elif mail.subject is Mail.SUBJECT_REQUEST_TASK and mail.requisitionInstance.blank.requisition.category == Requisition.CATEGORY_TASK:
            #Check if requested task exists
            #TODO check more conditions (e.g. trust level)
            try:
                task = Task.objects.get(serial=mail.requisitionInstance.data)
            except Task.DoesNotExist:
                task = None
            if task is not None and task.unit == mail.unit:
                newMail.subject = Mail.SUBJECT_RECEIVE_TASK
                newMail.body = "You have been assigned task " + task.serial + "."
                newMail.save()
                taskInstance = TaskInstance(state=TaskInstance.STATE_ACTIVE, task=task, mop=mail.mop)
                taskInstance.save()
            else:
                newMail.subject = Mail.SUBJECT_ERROR
                newMail.body = "We cannot help you with requesting task " + mail.requisitionInstance.data
                newMail.save()
        else:
            newMail.subject = Mail.SUBJECT_ERROR
            newMail.body = "Your form is not applicable for this request."
            newMail.save()
        
    else:
        newMail.subject = Mail.SUBJECT_ERROR
        newMail.body = "Denied."
        newMail.save()
        
            
            
        

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_task(request):
    if request.method == 'POST':
        serial = request.POST['serial']
        try:
            taskInstance = TaskInstance.objects.get(serial=serial)
        except TaskInstance.DoesNotExist:
            #TODO error handling
            taskInstance = None
        if taskInstance is not None:
            req = RequisitionInstance()
            #req.type = RequisitionInstance.CATEGORY_TASK
            req.mop = request.user.mop
            req.data = serial
            req.save()
            return redirect('mop_forms')
            
    return render_to_response('mop/forms_task.html', {"mop": request.user.mop}, context_instance=RequestContext(request))

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_blank(request):
    
    # Create a blank form for all Forms that the mop user should have at start
    initialRequisitions = Requisition.objects.filter(isInitial=True)
    for initial in initialRequisitions:
        RequisitionBlank.objects.get_or_create(mop=request.user.mop, requisition=initial)
            
    blank_list = RequisitionBlank.objects.filter(mop=request.user.mop)            
    return render(request, 'mop/forms_blank.html', {"blank_list": blank_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_fill(request, reqBlank_id):
    #TODO check if user has rights to access the requisition in the first place
    try:
        reqBlank = RequisitionBlank.objects.get(id=reqBlank_id)
    except RequisitionBlank.DoesNotExist:
        reqBlank=None
        
    if request.method == 'POST':
        requisitionInstance = RequisitionInstance(blank=reqBlank)
        form = RequisitionInstanceForm(data=request.POST, instance=requisitionInstance)
        if form.is_valid():
            form.save()
            return redirect('mop_forms_signed')
    else:
        form = RequisitionInstanceForm()
        return render(request, 'mop/forms_fill.html', {"reqBlank": reqBlank, "form": form}, context_instance=RequestContext(request))

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_signed(request):
    requisitionInstance_list = RequisitionInstance.objects.filter(blank__mop=request.user.mop).order_by("-date")
    return render(request, 'mop/forms_signed.html', {"requisitionInstance_list": requisitionInstance_list})


