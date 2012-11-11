from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^$', direct_to_template, {
                'template': 'index.html'
                    }, name='home'),

    url(r'^rutas/$', 'rutas.views.home', name='home_rutas'),

    url(r'^sitios/buscador/$', 'sitios.views.buscador', name='sitios_buscador'),

    url(r'^api/sitios/cerca/$', 'api.views.sitios_cerca', name='api_sitios_cerca'),

    url(r'^admin/', include(admin.site.urls)),
)


from django.conf import settings
## debug stuff to serve static media
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':
                '/home/daniel/bicinet/static/'}),
   )

