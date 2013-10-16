from django.conf.urls.defaults import *
from django.http import HttpResponseNotFound

from dummyimage import views

WIDTH_RE = r'(?P<width>\d+)'
HEIGHT_RE = r'(?P<height>\d+)'
FORMAT_RE = r'(?P<format>[a-z]{3})'
IMAGE_RE = r'^%sx%s\.%s$' % (WIDTH_RE, HEIGHT_RE, FORMAT_RE)

#urlpatterns = patterns('dummyimage.views',
#    (IMAGE_RE, 'render_image'),
#)
urlpatterns = patterns('',
    url(r'^$', views.faker, name='dummyimage_base_url'),
    url(r'(\d+)/(\d+)/([-\w]+)', views.render_image, name='dummyimage_render_image'),
)




def view404(request):
    return HttpResponseNotFound()


handler404 = view404
