from django.conf.urls import patterns, url

from provmanager import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='provmanager_index'),
     url(r'view/(\d+)', views.view, name='provmanager_view'),
     url(r'convert/(\d+)', views.convert, name='provmanager_convert'),
     url(r'create/', views.create, name='provmanager_create'),
     
     url(r'improve/([-\w]+)', views.improve, name='provmanager_improve'),
     
     url(r'cron_submit/', views.cron_submit, name='provmanager_cron_submit'),
     url(r'mop_submit/', views.mop_submit, name='provmanager_mop_submit'),
        
)
