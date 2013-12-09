from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'deptx.views.index', name='deptx_index'),
    # url(r'^deptx/', include('deptx.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^cron/', include('cron.urls')),
    url(r'^mop/', include('mop.urls')),
    url(r'^control/mop/', include('mop.urls_control')),
    url(r'^control/cron/', include('cron.urls_control')),
    url(r'^provmanager/', include('provmanager.urls')),
    
)

# Static and Media files

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s/(?P<path>.*)$'  % settings.MEDIA_URL.strip('/'),
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT,
             'show_indexes': True}),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s/(?P<path>.*)$'  % settings.STATIC_URL.strip('/'),
            'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT,
             'show_indexes': True}),
    )
