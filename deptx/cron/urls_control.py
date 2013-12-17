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
)