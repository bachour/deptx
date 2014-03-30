from django.conf.urls import patterns, url

from cron import views
from players import views as players_views
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'registration/$', players_views.register, name='players_registration'),
    url(r'registration/([-\w]+)/study', players_views.activate_study, name='players_activation_study'),
    url(r'registration/([-\w]+)/nostudy', players_views.activate_nostudy, name='players_activation_nostudy'),
    
    url(r'password/reset/$', 'django.contrib.auth.views.password_reset', {'post_reset_redirect' : '/password/reset/done/'}, name="password_reset"),
    url(r'password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'post_reset_redirect' : '/password/done/'}),
    url(r'password/done/$', 'django.contrib.auth.views.password_reset_complete'),



    url(r'^$', views.index, name='cron_index'),
    url(r'login/', views.login, name='cron_login'),
    url(r'logout/', views.logout_view, name='cron_logout'),
    url(r'mission/([-\w]+)/introduction', views.mission_intro, name='cron_mission_intro'),
    url(r'mission/([-\w]+)/briefing', views.mission_briefing, name='cron_mission_briefing'),
    url(r'mission/([-\w]+)/overview', views.mission_cases, name='cron_mission_cases'),
    url(r'mission/([-\w]+)/case/([-\w]+)/$', views.case_intro, name='cron_case_intro'),
    url(r'mission/([-\w]+)/case/([-\w]+)/provenance/([-\w]+)', views.provenance, name='cron_provenance'),
    url(r'mission/([-\w]+)/case/([-\w]+)/content/([-\w]+)', views.no_provenance, name='cron_no_provenance'),
    url(r'mission/([-\w]+)/case/([-\w]+)/report', views.case_report, name='cron_case_report'),
    url(r'mission/([-\w]+)/case/([-\w]+)/outcome', views.case_outro, name='cron_case_outro'),
    url(r'mission/([-\w]+)/debriefing', views.mission_debriefing, name='cron_mission_debriefing'),
    url(r'mission/([-\w]+)/aftermath', views.mission_outro, name='cron_mission_outro'),
    url(r'mission/([-\w]+)/reset', views.missionInstance_reset, name='cron_mission_reset'),
    url(r'mission/([-\w]+)/delete', views.missionInstance_delete, name='cron_mission_delete'),
    url(r'archive/$', views.archive, name='cron_archive'),
    url(r'messages/$', views.messages, name='cron_messages'),
    url(r'messages/compose/', views.message_compose, name='cron_message_compose'),
    
    url(r'operation/cluster-mine/$', views.operation_cluster_mine, name='cron_operation_cluster_mine'),
    url(r'operation/cluster-mine/infiltration/$', views.operation_cluster_mine_infiltration, name='cron_operation_cluster_mine_infiltration'),
    url(r'operation/cluster-mine/sync/$', views.operation_cluster_mine_sync, name='cron_operation_cluster_mine_sync'),

    
    url(r'chat/$', views.chat, name='cron_chat'),
    url(r'chat/send/', views.chat_send, name='cron_chat_send'),
    url(r'chat/sync/', views.chat_sync, name='cron_chat_sync'),
    
    url(r'intelligence/cr0n-report-gc8.html', views.intelligence_report_gc8, name='cron_intelligence_report_gc8'),
    url(r'intelligence/inside-the-bunker.html', views.intelligence_bunker, name='cron_intelligence_bunker'),
    url(r'intelligence/mop-message.html', views.intelligence_mop_message, name='cron_intelligence_mop_message'),
    url(r'intelligence/dr-moreau.html', views.intelligence_dr_moreau, name='cron_intelligence_dr_moreau'),
    url(r'intelligence/inside-the-bunker/([-\w].+)', views.intelligence_bunker_image, name='cron_intelligence_bunker_image'),
    url(r'intelligence/jean-baker-message.html', views.intelligence_jean_baker_message, name='cron_intelligence_jean_baker_message'),
     
    url(r'profile/$', views.profile, name='cron_profile'),
    url(r'termination/$', views.terminate, name='cron_terminate'),
    url(r'termination/([-\w].+)', views.terminate_remote, name='cron_terminate_remote'),
    
    url(r'hack/([-\w]+)', views.hack_document, name='cron_hack_document'),

)