from django.conf.urls import patterns, url

from mop import views

urlpatterns = patterns('',
    url(r'^$', views.control, name='mop_control'),
    url(r'randomize/(\d+)', views.control_randomize, name='mop_control_randomize'),
    url(r'mail/$', views.control_mail, name='mop_control_mail'),
    url(r'mail/outstanding', views.control_mail_outstanding, name='mop_control_mail_outstanding'),
    url(r'mail/noreply/(\d+)/$', views.control_mail_noreply, name='mop_control_mail_noreply'),
    url(r'mail/reply/(\d+)/$', views.control_mail_reply, name='mop_control_mail_reply'),      
)
