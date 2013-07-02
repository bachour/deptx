from django.conf.urls import patterns, url

from mop import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='mop_index'),
    url(r'login/', views.login, name='mop_login'),
)