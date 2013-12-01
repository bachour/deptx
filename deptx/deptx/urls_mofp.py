from django.conf.urls import patterns, include, url
from django.conf import settings

handler404 = 'mop.views.custom_404_view'
handler500 = 'mop.views.custom_500_view'

urlpatterns = patterns('',
    url(r'^', include('mop.urls')),
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
