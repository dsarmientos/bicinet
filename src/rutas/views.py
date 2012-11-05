from django.shortcuts import render_to_response
from django.http import HttpResponse
from rutas.models import Ruta
from django.db import connection, transaction
import ppygis

def home(request):
    rutas = Ruta.objects.all()
    return render_to_response('rutas/home.html', {'rutas': rutas})


def findNearestEdge(latitud, longitud):
    latitudini = float(latitud)
    longitudini = float(longitud)

    latitudinid = latitudini - 0.1
    latitudinit = latitudini + 0.1
    longitudinid = longitudini - 0.1
    longitudinit = longitudini + 0.1

    stringSQL = "SELECT osm_id, source, target, way, ST_Distance(way, ST_GeometryFromText( 'POINT("  + str(latitudini)
    stringSQL = stringSQL + " " + str(longitudini) + ")',4326)) AS dist FROM ways"
    stringSQL = stringSQL + " Where way && setsrid( 'BOX3D("  + str(latitudinid) + " " + str(latitudinit) + ", " + str(longitudinid) + " "
    stringSQL = stringSQL + str(longitudinit) + ")'::box3d, 4326) ORDER BY dist LIMIT 1"
    cursor = connection.cursor()
    cursor.execute(stringSQL)

    fila = cursor.fetchone()
    resultado = {}
    if fila:
        resultado.update(
            {'osmId': fila[0], 'origen': fila[1], 'destino':fila[2]})
    return resultado


def routingExec(request):
    if request.method == 'POST':
        latitudini = request.POST.get('LatIni', '')
        longitudini = request.POST.get('LongIni', '')
        latitudFin = request.POST.get('LatFin', '')
        longitudFin = request.POST.get('LongFin', '')

        arcoIni = findNearestEdge(latitudini, longitudini)
        arcoFin = findNearestEdge(latitudFin, longitudFin)

        metodo = request.POST.get('Metodo', '')
        if metodo == "SPD":
            stringSQL = "SELECT rt.osm_id, ST_AsGeoJSON(ST_Transform(rt.ways,4326)) as geojson, lenght(rt.ways) as lenght, t1.osm_id from ways t1, "
            stringSQL = stringSQL + " (SELECT osm_id, ways from dijkstra_sp_delta('ways'," + str(arcoIni.Origen) + "," 
            stringSQL = stringSQL + str(arcoFin.destino) + ", 0.1 ) as rt where t1.osm_id = rt.osm_id " 

        elif metodo == "SPA":
            stringSQL = "SELECT rt.osm_id, ST_AsGeoJSON(ST_Transform(rt.ways,4326)) as geojson, lenght(rt.ways) as lenght, t1.osm_id from ways t1, "
            stringSQL = stringSQL + " (SELECT osm_id, ways from start_sp_delta('ways'," + str(arcoIni.Origen) + "," 
            stringSQL = stringSQL + str(arcoFin.destino) + ", 0.1 ) as rt where t1.osm_id = rt.osm_id " 

        elif metodo == "SPS":
            stringSQL = "SELECT rt.osm_id, ST_AsGeoJSON(ST_Transform(rt.ways,4326)) as geojson, lenght(rt.ways) as lenght, t1.osm_id from ways t1, "
            stringSQL = stringSQL + " (SELECT osm_id, ways from shootingstar_sp('ways'," + str(arcoIni.Origen) + "," 
            stringSQL = stringSQL + str(arcoFin.destino) + ", 0.1 ) as rt where t1.osm_id = rt.osm_id " 

        if stringSQL != "":
            cursor = connection.cursor()
            cursor.execute(stringSQL)

            for fila in cursor.fetchall():
               resultado.osmId = fila[0]
               resultado.origen = fila[1]
               resultado.destino = fila[2]


