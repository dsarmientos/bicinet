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


def calcular_ruta(request):
    latitud_i = request.GET['latitud_i']
    longitud_i = request.GET['longitud_i']
    latitud_f = request.GET['latitud_f']
    longitud_f = request.GET['longitud_f']
    ruta = json.dumps(
        geo.routingExec(longitud_i, latitud_i, longitud_f, latitud_f))
    response = HttpResponse(ruta, content_type="application/json")
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With'
    return response


def crear_ruta(request):
    response = HttpResponse('%s' % request.POST, content_type="application/json")
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With'
    return response

def calcular_ruta_por_dir(request):
    origen = request.POST['direccion_origen']
    destino = request.POST['direccion_destino']
    ruta = json.dumps(
        geo.routingExec(longitud_i, latitud_i, longitud_f, latitud_f))
    response = HttpResponse(ruta, content_type="application/json")
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With'
    return response


