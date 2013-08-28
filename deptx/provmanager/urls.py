from django.conf.urls import patterns, url

from provmanager import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='provmanager_index'),
     url(r'view/(\d+)', views.view, name='provmanager_view'),
     url(r'create/', views.create, name='provmanager_create'),
         
)
