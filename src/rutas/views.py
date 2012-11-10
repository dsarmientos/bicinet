from django.shortcuts import render_to_response
from django.http import HttpResponse
from rutas.models import Ruta
from django.db import connection, transaction
import ppygis

def home(request):
    rutas = Ruta.objects.all()
    return render_to_response('rutas/home.html', {'rutas': rutas})


def findNearestEdge(latitud, longitud):


    stringSQL = "select ST_X(ST_Transform(ST_GeomFromText('POINT(" + longitud + " " +  latitud + " )', 4326), 900913))"
    cursor = connection.cursor()
    cursor.execute(stringSQL)
    fila = cursor.fetchone()
    longitudini = fila[0]
   
    stringSQL = "select ST_Y(ST_Transform(ST_GeomFromText('POINT(" + longitud + " " +  latitud + " )', 4326), 900913))"
    cursor = connection.cursor()
    cursor.execute(stringSQL)
    fila = cursor.fetchone()
    latitudini = fila[0]

    latitudinid = latitudini - 0.01
    latitudinit = latitudini + 0.01
    longitudinid = longitudini - 0.01
    longitudinit = longitudini + 0.01

    stringSQL = "SELECT osm_id, source, target, way, ST_Distance(way, ST_GeometryFromText( 'POINT("  + str(longitudini)
    stringSQL = stringSQL + " " + str(latitudini) + ")',900913)) AS dist FROM ways ORDER BY dist LIMIT 1"
    cursor = connection.cursor()
    cursor.execute(stringSQL)

    print(stringSQL)

    fila = cursor.fetchone()
    resultado = {}

    if fila:
         resultado.update({'osmId': fila[0], 'origen': fila[1], 'destino':fila[2]})  
    else:
         resultado.update({'osmId': -1, 'origen': -1, 'destino': -1 })

    return resultado


def routingExec(latIni, longIni, latFin, longFin, metodo ):
    
    arcoIni = findNearestEdge(latIni, longIni)
    arcoFin = findNearestEdge(latFin, longFin)

    print arcoIni
    print arcoFin

    if metodo == "SPD":
        stringSQL = "SELECT rt.osm_id, ST_AsGeoJSON(rt.ways) as geojson, lenght(rt.ways) as lenght, t1.osm_id, t1.name from ways t1, "
        stringSQL = stringSQL + " (SELECT osm_id, ways from dijkstra_sp_delta('ways'," + str(arcoIni["origen"]) + "," 
        stringSQL = stringSQL + str(arcoFin["destino"]) + ", 0.1 ) as rt where t1.osm_id = rt.osm_id " 

    elif metodo == "SPA":
        stringSQL = "SELECT rt.osm_id, ST_AsGeoJSON(rt.ways) as geojson, lenght(rt.ways) as lenght, t1.osm_id, t1.name from ways t1, "
        stringSQL = stringSQL + " (SELECT osm_id, ways from start_sp_delta('ways'," + str(arcoIni["origen"]) + "," 
        stringSQL = stringSQL + str(arcoFin["destino"]) + ", 0.1 ) as rt where t1.osm_id = rt.osm_id " 

    elif metodo == "SPS":
        stringSQL = "SELECT rt.osm_id, ST_AsGeoJSON(rt.ways) as geojson, lenght(rt.ways) as lenght, t1.osm_id, t1.name from ways t1, "
        stringSQL = stringSQL + " (SELECT osm_id, ways from shootingstar_sp('ways'," + str(arcoIni["origen"]) + "," 
        stringSQL = stringSQL + str(arcoFin["destino"]) + ", 0.1 ) as rt where t1.osm_id = rt.osm_id " 

    print stringSQL
    if stringSQL != "":
        cursor = connection.cursor()
        cursor.execute(stringSQL)

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
            crs = {}
            crs.update({'type': 'EPSG' })
            crs.update({'properties': {'code' : '900913' } } )

            properties = {}
            properties.update({'id': fila[0]})
            properties.update({'length': fila[2]})

            if ( fila[4] is not None ) and ( len(fila[4]) > 0 ):
                 properties.update({'nombre': fila[4]})
            else:
                 properties.update({'nombre': ' ' })

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
        
    else:

        resultado = {}
        resultado.update({'type': 'FeatureCollection'})
        resultado.update({'Encontrado': 'False'})

    return json.dumps(resultado)

