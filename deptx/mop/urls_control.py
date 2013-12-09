from django.conf.urls import patterns, url

from mop import views

urlpatterns = patterns('',
    url(r'^$', views.control, name='mop_control'),
    url(r'randomize/(\d+)', views.control_randomize, name='mop_control_randomize'),
    url(r'mail/$', views.control_mail, name='mop_control_mail'),      
)
