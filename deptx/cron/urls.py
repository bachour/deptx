from django.conf.urls import patterns, url

from cron import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='cron_index'),
    url(r'login/', views.login, name='cron_login'),
    url(r'mopmaker/', views.mopmaker, name='cron_mopmaker'),
    url(r'mission/', views.mission, name='cron_mission'),
    url(r'case/([-\w]+)', views.case, name='cron_case_detail'),
    url(r'provenance/([-\w]+)', views.provenance, name='cron_provenance'),
   
)