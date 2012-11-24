from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^$', direct_to_template, {
                'template': 'index.html'
                    }, name='home'),

    url('^geotest/$', direct_to_template, {
                'template': 'geo.html'
                    }, name='geo'),

    url(r'^users/login/$', 'users.views.login', name='login'),
    url(r'^rutas/$', 'rutas.views.home', name='home_rutas'),

    url('^sitios/mapa/$', direct_to_template, {
                'template': 'sitios/mapa.html'
                    }, name='sitios_mapa'),

    url(r'^api/sitios/cerca/$', 'api.views.sitios_cerca', name='api_sitios_cerca'),
    url(r'^api/rutas/calcular/$', 'api.views.calcular_ruta',
        name='api_rutas_calcular'),
    url(r'^api/rutas/calcular_por_dir/$', 'api.views.calcular_ruta_por_dir',
        name='api_rutas_calcular_por_dir'),
    url(r'^api/rutas/crear/$', 'api.views.crear_ruta', name='api_rutas_crear'),
    url(r'^api/sitios/buscar_por_dir/$', 'api.views.sitios_por_dir',
        name='api_sitios_buscar_por_dir'),

    url(r'^api/sitios/buscar_por_ubi/$', 'api.views.tipo_sitio_cerca',
        name='api_tipo_sitio_buscar_por_ubi'),


    url(r'^admin/', include(admin.site.urls)),
)


from django.conf import settings
## debug stuff to serve static media
if settings.DEBUG is True:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':
                '/home/luis/bicinet/static/'}),
   )

