import json

from django.http import HttpResponse

import geo.views as geo


def sitios_cerca(request):
    latitud = request.GET['latitud']
    longitud = request.GET['longitud']
    tipo_sitio = 'parking'
    radio = '0.01'
    sitios = json.dumps(
        geo.findNearestSites(latitud, longitud, tipo_sitio, radio))

    response = HttpResponse(sitios, content_type="application/json")
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With'
    return response
