from django.shortcuts import render, redirect

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from django.contrib import auth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

from mop import documentcreator
from players.models import Mop
from players.forms import MopCheckForm, PasswordForm

from django.contrib.auth.forms import UserCreationForm

from assets.models import Requisition, Unit, CronDocument, MopDocument
from mop.models import Mail, RequisitionInstance, RequisitionBlank, MopDocumentInstance, RandomizedDocument, MopTracker, TrustInstance
from mop.forms import MailForm, RequisitionInstanceForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
import json

from mop.performer import analyze_performance

from django.views.decorators.csrf import csrf_exempt
from mop.mailserver import analyze_mail
import tutorial
from deptx.helpers import now
from logger import logging
from logger.models import ProvLog, ActionLog

def isMop(user):
    if user:
        for mop in Mop.objects.filter(user=user):
            if mop.active:
                return True
    return False

def custom_404_view(request):
    return render(request, 'mop/404.html')

def custom_500_view(request):
    return render(request, 'mop/500.html')

def index(request):

    if not request.user == None and request.user.is_active and isMop(request.user):

        hide = tutorial.hide(request.user.mop.mopTracker)
  
        #MAIL MANAGING
        #inbox = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).count()
        inbox_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
        #outbox = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_SENT).count()
        #trash = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_TRASHED).count()
        #draft = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_DRAFT).count()
        
        request.user.mop.mopTracker.unreadEmails = inbox_unread
        request.user.mop.mopTracker.save()
        
        logging.log_action(ActionLog.ACTION_MOP_VIEW_INDEX, mop=request.user.mop)
        
        context = {'user': request.user, 'inbox_unread': inbox_unread, 'hide':hide}

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

            logging.log_action(ActionLog.ACTION_MOP_LOGIN, mop=request.user.mop)
            mopTracker, created = MopTracker.objects.get_or_create(mop=request.user.mop)
            mopTracker.hasCheckedInbox = False
            mopTracker.save()
            
            if created:
                tutorial.firstLogin(mopTracker)
            
            return HttpResponseRedirect(reverse('mop_index'))
            
        else:
            return render(request, 'mop/login.html', {'form' : form})
        
    else:
        form =  AuthenticationForm()
        return render(request, 'mop/login.html', {'form' : form})

def logout_view(request):
    if not request.user == None and request.user.is_active and isMop(request.user):
        logging.log_action(ActionLog.ACTION_MOP_LOGOUT, mop=request.user.mop)
        logout(request)
    return redirect('mop_index')

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def rules(request):
    unit_list = Unit.objects.all().order_by('serial')
    requisition_list = Requisition.objects.all().order_by('serial')
    logging.log_action(ActionLog.ACTION_MOP_VIEW_GUIDEBOOK, mop=request.user.mop)
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
    logging.log_action(ActionLog.ACTION_MOP_VIEW_PERFORMANCE, mop=request.user.mop)
    return render(request, 'mop/performance.html', {'trustInstance_list':trustInstance_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def documents_pool(request):

    randomizedDocument_list_all = tutorial.getTutorialDocument(request.user.mop.mopTracker)
    if randomizedDocument_list_all == None:
        randomizedDocument_list_all = getDocumentPoolForMop(request.user.mop)

    mopDocumentInstance_list = MopDocumentInstance.objects.filter(mop=request.user.mop)
    
        
    for randomizedDocument in randomizedDocument_list_all:
        for mopDocumentInstance in mopDocumentInstance_list:
            if mopDocumentInstance.randomizedDocument == randomizedDocument:
                randomizedDocument.exists = True
                break
    randomizedDocument_list = paginate(request, randomizedDocument_list_all)
 
    logging.log_action(ActionLog.ACTION_MOP_VIEW_DOCUMENTS_POOL, mop=request.user.mop)
    return render(request, 'mop/documents_pool.html', {"randomizedDocument_list": randomizedDocument_list})

def getDocumentPoolForMop(mop):
        all_list = RandomizedDocument.objects.filter(active=True).filter(mopDocument__clearance__lte=mop.mopTracker.clearance)
        public_list = all_list.filter(mop__isnull=True)
        personal_list = all_list.filter(mop=mop)
        randomizedDocument_list = public_list | personal_list
        return randomizedDocument_list.order_by('createdAt')


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def documents(request):
    mopDocumentInstance_list_all = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE)
    mopDocumentInstance_list = paginate(request, mopDocumentInstance_list_all)
    logging.log_action(ActionLog.ACTION_MOP_VIEW_DOCUMENTS_DRAWER, mop=request.user.mop)
    return render(request, 'mop/documents.html', {"mopDocumentInstance_list": mopDocumentInstance_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def documents_archive(request):
    mopDocumentInstance_list_all = MopDocumentInstance.objects.filter(mop=request.user.mop).exclude(status=MopDocumentInstance.STATUS_ACTIVE).exclude(status=MopDocumentInstance.STATUS_HACKED)
    mopDocumentInstance_list = paginate(request, mopDocumentInstance_list_all)
    logging.log_action(ActionLog.ACTION_MOP_VIEW_DOCUMENTS_ARCHIVE, mop=request.user.mop)
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
        if documentInstance.type == MopDocumentInstance.TYPE_MOP:
            logging.log_prov(action=ProvLog.ACTION_OPEN, mopDocumentInstance=documentInstance)
        else:
            logging.log_prov(action=ProvLog.ACTION_OPEN, cronDocumentInstance=documentInstance)
        logging.log_action(ActionLog.ACTION_MOP_VIEW_PROVENANCE, mop=request.user.mop, mopDocumentInstance=documentInstance, mopDocumentInstanceCorrect=documentInstance.correct)
        return render(request, 'mop/provenance.html', {'document': document, "inactive":inactive})
    else:
        logging.log_action(ActionLog.ACTION_MOP_VIEW_PROVENANCE_NO_CLEARANCE, mop=request.user.mop, mopDocumentInstance=documentInstance)
        return render(request, 'mop/provenance_noclearance.html', {'document': document})


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_inbox(request):
    mail_list_all = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).order_by('-createdAt')
    mail_list = paginate(request, mail_list_all)
    
    try:
        page = request.GET.get['page']
    except:
        page = 1
    if page == 1:
        request.user.mop.mopTracker.unreadEmails = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
        request.user.mop.mopTracker.hasCheckedInbox = True
        request.user.mop.mopTracker.save()

    logging.log_action(ActionLog.ACTION_MOP_VIEW_INBOX, mop=request.user.mop)
    return render(request, 'mop/mail_inbox.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_outbox(request):
    mail_list_all = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_SENT).order_by('-createdAt')
    mail_list = paginate(request, mail_list_all)
    logging.log_action(ActionLog.ACTION_MOP_VIEW_OUTBOX, mop=request.user.mop)
    return render(request, 'mop/mail_outbox.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_draft(request):
    mail_list_all = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_DRAFT).order_by('-createdAt')
    mail_list = paginate(request, mail_list_all)
    logging.log_action(ActionLog.ACTION_MOP_VIEW_DRAFT, mop=request.user.mop)
    return render(request, 'mop/mail_draft.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_trash(request):
    mail_list_all = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_TRASHED).order_by('-createdAt')
    mail_list = paginate(request, mail_list_all)
    logging.log_action(ActionLog.ACTION_MOP_VIEW_TRASH, mop=request.user.mop)
    return render(request, 'mop/mail_trash.html', {"mail_list": mail_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_view(request, serial):
    try:
        mail = Mail.objects.get(serial=serial, mop=request.user.mop)
        mail.read = True
        mail.save()
    except Mail.DoesNotExist:
        mail = None
    
    request.user.mop.mopTracker.unreadEmails = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
    request.user.mop.mopTracker.save()
    
    #to check if this is the last tutorial email
    tutorial.cronMail(request.user.mop.mopTracker, mail)
    
    logging.log_action(ActionLog.ACTION_MOP_VIEW_MAIL, mop=request.user.mop)
    return render(request, 'mop/mail_view.html', {'mail': mail})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_trashing(request, serial):
    try:
        mail = Mail.objects.get(serial=serial, mop=request.user.mop, state=Mail.STATE_NORMAL)
    except Mail.DoesNotExist:
        #TODO Error handling
        return redirect('mop_index')
    mail.state = Mail.STATE_TRASHED
    mail.save()
    
    logging.log_action(ActionLog.ACTION_MOP_MAIL_TRASH, mop=request.user.mop, mail=mail)
    
    if mail.type == Mail.TYPE_RECEIVED:
        return redirect('mop_mail_inbox')
    elif mail.type == Mail.TYPE_SENT:
        return redirect('mop_mail_outbox')
    elif mail.type == Mail.TYPE_DRAFT:
        return redirect('mop_mail_draft')
    

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_untrashing(request, serial):
    try:
        mail = Mail.objects.get(serial=serial, mop=request.user.mop, state=Mail.STATE_TRASHED)
    except Mail.DoesNotExist:
        return redirect('mop_index')
    mail.read = True
    mail.state = Mail.STATE_NORMAL
    mail.save()
    
    logging.log_action(ActionLog.ACTION_MOP_MAIL_UNTRASH, mop=request.user.mop, mail=mail)
    
    return redirect('mop_mail_trash')

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_deleting(request, serial):
    try:
        mail = Mail.objects.get(serial=serial, mop=request.user.mop, state=Mail.STATE_TRASHED)
    except Mail.DoesNotExist:
        #TODO Error handling
        return redirect('mop_index')
    mail.read = True
    mail.state = Mail.STATE_DELETED
    mail.save()
    
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
            mail.sentAt = now()
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
                logging.log_action(ActionLog.ACTION_MOP_MAIL_SEND, mop=request.user.mop, mail=mail)
            else:
                logging.log_action(ActionLog.ACTION_MOP_MAIL_DRAFT, mop=request.user.mop, mail=mail)    
            return redirect('mop_mail_outbox')
        else:
            #TODO code duplication between here and the else below
            form.fields["unit"].queryset = Unit.objects.all().order_by('serial')
            form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by('-modifiedAt')
            form.fields["mopDocumentInstance"].queryset = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE).order_by('-modifiedAt')
            form.fields["subject"].choices = Mail.CHOICES_SUBJECT_SENDING
            
            logging.log_action(ActionLog.ACTION_MOP_VIEW_COMPOSE, mop=request.user.mop)
            return render(request, 'mop/mail_compose.html', {'form' : form,})
        
    else:
        form = MailForm()
        requisitionInstance_list = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by('-modifiedAt')
        withForm = False
        if fullSerial is not None:
            for requisitionInstance in requisitionInstance_list:
                if requisitionInstance.fullSerial() == fullSerial:
                    subject = None
                    if requisitionInstance.blank.requisition.category == Requisition.CATEGORY_FORM:
                        subject = Mail.SUBJECT_REQUEST_FORM
                    elif requisitionInstance.blank.requisition.category == Requisition.CATEGORY_DOCUMENT:
                        subject = Mail.SUBJECT_REQUEST_DOCUMENT
                    elif requisitionInstance.blank.requisition.category == Requisition.CATEGORY_SUBMISSION:
                        subject = Mail.SUBJECT_SUBMIT_DOCUMENT
                    elif requisitionInstance.blank.requisition.category == Requisition.CATEGORY_HELP:
                        subject = Mail.SUBJECT_REQUEST_HELP
                    form = MailForm(initial={'requisitionInstance': requisitionInstance, 'unit': requisitionInstance.blank.requisition.unit, 'subject':subject})
                    logging.log_action(ActionLog.ACTION_MOP_MAIL_COMPOSE_WITH_FORM, mop=request.user.mop, requisitionInstance=requisitionInstance)
                    withForm = True
                    break
        form.fields["unit"].queryset = Unit.objects.all().order_by('serial')
        form.fields["requisitionInstance"].queryset = requisitionInstance_list
        form.fields["mopDocumentInstance"].queryset = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE).order_by('-modifiedAt')
        form.fields["subject"].choices = Mail.CHOICES_SUBJECT_SENDING
        if not withForm:
            logging.log_action(ActionLog.ACTION_MOP_VIEW_COMPOSE, mop=request.user.mop)
        return render(request, 'mop/mail_compose.html', {'form' : form,})

#TODO code duplication between mail_edit and mail_compose    
@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def mail_edit(request, serial):
    try:
        mail = Mail.objects.get(serial=serial)
    except mail.DoesNotExist:
        #TODO error handling
        return redirect('mop_mail_index')
    
    if request.method == 'POST':
        if 'send' in request.POST:
            mail.type = Mail.TYPE_SENT
            mail.read = True
            mail.sentAt = now()
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
                logging.log_action(ActionLog.ACTION_MOP_MAIL_SEND, mop=request.user.mop, mail=mail)
            else:
                logging.log_action(ActionLog.ACTION_MOP_MAIL_DRAFT, mop=request.user.mop, mail=mail)
            return redirect('mop_mail_outbox')
        else:
            form.fields["unit"].queryset = Unit.objects.all().order_by('serial')
            form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by('-modifiedAt')
            form.fields["mopDocumentInstance"].queryset = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE).order_by('-modifiedAt')
            form.fields["subject"].choices = Mail.CHOICES_SUBJECT_SENDING
            logging.log_action(ActionLog.ACTION_MOP_VIEW_EDIT, mop=request.user.mop)
            return render(request, 'mop/mail_compose.html', {'form' : form, 'mail':mail})
        
    else:
        form = MailForm(instance=mail)
        #TODO same with documents at all occurences
        form.fields["unit"].queryset = Unit.objects.all().order_by('serial')
        form.fields["requisitionInstance"].queryset = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by('-modifiedAt')
        form.fields["mopDocumentInstance"].queryset = MopDocumentInstance.objects.filter(mop=request.user.mop).filter(status=MopDocumentInstance.STATUS_ACTIVE).order_by('-modifiedAt')
        form.fields["subject"].choices = Mail.CHOICES_SUBJECT_SENDING
        logging.log_action(ActionLog.ACTION_MOP_VIEW_EDIT, mop=request.user.mop)
        return render(request, 'mop/mail_compose.html', {'form' : form, 'mail':mail})

@csrf_exempt
def mail_check(request):
    json_data = json.dumps({'error':True})
    #TODO: populate with current unread count
    if not request.user == None and request.user.is_active and isMop(request.user):
        if request.is_ajax() and request.method == 'POST':
            try:
                total_unread = Mail.objects.filter(mop=request.user.mop).filter(state=Mail.STATE_NORMAL).filter(type=Mail.TYPE_RECEIVED).filter(read=False).count()
            except:
                total_unread = None
            has_new_mail = False
            if total_unread > request.user.mop.mopTracker.unreadEmails:
                has_new_mail = True
                request.user.mop.mopTracker.hasCheckedInbox = False
            
            try:
                request.user.mop.mopTracker.unreadEmails = total_unread
            except:
                pass
            
            request.user.mop.mopTracker.save()
            
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
    
    logging.log_action(ActionLog.ACTION_MOP_VIEW_FORMS_BLANKS, mop=request.user.mop)
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
            requisitionInstance = form.save()
            logging.log_action(ActionLog.ACTION_MOP_FORM_SIGN, mop=request.user.mop, requisitionInstance=requisitionInstance)
            return redirect('mop_forms_signed')
    else:
        form = RequisitionInstanceForm()
        logging.log_action(ActionLog.ACTION_MOP_VIEW_FORMS_FILL, mop=request.user.mop)
        return render(request, 'mop/forms_fill.html', {"reqBlank": reqBlank, "form": form})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_signed(request):
    requisitionInstance_list_all = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=False).order_by("-modifiedAt")
    requisitionInstance_list = paginate(request, requisitionInstance_list_all)    
    logging.log_action(ActionLog.ACTION_MOP_VIEW_FORMS_SIGNED, mop=request.user.mop)
    return render(request, 'mop/forms_signed.html', {"requisitionInstance_list": requisitionInstance_list})


@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def forms_archive(request):
    requisitionInstance_list_all = RequisitionInstance.objects.filter(blank__mop=request.user.mop).filter(used=True).order_by("-modifiedAt")
    requisitionInstance_list = paginate(request, requisitionInstance_list_all)
    logging.log_action(ActionLog.ACTION_MOP_VIEW_FORMS_ARCHIVE, mop=request.user.mop)
    return render(request, 'mop/forms_archive.html', {"requisitionInstance_list": requisitionInstance_list})

@login_required(login_url='mop_login')
@user_passes_test(isMop, login_url='mop_login')
def form_trashing(request, fullSerial):
    requisitionInstance_list = RequisitionInstance.objects.filter(blank__mop=request.user.mop)
    for requisitionInstance in requisitionInstance_list:
        if requisitionInstance.fullSerial() == fullSerial:
            requisitionInstance.trashed = True
            requisitionInstance.used = True
            requisitionInstance.save()
            logging.log_action(ActionLog.ACTION_MOP_FORM_TRASH, mop=request.user.mop, requisitionInstance=requisitionInstance)
            return redirect('mop_forms_signed')

def paginate(request, all_list, items=20):
    paginator = Paginator(all_list, items)

    page = request.GET.get('page')
    try:
        paginated = paginator.page(page)
    except PageNotAnInteger:
        paginated = paginator.page(1)
    except EmptyPage:
        paginated = paginator.page(paginator.num_pages)
    return paginated

def password(request):
    if request.method == 'POST':
        mop_form = MopCheckForm(request.POST, prefix="mop")
        pass_form = PasswordForm(request.POST, prefix="pass")
        if mop_form.is_valid() and pass_form.is_valid():
            mop_data = mop_form.cleaned_data
            pass_data = pass_form.cleaned_data
            mop = Mop.objects.get(serial=pass_data['serial'])
            wrong = {}
            correct = True
            if not mop.firstname == mop_data['firstname']:
                correct = False
                wrong['firstname'] = True
            if not mop.lastname == mop_data['lastname']:
                correct = False
                wrong['lastname'] = True 
            if not mop.dob == mop_data['dob']:
                correct = False
                wrong['dob'] = True
            if not mop.gender == mop_data['gender']:
                correct = False
                wrong['gender'] = True
            if not mop.weight == mop_data['weight']:
                correct = False
                wrong['weight'] = True
            if not mop.height == mop_data['height']:
                correct = False
                wrong['height'] = True
            if not mop.marital == mop_data['marital']:
                correct = False
                wrong['marital'] = True
            if not mop.hair == mop_data['hair']:
                correct = False
                wrong['hair'] = True
            if not mop.eyes == mop_data['eyes']:
                correct = False
                wrong['eyes'] = True
            
            if correct:
                mop.user.set_password(pass_data['password1'])
                mop.user.save()
                return render(request, 'mop/password.html', {'correct':correct, "mop":mop})
            else:
                return render(request, 'mop/password.html', {'mop_form':mop_form, 'pass_form':pass_form, 'wrong':wrong})
        
        else:
            return render(request, 'mop/password.html', {'mop_form':mop_form, 'pass_form':pass_form})
        
    else:
        mop_form = MopCheckForm(prefix='mop')
        pass_form = PasswordForm(prefix='pass', initial={'pasword1':'haha'})
        return render(request, 'mop/password.html', {'mop_form':mop_form, 'pass_form':pass_form})


@staff_member_required
def control(request):
    output = None
    if request.method == 'POST':
        if 'mail' in request.POST:
            output = analyze_mail()
        elif 'performance' in request.POST:
            output = analyze_performance()
        elif 'create daily documents' in request.POST:
            output = documentcreator.create_daily_documents()
        elif 'remove old documents' in request.POST:
            output = documentcreator.remove_old_documents()
    mail_list = Mail.objects.filter(type=Mail.TYPE_SENT).filter(processed=False)
    mopDocument_list = MopDocument.objects.all()
    for mopDocument in mopDocument_list:
        mopDocument.amount = RandomizedDocument.objects.filter(mopDocument=mopDocument).filter(active=True).count()
    
    mop_list = Mop.objects.all()

    for mop in mop_list:
        mop.availableDocs = getDocumentPoolForMop(mop).count() - MopDocumentInstance.objects.filter(mop=mop).count()
    
    return render(request, 'mop/control.html', {'output':output, 'mail_list':mail_list, 'mopDocument_list':mopDocument_list, 'mop_list':mop_list})       

@staff_member_required
def control_randomize(request, mopDocument_id):
    mopDocument = MopDocument.objects.get(id=mopDocument_id)
    documentcreator.create_single_document(mopDocument)
    return HttpResponseRedirect(reverse('mop_control'))
    
    
    