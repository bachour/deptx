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
    url(r'hq/$', views.hq, name='cron_hq'),
    url(r'hq/m/(\d+)/intro', views.hq_mission_intro, name='cron_hq_mission_intro'),
    url(r'hq/m/(\d+)/briefing', views.hq_mission_briefing, name='cron_hq_mission_briefing'),
    url(r'hq/m/(\d+)/debriefing', views.hq_mission_debriefing, name='cron_hq_mission_debriefing'),
    url(r'hq/m/(\d+)/outro', views.hq_mission_outro, name='cron_hq_mission_outro'),
    url(r'hq/c/(\d+)/intro', views.hq_case_intro, name='cron_hq_case_intro'),
    url(r'hq/c/(\d+)/outro', views.hq_case_outro, name='cron_hq_case_outro'),
)