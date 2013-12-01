from django.conf.urls import patterns, url

from mop import views

urlpatterns = patterns('',
    url(r'^$', views.login, name='mop_login'),
    url(r'intranet/$', views.index, name='mop_index'),

    url(r'intranet/logout/', views.logout_view, name='mop_logout'),
    url(r'intranet/rules/', views.rules, name='mop_rules'),
    url(r'intranet/performance/', views.performance, name='mop_performance'),
    url(r'intranet/forms/blank/', views.forms_blank, name='mop_forms_blank'),
    url(r'intranet/forms/signed/', views.forms_signed, name='mop_forms_signed'),
    url(r'intranet/forms/archive/', views.forms_archive, name='mop_forms_archive'),
    url(r'intranet/forms/fill/([-\w]+)', views.form_fill, name='mop_forms_fill'),
    url(r'intranet/documents/archive/', views.documents_archive, name='mop_documents_archive'),
    url(r'intranet/documents/pool/', views.documents_pool, name='mop_documents_pool'),
    url(r'intranet/documents/$', views.documents, name='mop_documents'),
    url(r'intranet/document/([-\w]+)/provenance', views.provenance, name='mop_provenance'),
    url(r'intranet/mail/inbox/', views.mail_inbox, name='mop_mail_inbox'),
    url(r'intranet/mail/outbox/', views.mail_outbox, name='mop_mail_outbox'),
    url(r'intranet/mail/trash/', views.mail_trash, name='mop_mail_trash'),
    url(r'intranet/mail/draft/', views.mail_draft, name='mop_mail_draft'),
    url(r'intranet/mail/view/([-\w]+)', views.mail_view, name='mop_mail_view'),
    url(r'intranet/mail/trashing/([-\w]+)', views.mail_trashing, name='mop_mail_trashing'),    
    url(r'intranet/mail/untrashing/([-\w]+)', views.mail_untrashing, name='mop_mail_untrashing'),    
    url(r'intranet/mail/deleting/([-\w]+)', views.mail_deleting, name='mop_mail_deleting'),
    url(r'intranet/mail/compose/$', views.mail_compose, name='mop_mail_compose'),
    url(r'intranet/mail/compose/form/([-\w]+)', views.mail_compose, name='mop_mail_compose'),
    url(r'intranet/mail/compose/([-\w]+)', views.mail_edit, name='mop_mail_edit'),
    url(r'intranet/mail/check/', views.mail_check, name='mop_mail_check'),
    
    url(r'intranet/control/$', views.control, name='mop_control'),
          
)
