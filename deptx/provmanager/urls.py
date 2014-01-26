from django.conf.urls import patterns, url

from provmanager import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='provmanager_index'),
     url(r'view/(\d+)/$', views.view, name='provmanager_view'),
     url(r'view/(\d+)/randomize', views.view_randomize, name='provmanager_view_randomize'),
     url(r'convert/(\d+)', views.convert, name='provmanager_convert'),
     url(r'create/', views.create, name='provmanager_create'),
     
     url(r'improve/(\w+)/$', views.improve, name='provmanager_improve'),
     url(r'improve/(\w+)/state', views.improve_saved_state, name='provmanager_improve_saved_state'),
     
     url(r'prov_check/', views.prov_check, name='provmanager_prov_check'),
     url(r'prov_log_action/', views.prov_log_action, name='provmanager_prov_log_action'),

     url(r'export/(?P<user_id>\d+).(?P<ext>provn|json)', views.provexport),
)
