$(document).ready(function() {
    initiate_geolocation();
});

function initiate_geolocation() {  
    navigator.geolocation.getCurrentPosition(handle_geolocation_query);  
}  


function handle_geolocation_query(position){  
    var lat = position.coords.latitude;
    var lon = position.coords.longitude;
    init(lat, lon);
}  


function init(latitud, longitud) {
    //set up projections
    
    // World Geodetic System 1984 projection (lon/lat)
    var WGS84 = new OpenLayers.Projection("EPSG:4326");
    
    // WGS84 Google Mercator projection (meters)
    var WGS84_google_mercator = new OpenLayers.Projection("EPSG:900913");
    
    //Initialize the map
    
    //creates a new openlayers map in
    //the <div> html element with id="map"
    var map = new OpenLayers.Map ("map", {
    
    allOverlays: true,
    
    
    controls:[
    //allows user pan/zoom ability
    new OpenLayers.Control.Navigation(),
    
    //displays the pan/zoom tools
    new OpenLayers.Control.PanZoom(),
    
    //displays a layer switcher
    new OpenLayers.Control.LayerSwitcher(),
    
    //displays the mouse positions coordinates in a
    //<div> html element with id coordinates
    new OpenLayers.Control.MousePosition({
    div:document.getElementById("coordinates")
    
    })
    ],
    projection: WGS84_google_mercator,
    displayProjection: WGS84
    } );
    
    
    // Esto que sigue debe llevarse a una función, en la cual se establece el zoom adecuado para un usuario
    
    // Encontramos el punto en el cual esta el usuario por el GPS o se le coloca un defecto en el usuario
    var precision = 0.01
    
    var latIni = latitud - precision
    var latFin = latitud + precision
    var longIni = longitud - precision
    var longFin = longitud + precision
    
    
    
    var Bogota = new OpenLayers.Bounds( longIni, latIni, longFin, latFin).transform(WGS84, map.getProjectionObject());
    
    var openstreetmap = new OpenLayers.Layer.OSM();
    
    
    var overview = new OpenLayers.Control.OverviewMap({mapOptions: {
    		   projection: new OpenLayers.Projection("EPSG:900913"),
    		   units: "m",
    		   maxExtent: Bogota,
    		   restrictedExtent: Bogota,
    		   maxResolution: 22,
    		   numZoomLevels: 5
    		  }
    		});
    
    map.addControl(overview);
    
    map.addLayer(openstreetmap);
    var mapextent = new OpenLayers.Bounds(longIni, latIni, longFin, latFin).transform(WGS84, map.getProjectionObject());
    
    $.get('/api/sitios/cerca/',
    	   {latitud:latitud,longitud:longitud},
    	   function(data, textStatus, jqXHR) {     
    		add_layers(map, data);
    	});
    map.zoomToExtent(mapextent);

}

function add_layers(map, featurecollection) {
        var geojson_format = new OpenLayers.Format.GeoJSON();

        var renderer = OpenLayers.Util.getParameters(window.location.href).renderer;
        renderer = (renderer) ? [renderer] : OpenLayers.Layer.Vector.prototype.renderers;

        var vector_layer = new OpenLayers.Layer.Vector("Sitios Cercanos", {
		                styleMap: new OpenLayers.StyleMap({'default':{
		                    strokeColor: "#00FF00",
		                    strokeOpacity: 1,
		                    strokeWidth: 3,
		                    fillColor: "#0000FF",
		                    fillOpacity: 0.5,
		                    pointRadius: 10,
		                    label : "${nombre}",
		                    pointerEvents: "visiblePainted",
		                    fontColor: "red",
		                    fontSize: "12px",
		                    fontFamily: "Courier New, monospace",
		                    fontWeight: "bold",
		                    labelAlign: "cm",
		                    labelOutlineColor: "white",
		                    labelOutlineWidth: 3
		                }}),
		                renderers: renderer
            });



        vector_layer.addFeatures(geojson_format.read(featurecollection));
        map.addLayer(vector_layer);


}

