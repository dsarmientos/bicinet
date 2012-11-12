import json

from django.shortcuts import render_to_response
from django.http import HttpResponse
from rutas.models import Ruta
from django.db import connection, transaction

import ppygis

def home(request):
    rutas = Ruta.objects.all()
    return render_to_response('rutas/home.html', {'rutas': rutas})


def findNearestEdge(longitud, latitud):
    tol= 0.001
    latitud_inf, longitud_inf = latitud -tol, longitud - tol
    latitud_sup, longitud_sup = latitud + tol, longitud + tol
    stringSQL = """SELECT osm_id, source, target, geom_way,
                    ST_Distance(geom_way,
                    ST_GeometryFromText('POINT(%s %s)', 4326)) AS dist, id
                    FROM osm_2po_4pgr
                    WHERE  geom_way && setsrid('BOX3D(%s %s, %s %s)'::box3d, 4326)
                    ORDER BY dist LIMIT 1"""
    parametrosSQL = (longitud, latitud, longitud_inf, latitud_inf, longitud_sup,
                     latitud_sup)
    columnas = ('osmId', 'origen', 'destino', 'id')
    resultado = {}

    cursor = connection.cursor()
    cursor.execute(stringSQL, parametrosSQL)
    fila = cursor.fetchone()
    cursor.close()
    if fila:
        resultado = dict(zip(columnas, (fila[0], fila[1], fila[2], fila[5])))
    return resultado


def routingExec(longIni, latIni, longFin, latFin):
    arcoIni = findNearestEdge(longIni, latIni)
    arcoFin = findNearestEdge(longFin, latFin)
    stringSQL =  """
        SELECT rd.osm_id, ST_AsGeoJSON(ST_Transform(rd.the_geom,900913)) as geojson, rt.cost as cost, rd.name
        FROM osm_2po_4pgr t1,
            (SELECT vertex_id, cost
             FROM shortest_path('
                     SELECT osm_id AS id,
                        source::int4,
                        target::int4,
                        cost_seg as cost
                     FROM osm_2po_4pgr',
                     %s, %s, false, false))
            as rt, roads rd
        WHERE rt.vertex_id = t1.source
            AND rd.osm_id = t1.osm_id"""
    parametrosSQL = (arcoIni['origen'], arcoFin['destino'])
    cursor = connection.cursor()
    cursor.execute(stringSQL, parametrosSQL)
    # Defino el resultado como diccionario
    resultado = {}
    resultado.update({'type': 'FeatureCollection'})
    features = []
    segmentos = 0

    for fila in cursor.fetchall():
        feature = {}
        feature.update({'type': 'Feature'})
        feature.update({'geometry': json.loads(fila[1]) })

        # construye el arreglo que especifica la proyeccion en la que vienen los datos
        crs = {
            'type': 'EPSG',
            'properties': {'code':'900913'},
        }
        nombre = fila[3] if fila[3] else ''
        properties = {
            'id': fila[0],
            'length': fila[2],
            'nombre': nombre,
        }

        feature.update({'crs': crs } )
        feature.update({'properties' : properties})
        features.append(feature)
        # El elemento features es a la vez un diccionario
        resultado.update({'features': features } )
        segmentos = segmentos + 1

    if segmentos == 0:
        resultado.update({'Encontrado': 'False'})
    else:
        resultado.update({'Encontrado': 'True'})

    return json.dumps(resultado)

