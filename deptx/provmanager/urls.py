from django.conf.urls import patterns, url

from provmanager import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='provmanager_index'),
     url(r'view/(\d+)', views.view, name='provmanager_view'),
     url(r'convert/(\d+)', views.convert, name='provmanager_convert'),
     url(r'create/', views.create, name='provmanager_create'),
     
     url(r'improve/([-\w]+)', views.improve, name='provmanager_improve'),
     
     url(r'prov_check/', views.prov_check, name='provmanager_prov_check'),
             
)
