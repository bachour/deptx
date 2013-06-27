from django.conf.urls import patterns, url

from testGround import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)