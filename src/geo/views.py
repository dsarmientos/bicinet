import json
import urllib
import urllib2

from django.db import connection, transaction
from django.core.cache import cache


def findNearestSites(latitud, longitud, tipo, radio):
    latitudini = float(latitud)
    longitudini = float(longitud)
    radioN = float(radio)

    stringSQL = "SELECT osm_id, type, name, ST_AsGeoJSON(ST_Transform(the_geom,900913))"
    stringSQL = stringSQL + " " + "FROM points"
    stringSQL = stringSQL + " " + "WHERE ST_Within(the_geom, ST_buffer(ST_GeomFromText('POINT(" + str(longitudini)
    stringSQL = stringSQL + " " + " " + str(latitudini) + ")', 4326) , " + str(radioN) + " , 'quad_segs=4'))"
    stringSQL += " " + " AND (type = '" + tipo + "' OR type ilike '%%bicycle%%' "
    stringSQL += "OR type='fuel')"

    cursor = connection.cursor()
    cursor.execute(stringSQL)

    # Defino el resultado como diccionario
    resultado = {}
    resultado.update({'type': 'FeatureCollection'})

    features = []

    for fila in cursor.fetchall():
         feature = {}
         feature.update({'type': 'Feature'})
         feature.update({'geometry': json.loads(fila[3]) })

         # construye el arreglo que especifica la proyeccion en la que vienen los datos
         crs = {}
         crs.update({'type': 'EPSG' })
         crs.update({'properties': {'code' : '900913' } } )

         properties = {}
         properties.update({'id': fila[0]})
         properties.update({'tipo': fila[1]})

         if ( fila[2] is not None ) and ( len(fila[2]) > 0 ):
              properties.update({'nombre': fila[2]})
         else:
              properties.update({'nombre': ' ' })
         feature.update({'crs': crs } )
         feature.update({'properties' : properties})
         features.append(feature)
    # El elemento features es a la vez un diccionario
    resultado.update({'features': features } )
    return resultado


def findNearestEdge(longitud, latitud):
    key_ = '%s:%s' % (longitud, latitud)
    edge = cache.get(key_)
    if edge is not None: return edge
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
    cache.set(key_, resultado)
    return resultado


def routingExec(longIni, latIni, longFin, latFin, preferencia):
    longIni = float(longIni)
    latIni = float(latIni)
    longFin = float(longFin)
    latFin = float(latFin)
    arcoIni = findNearestEdge(longIni, latIni)
    arcoFin = findNearestEdge(longFin, latFin)
    cost_column = 'cost_seg'
    if preferencia == 'distancia':
        cost_column = 'cost'
    key_ = '%s:%s:%s' % (arcoIni, arcoFin, cost_column)
    route = cache.get(key_)
    if route is not None: return route
    stringSQL =  """
        SELECT rd.osm_id, ST_AsGeoJSON(ST_Transform(rd.the_geom,900913)) as geojson, rt.cost as cost, rd.name
        FROM osm_2po_4pgr t1,
            (SELECT vertex_id,edge_id,  cost
             FROM shortest_path('
                     SELECT id AS id,
                        source::int4,
                        target::int4,
                        %s as cost""" % cost_column
    stringSQL += """ FROM osm_2po_4pgr',
                     %s, %s, false, false))
            as rt, roads rd
        WHERE rt.edge_id = t1.id
            AND rd.osm_id = t1.osm_id"""
    parametrosSQL = (arcoIni['origen'], arcoFin['destino'])
    cursor = connection.cursor()
    cursor.execute(stringSQL, parametrosSQL)
    # Defino el resultado como diccionario
    resultado = {'type': 'FeatureCollection'}
    features = []
    segmentos = 0

    for fila in cursor.fetchall():
        feature = {'type': 'Feature'}
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
    if not segmentos:
        resultado = {'error': 'No se pudo encontrar una ruta'}
    cache.set(key_, resultado)

    return resultado


def geocode(address):
    address = urllib.quote_plus(address)
    url = ("http://maps.googleapis.com/maps/api/geocode/json?"
          "address=%s&sensor=true&components=country:CO") % (address,)
    request = urllib2.urlopen(url)
    response = request.read()
    request.close()
    resDiccionario = json.loads(response)
    location = {'error': True}
    if resDiccionario["status"] == "OK":
        vecResults = resDiccionario["results"]
        geometria = vecResults[0]["geometry"]
        location = geometria["location"]
    return location
