from django.conf.urls import patterns, url

from gamecity import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='gamecity_index'),
)


