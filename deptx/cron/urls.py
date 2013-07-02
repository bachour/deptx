from django.conf.urls import patterns, url

from cron import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='cron_index'),
    url(r'login/', views.login, name='cron_login'),
)