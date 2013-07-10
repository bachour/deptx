from django.conf.urls import patterns, url

from mop import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='mop_index'),
    url(r'login/', views.login, name='mop_login'),
    url(r'rules/', views.rules, name='mop_rules'),
    url(r'tasks/', views.tasks, name='mop_tasks'),
    url(r'forms/blank', views.forms_blank, name='mop_forms_blank'),
    url(r'forms/signed', views.forms_signed, name='mop_forms_signed'),
    url(r'forms/fill/(\d+)', views.forms_fill, name='mop_forms_fill'),
    
    
    url(r'documents/', views.documents, name='mop_documents'),
    url(r'mail/inbox/', views.mail_inbox, name='mop_mail_inbox'),
    url(r'mail/outbox/', views.mail_outbox, name='mop_mail_outbox'),
    url(r'mail/trash/', views.mail_trash, name='mop_mail_trash'),
    url(r'mail/draft/', views.mail_draft, name='mop_mail_draft'),
    url(r'mail/view/(\d+)', views.mail_view, name='mop_mail_view'),
    url(r'mail/trashing/(\d+)', views.mail_trashing, name='mop_mail_trashing'),    
    url(r'mail/untrashing/(\d+)', views.mail_untrashing, name='mop_mail_untrashing'),    
    url(r'mail/deleting/(\d+)', views.mail_deleting, name='mop_mail_deleting'),
    url(r'mail/compose/$', views.mail_compose, name='mop_mail_compose'),
    url(r'mail/compose/(\d+)', views.mail_edit, name='mop_mail_edit'),
        
)
