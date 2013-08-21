from django.conf.urls import patterns, url

from players import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='players_index'),
    url(r'registration/', views.register, name='players_registration'),
)


