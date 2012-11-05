# Create your views here.

def findNearSites(latitud, longitud, tipoSitio):

    latitudini = float(latitud)
    longitudini = float(longitud)


    stringSQL = "SELECT osm_id, amenity, name, way"
    stringSQL = stringSQL + " " + "FROM planet_osm_point" 
    stringSQL = stringSQL + " " + "ST_Within(way, ST_Buffer(ST_Transform(ST_GeomFromText('POINT(" + str(longitudini) 
    stringSQL = stringSQL + " " + " " + str(latitudini) + ")', 4326), 900913), 500, 'quad_segs=4')"
    stringSQL = stringSQL + " " + " amenity = '" + tipoSitio + "'"

    cursor = connection.cursor()
    cursor.execute(stringSQL)

