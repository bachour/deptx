from django.conf.urls import patterns, url

from cron import views
from players import views as players_views

urlpatterns = patterns('',
    url(r'registration/$', players_views.register, name='players_registration'),
    url(r'registration/([-\w]+)', players_views.activate, name='players_activation'),

    url(r'^$', views.index, name='cron_index'),
    url(r'login/', views.login, name='cron_login'),
    url(r'logout/', views.logout_view, name='cron_logout'),
    url(r'mopmaker/', views.mopmaker, name='cron_mopmaker'),
    url(r'mission/$', views.mission, name='cron_mission'),
    url(r'mission/reset/', views.mission_reset, name='cron_mission_reset'),
    url(r'mission/redo/(\d+)', views.mission_redo, name='cron_mission_redo'),
    url(r'case/([-\w]+)', views.case, name='cron_case_detail'),
    url(r'provenance/([-\w]+)', views.provenance, name='cron_provenance'), 
    url(r'profile/', views.profile, name='cron_profile'),
    url(r'hack/([-\w]+)', views.hack_document, name='cron_hack_document'),

)