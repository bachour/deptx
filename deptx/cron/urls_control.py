from django.conf.urls import patterns, url

from cron import views

urlpatterns = patterns('',
    url(r'^$', views.hq, name='cron_hq'),
    url(r'm/(\d+)/intro', views.hq_mission_intro, name='cron_hq_mission_intro'),
    url(r'm/(\d+)/briefing', views.hq_mission_briefing, name='cron_hq_mission_briefing'),
    url(r'm/(\d+)/cases', views.hq_cases, name='cron_hq_cases'),
    url(r'm/(\d+)/debriefing', views.hq_mission_debriefing, name='cron_hq_mission_debriefing'),
    url(r'm/(\d+)/outro', views.hq_mission_outro, name='cron_hq_mission_outro'),
    url(r'c/(\d+)/intro', views.hq_case_intro, name='cron_hq_case_intro'),
    url(r'c/(\d+)/report', views.hq_case_report, name='cron_hq_case_report'),
    url(r'c/(\d+)/outro', views.hq_case_outro, name='cron_hq_case_outro'),
    url(r'mail/$', views.hq_mail, name='cron_hq_mail'),
    url(r'mail/outstanding', views.hq_mail_outstanding, name='cron_hq_mail_outstanding'),
    url(r'mail/noreply/(\d+)/$', views.hq_mail_noreply, name='cron_hq_mail_noreply'),
    url(r'mail/reply/(\d+)/$', views.hq_mail_reply, name='cron_hq_mail_reply'),
    url(r'answers/$', views.hq_answers, name='cron_hq_answers'),
    url(r'stats/$', views.hq_stats, name='cron_hq_stats'),
    url(r'stats/(\d+)/$', views.hq_stats_cron, name='cron_hq_stats_cron'),
    url(r'stats/documents/all/$', views.hq_stats_documents, name='cron_hq_stats_documents'),
    url(r'stats/documents/$', views.hq_stats_documents_overview, name='cron_hq_stats_documents_overview'),
    url(r'stats/document/(\d+)/$', views.hq_stats_document, name='cron_hq_stats_document'),
    
    
)