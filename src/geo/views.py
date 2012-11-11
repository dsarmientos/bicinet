import json

from django.db import connection, transaction


def findNearestSites(latitud, longitud, tipoSitio, radio):
    latitudini = float(latitud)
    longitudini = float(longitud)
    radioN = float(radio)

    stringSQL = "SELECT osm_id, type, name, ST_AsGeoJSON(ST_Transform(the_geom,900913))"
    stringSQL = stringSQL + " " + "FROM points"
    stringSQL = stringSQL + " " + "WHERE ST_Within(the_geom, ST_buffer(ST_GeomFromText('POINT(" + str(longitudini)
    stringSQL = stringSQL + " " + " " + str(latitudini) + ")', 4326) , " + str(radioN) + " , 'quad_segs=4'))"
    stringSQL = stringSQL + " " + " AND type = '" + tipoSitio + "'"

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
