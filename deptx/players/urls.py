from django.conf.urls import patterns, url

from players import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name='cron_index'),
    url(r'registration/', views.register, name='player_registration'),
)

