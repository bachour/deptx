from django.shortcuts import render, redirect

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm


from players.models import Mop

from assets.models import Requisition, Unit, CronDocument
from mop.models import Mail, RequisitionInstance, RequisitionBlank, MopDocumentInstance, RandomizedDocument, MopTracker, TrustInstance
from mop.forms import MailForm, RequisitionInstanceForm

from provmanager.provlogging import provlog_add_mop_login, provlog_add_mop_logout, provlog_add_mop_sign_form, provlog_add_mop_send_form, provlog_add_mop_issue_form, provlog_add_mop_issue_document

from logger.logging import log_cron, log_mop
import json

from mop.mailserver import analyze_mail
from mop.performer import analyze_performance
from mop.documentcreator import create_documents
from django.views.decorators.csrf import csrf_exempt

import tutorial

def isMop(user):
    if user:
        for mop in Mop.objects.filter(user=user):
            if mop.active:
                return True
    return False

#@login_required(login_url='mop_login')
#@user_passes_test(isMop, login_url='mop_login')
def index(request):

    if not request.user == None and request.user.is_active and isMop(request.user):

        mopTracker, created = MopTracker.objects.get_or_create(mop=request.user.mop)
        
        hide = tutorial.hide(mopTracker, created)
  
        #MAIL MANAGING
        inbox_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
        outbox_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_SENT).filter(read=False).count()
        trash_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_TRASHED).filter(read=False).count()
        draft_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_DRAFT).filter(read=False).count()
        
        request.session['inbox_unread'] = inbox_unread
        
        log_mop(request.user.mop, 'index')
        context = {'user': request.user, 'inbox_unread': inbox_unread, 'outbox_unread': outbox_unread, 'trash_unread': trash_unread, 'draft_unread': draft_unread, 'hide':hide}

        return render(request, 'mop/index.html', context)
    
    else:
        return login(request)

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
        if not user == None and user.is_active and isMop(user):
            auth.login(request, user)
            log_mop(request.user.mop, 'login')
            provlog_add_mop_login(request.user.mop, request.session.session_key)
            
            request.session['has_checked_inbox'] = False
            return HttpResponseRedirect(reverse('mop_index'))
            
        else:
            return render(request, 'mop/login.html', {'form' : form})
        
    else:
        form =  AuthenticationForm()
        return render(request, 'mop/login.html', {'form' : form})

def logout_view(request):
    log_mop(request.user.mop, 'logout')
    provlog_add_mop_logout(request.user.mop, request.session.session_key)
    logout(request)
    return redirect('mop_index')

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def rules(request):
    unit_list = Unit.objects.all().order_by('serial')
    requisition_list = Requisition.objects.all().order_by('serial')
    log_mop(request.user.mop, 'read rules')
    return render(request, 'mop/rules.html', {"unit_list":unit_list, "requisition_list": requisition_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def performance(request):
#     badge_list = Badge.objects.filter(mop=request.user.mop).order_by('-modifiedAt')
    
#     taskInstance_list = TaskInstance.objects.filter(mop=request.user.mop).exclude(status=TaskInstance.STATUS_ACTIVE).order_by('modifiedAt')
#     print taskInstance_list
#     
#     #creationDate = request.user.mop.created
#     creationDate = request.user.mop.created - timedelta(weeks=-3)
#     today = now()
#     print creationDate
#     print today
#     nextMonday = timedelta(days=-today.weekday(), weeks=1)
#     lastMonday = today - timedelta(days=today.weekday())
#     print nextMonday
#     print lastMonday
#     weekTrust_list = WeekTrust.objects.filter(mop=request.user.mop).order_by('-year', '-week')

    trustInstance_list = TrustInstance.objects.filter(mop=request.user.mop).order_by('-createdAt')
    log_mop(request.user.mop, 'read performance')
    return render(request, 'mop/performance.html', {'trustInstance_list':trustInstance_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def documents_pool(request):

    randomizedDocument_list = tutorial.getTutorialDocument(request.user.mop.mopTracker)
    if randomizedDocument_list == None:
        randomizedDocument_list = RandomizedDocument.objects.filter(active=True).filter(mopDocument__clearance__lte=request.user.mop.mopTracker.clearance)

    mopDocumentInstance_list = MopDocumentInstance.objects.filter(mop=request.user.mop)
    
        
    for randomizedDocument in randomizedDocument_list:
        for mopDocumentInstance in mopDocumentInstance_list:
            if mopDocumentInstance.randomizedDocument == randomizedDocument:
                randomizedDocument.exists = True
                break
        
 
    log_mop(request.user.mop, 'view pool')   
    return render(request, 'mop/documents_pool.html', {"randomizedDocument_list": randomizedDocument_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def documents(request):
    mopDocumentInstance_list = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE)
    
    log_mop(request.user.mop, 'view documents')
    return render(request, 'mop/documents.html', {"mopDocumentInstance_list": mopDocumentInstance_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def documents_archive(request):
    mopDocumentInstance_list = MopDocumentInstance.objects.filter(mop=request.user.mop).exclude(status=MopDocumentInstance.STATUS_ACTIVE).exclude(status=MopDocumentInstance.STATUS_HACKED)
    
    log_mop(request.user.mop, 'view documents archive')
    return render(request, 'mop/documents_archive.html', {"mopDocumentInstance_list": mopDocumentInstance_list})


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def provenance(request, serial):
    try:
        document = RandomizedDocument.objects.get(serial=serial)
        clearance = document.mopDocument.clearance
        documentInstance = MopDocumentInstance.objects.get(mop=request.user.mop, randomizedDocument=document)
    except RandomizedDocument.DoesNotExist:
        document = None
        documentInstance = None
    except MopDocumentInstance.DoesNotExist:
        documentInstance = None
    
    if document is None:
        try:
            document = CronDocument.objects.get(serial=serial)
            clearance = document.clearance
            documentInstance = MopDocumentInstance.objects.get(mop=request.user.mop, cronDocument=document)
        except CronDocument.DoesNotExist:
            document = None
            documentInstance = None
        except MopDocumentInstance.DoesNotExist:
            documentInstance = None
    
    if documentInstance is None:
        return None
    elif clearance <= request.user.mop.mopTracker.clearance:
        if documentInstance.status == MopDocumentInstance.STATUS_ACTIVE:
            inactive = False
        else:
            inactive = True
        return render(request, 'mop/provenance.html', {'document': document, "inactive":inactive})
    else:
        return render(request, 'mop/provenance_noclearance.html', {'document': document})


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_inbox(request):
    mail_list = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).order_by('-createdAt')
    request.session['inbox_unread'] = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
    request.session['has_checked_inbox'] = True

    log_mop(request.user.mop, 'view inbox')
    return render(request, 'mop/mail_inbox.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_outbox(request):
    mail_list = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_SENT).order_by('-createdAt')
    log_mop(request.user.mop, 'view outbox')
    return render(request, 'mop/mail_outbox.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_draft(request):
    mail_list = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_DRAFT).order_by('-createdAt')
    log_mop(request.user.mop, 'view drafts')
    return render(request, 'mop/mail_draft.html', {"mail_list": mail_list})


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_trash(request):
    mail_list = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_TRASHED).order_by('-createdAt')
    log_mop(request.user.mop, 'view trash')
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
    
    request.session['inbox_unread'] = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
    
    if not mail == None:
        m ={}
        m['id'] = mail.id
        m['subject'] = mail.subject
        log_mop(request.user.mop, 'view mail', json.dumps(m))
    
    return render(request, 'mop/mail_view.html', {'mail': mail})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_trashing(request, mail_id):
    try:
        mail = Mail.objects.get(id=mail_id, mop=request.user.mop, state=Mail.STATE_NORMAL)
    except Mail.DoesNotExist:
        #TODO Error handling
        return redirect('mop_index')
    mail.state = Mail.STATE_TRASHED
    mail.save()
    
    if not mail == None:
        m ={}
        m['id'] = mail.id
        m['subject'] = mail.subject
        log_mop(request.user.mop, 'trash mail', json.dumps(m))
    
    if mail.type == Mail.TYPE_RECEIVED:
        return redirect('mop_mail_inbox')
    elif mail.type == Mail.TYPE_SENT:
        return redirect('mop_mail_outbox')
    elif mail.type == Mail.TYPE_DRAFT:
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
    
    if not mail == None:
        m ={}
        m['id'] = mail.id
        m['subject'] = mail.subject
        log_mop(request.user.mop, 'untrash mail', json.dumps(m))
    
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
    
    if not mail == None:
        m ={}
        m['id'] = mail.id
        m['subject'] = mail.subject
        log_mop(request.user.mop, 'delete mail', json.dumps(m))
    
    return redirect('mop_mail_trash')


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_compose_with_form(request, fullSerial):
    return mail_compose(request, fullSerial)

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_compose(request, fullSerial=None):
    #TODO Mail needs a sentAt / savedAt value so that trashing email does not change its date
    if request.method == 'POST':
        mail = Mail(mop=request.user.mop, type=Mail.TYPE_SENT)
        if 'send' in request.POST:
            mail.type = Mail.TYPE_SENT
            mail.read = True
        elif 'draft' in request.POST:
            mail.type = Mail.TYPE_DRAFT
            mail.read = False
        form = MailForm(data=request.POST, instance=mail)
        
        if form.is_valid():
            mail.processed = False
            mail = form.save()
            if mail.type == Mail.TYPE_SENT:
                if not mail.requisitionInstance == None:
                    mail.requisitionInstance.used = True
                    mail.requisitionInstance.save()
                if not mail.mopDocumentInstance == None:
                    mail.mopDocumentInstance.status = MopDocumentInstance.STATUS_LIMBO
                    mail.mopDocumentInstance.save()
            
            
            #TODO remove for real game
            analyze_mail()    
            return redirect('mop_index')
        else:
            #TODO code duplication between here and the else below
            form.fields["unit"].queryset = Unit.objects.all().order_by('serial')
            form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by('-modifiedAt')
            form.fields["mopDocumentInstance"].queryset = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE).order_by('-modifiedAt')
            form.fields["subject"].choices = Mail.CHOICES_SUBJECT_SENDING
            return render(request, 'mop/mail_compose.html', {'form' : form,})
        
    else:
        form = MailForm()
        requisitionInstance_list = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by('-modifiedAt')
        if fullSerial is not None:
            for requisitionInstance in requisitionInstance_list:
                if requisitionInstance.fullSerial() == fullSerial:
                    form = MailForm(initial={'requisitionInstance': requisitionInstance})
                    break
        form.fields["unit"].queryset = Unit.objects.all().order_by('serial')
        form.fields["requisitionInstance"].queryset = requisitionInstance_list
        form.fields["mopDocumentInstance"].queryset = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE).order_by('-modifiedAt')
        form.fields["subject"].choices = Mail.CHOICES_SUBJECT_SENDING
        return render(request, 'mop/mail_compose.html', {'form' : form,})

#TODO code duplication between mail_edit and mail_compose    
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
            mail.read = True
        elif 'draft' in request.POST:
            mail.type = Mail.TYPE_DRAFT
            mail.read = False
        
        form = MailForm(data=request.POST, instance=mail)
        print mail.id
        if form.is_valid():
            mail.processed = False
            mail = form.save()
            
            if mail.type == Mail.TYPE_SENT:
                if not mail.requisitionInstance == None:
                    mail.requisitionInstance.used = True
                    mail.requisitionInstance.save()
                if not mail.mopDocumentInstance == None:
                    mail.mopDocumentInstance.status = MopDocumentInstance.STATUS_LIMBO
                    mail.mopDocumentInstance.save()
            
            #TODO remove for real game
            analyze_mail()    
            return redirect('mop_index')
        else:
            form.fields["unit"].queryset = Unit.objects.all().order_by('serial')
            form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by('-modifiedAt')
            form.fields["mopDocumentInstance"].queryset = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE).order_by('-modifiedAt')
            form.fields["subject"].choices = Mail.CHOICES_SUBJECT_SENDING
            return render(request, 'mop/mail_compose.html', {'form' : form, 'mail':mail})
        
    else:
        form = MailForm(instance=mail)
        #TODO same with documents at all occurences
        form.fields["unit"].queryset = Unit.objects.all().order_by('serial')
        form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by('-modifiedAt')
        form.fields["mopDocumentInstance"].queryset = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE).order_by('-modifiedAt')
        form.fields["subject"].choices = Mail.CHOICES_SUBJECT_SENDING
        return render(request, 'mop/mail_compose.html', {'form' : form, 'mail':mail})

#@login_required(login_url='mop_login')
#@user_passes_test(isMop, login_url='mop_login')
@csrf_exempt
def mail_check(request):
    #TODO: populate with current unread count
    if request.is_ajax() and request.method == 'POST':
        try:
            total_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
        except:
            total_unread = None
        has_new_mail = False
        if total_unread > request.session['inbox_unread']:
            has_new_mail = True
            request.session['has_checked_inbox'] = False
        
        try:
            request.session['inbox_unread'] = total_unread
        except:
            pass
        
        json_data = json.dumps({'total_unread':total_unread, 'has_new_mail':has_new_mail})
    
        return HttpResponse(json_data, mimetype="application/json")


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_blank(request):
    
    # Create a blank form for all Forms that the mop user should have at start
    initialRequisitions = Requisition.objects.filter(type=Requisition.TYPE_INITIAL)
    for initial in initialRequisitions:
        RequisitionBlank.objects.get_or_create(mop=request.user.mop, requisition=initial)
            
    blank_list = RequisitionBlank.objects.filter(mop=request.user.mop).order_by('requisition__serial')            
    
    requisition_list = Requisition.objects.all().order_by('serial')
    requisition_list.allAcquired = True
    for requisition in requisition_list:
        requisition.acquired = False
        for blank in blank_list:
            if requisition == blank.requisition:
                requisition.acquired = True
                break
        if not requisition.acquired:
            requisition_list.allAcquired = False
    
    log_mop(request.user.mop, 'blank forms')
    return render(request, 'mop/forms_blank.html', {"blank_list": blank_list, "requisition_list":requisition_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def form_fill(request, reqBlank_serial):
    #TODO check if user has rights to access the requisition in the first place
    try:
        reqBlank = RequisitionBlank.objects.get(mop=request.user.mop, requisition__serial=reqBlank_serial)
    except RequisitionBlank.DoesNotExist:
        reqBlank=None
        
    if request.method == 'POST':
        requisitionInstance = RequisitionInstance(blank=reqBlank)
        form = RequisitionInstanceForm(data=request.POST, instance=requisitionInstance)
        if form.is_valid():
            form.save()
            
            f ={}
            f['form_id'] = reqBlank.requisition.id
            f['form_name'] = reqBlank.requisition.name
            f['instance_id'] = requisitionInstance.id
            f['data'] = form.data
            log_mop(request.user.mop, 'fill form', json.dumps(f))
            provlog_add_mop_sign_form(request.user.mop, requisitionInstance, request.session.session_key)
            return redirect('mop_forms_signed')
    else:
        form = RequisitionInstanceForm()
        return render(request, 'mop/forms_fill.html', {"reqBlank": reqBlank, "form": form})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_signed(request):
    requisitionInstance_list = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by("-modifiedAt")
    
    log_mop(request.user.mop, 'view filled forms')
    return render(request, 'mop/forms_signed.html', {"requisitionInstance_list": requisitionInstance_list})


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_archive(request):
    requisitionInstance_list = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=True).order_by("-modifiedAt")
    
    log_mop(request.user.mop, 'view archived forms')
    return render(request, 'mop/forms_archive.html', {"requisitionInstance_list": requisitionInstance_list})


@staff_member_required
def control(request):
    output = None
    if request.method == 'POST':
        if 'mail' in request.POST:
            output = analyze_mail()
        elif 'performance' in request.POST:
            output = analyze_performance()
        elif 'randomizer' in request.POST:
            output = create_documents()
    return render(request, 'mop/control.html', {'output':output})       


    
    