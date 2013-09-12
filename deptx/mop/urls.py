from django.conf.urls import patterns, url

from mop import views

urlpatterns = patterns('',
    url(r'^$', views.public_index, name='mop_public_index'),
    url(r'intranet/$', views.index, name='mop_index'),
    url(r'intranet/login/', views.login, name='mop_login'),
    url(r'intranet/logout/', views.logout_view, name='mop_logout'),
    url(r'intranet/rules/', views.rules, name='mop_rules'),
    url(r'intranet/tasks/', views.tasks, name='mop_tasks'),
    url(r'intranet/forms/blank', views.forms_blank, name='mop_forms_blank'),
    url(r'intranet/forms/signed', views.forms_signed, name='mop_forms_signed'),
    url(r'intranet/forms/fill/(\d+)', views.form_fill, name='mop_forms_fill'),
    url(r'intranet/documents/$', views.documents, name='mop_documents'),
    url(r'intranet/documents/view/(\d+)', views.document_view, name='mop_documents_view'),
    url(r'intranet/documents/provenance/(\d+)', views.document_provenance, name='mop_documents_provenance'),
    url(r'intranet/mail/inbox/', views.mail_inbox, name='mop_mail_inbox'),
    url(r'intranet/mail/outbox/', views.mail_outbox, name='mop_mail_outbox'),
    url(r'intranet/mail/trash/', views.mail_trash, name='mop_mail_trash'),
    url(r'intranet/mail/draft/', views.mail_draft, name='mop_mail_draft'),
    url(r'intranet/mail/view/(\d+)', views.mail_view, name='mop_mail_view'),
    url(r'intranet/mail/trashing/(\d+)', views.mail_trashing, name='mop_mail_trashing'),    
    url(r'intranet/mail/untrashing/(\d+)', views.mail_untrashing, name='mop_mail_untrashing'),    
    url(r'intranet/mail/deleting/(\d+)', views.mail_deleting, name='mop_mail_deleting'),
    url(r'intranet/mail/compose/$', views.mail_compose, name='mop_mail_compose'),
    url(r'intranet/mail/compose/(\d+)', views.mail_edit, name='mop_mail_edit'),
          
)
