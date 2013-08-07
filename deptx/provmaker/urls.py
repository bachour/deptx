from django.conf.urls import patterns, url

from provmaker import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='provmaker_index'),
    url(r'provenance/(\d+)', views.provenance, name='provmaker_provenance'),
    url(r'example/(\d+)', views.example, name='provmaker_example'),

)