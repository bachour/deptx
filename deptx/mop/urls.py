from django.conf.urls import patterns, url

from mop import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='mop_index'),
    url(r'login/', views.login, name='mop_login'),
    url(r'rules/', views.rules, name='mop_rules'),
    url(r'tasks/', views.tasks, name='mop_tasks'),
    url(r'forms/', views.forms, name='mop_forms'),
    url(r'documents/', views.documents, name='mop_documents'),
    url(r'inbox/', views.inbox, name='mop_inbox'),
    url(r'outbox/', views.outbox, name='mop_outbox'),
)
