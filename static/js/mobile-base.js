// initialize map when page ready
var map;
var gg = new OpenLayers.Projection("EPSG:4326");
var sm = new OpenLayers.Projection("EPSG:900913");

var init = function (onSelectFeatureFunction) {

    var vector = new OpenLayers.Layer.Vector("Vector Layer", {});

    var sitiosLayer = new OpenLayers.Layer.Vector("Sitios", {
       	    styleMap: new OpenLayers.StyleMap({
            externalGraphic: "/static/img/parking-marker.png",
            graphicOpacity: 1.0,
            graphicWidth: 16,
            graphicHeight: 26,
            graphicYOffset: -26
          })
      });

     $.getJSON('/api/sitios/cerca/',
    	       {latitud:4.6027189,longitud:-74.065304},
       	       function(data, textStatus, jqXHR) {     
		   addSites(sitiosLayer, data, onSelectFeatureFunction);
               }
    );

    var openstreetmap = new OpenLayers.Layer.OSM();

    var geolocate = new OpenLayers.Control.Geolocate({
        id: 'locate-control',
        geolocationOptions: {
            enableHighAccuracy: false,
            maximumAge: 0,
            timeout: 7000
        }
    });
    // create map
    map = new OpenLayers.Map({
        div: "map",
        theme: null,
        projection: sm,
        numZoomLevels: 20,
        controls: [
            new OpenLayers.Control.Attribution(),
            new OpenLayers.Control.TouchNavigation({
                dragPanOptions: {
                    enableKinetic: true
                }
            }),
            geolocate,
        ],
        layers: [
            new OpenLayers.Layer.Google("Google Streets", {numZoomLevels: 20}),
	    openstreetmap,
            vector,
            sitiosLayer,
        ],
        center: new OpenLayers.LonLat(74.065304, 4.602718),
        zoom: 10
    });

    var style = {
        fillOpacity: 0.1,
        fillColor: '#000',
        strokeColor: '#f00',
        strokeOpacity: 0.6
    };
    geolocate.events.register("locationupdated", this, function(e) {
        vector.removeAllFeatures();
        vector.addFeatures([
            new OpenLayers.Feature.Vector(
                e.point,
                {},
                {
                    graphicName: 'cross',
                    strokeColor: '#f00',
                    strokeWidth: 2,
                    fillOpacity: 0,
                    pointRadius: 10
                }
            ),
            new OpenLayers.Feature.Vector(
                OpenLayers.Geometry.Polygon.createRegularPolygon(
                    new OpenLayers.Geometry.Point(e.point.x, e.point.y),
                    e.position.coords.accuracy / 2,
                    50,
                    0
                ),
                {},
                style
            )
        ]);
        map.zoomToExtent(vector.getDataExtent());
    	var param = {latitud:e.position.coords.latitude,longitud:e.position.coords.longitude};
        $.getJSON('/api/sitios/cerca/', param,
       	       function(data, textStatus, jqXHR) {     
		   addNearSites(sitiosLayer, data);
               }
        );
    });
    activateMarkers();

    function readFeatures(features) {
        var reader = new OpenLayers.Format.GeoJSON();
        return reader.read(features);
    }
    
    function addSites(sitiosLayer, sitios, onSelectFeatureFunction) {
      var features = readFeatures(sitios);
      sitiosLayer.addFeatures(features);
      var selectControl = new OpenLayers.Control.SelectFeature(sitiosLayer, {
        autoActivate:true,
        onSelect: onSelectFeatureFunction});
      map.addLayer(sitiosLayer);
      map.addControl(selectControl);
      map.zoomToExtent(sitiosLayer.getDataExtent());
   }
    
   

   function addNearSites(sitiosLayer, sitios) {
      var features = readFeatures(sitios);
      sitiosLayer.addFeatures(features);
   }


};

var addRoute = function(route) {
      var reader = new OpenLayers.Format.GeoJSON();
      var features = reader.read(route);
      var routeLayer = new OpenLayers.Layer.Vector("Ruta", {
       	    styleMap: new OpenLayers.StyleMap({
	    strokeColor: "#663300",
	    strokeOpacity: 1,
	    strokeWidth: 3,
	    fillColor: "#663300",
	    fillOpacity: 0.5,
          })
      });
      routeLayer.addFeatures(features);
      map.addLayer(routeLayer);
      map.zoomToExtent(routeLayer.getDataExtent());
};


var addPlaces = function(sites) {
      var reader = new OpenLayers.Format.GeoJSON();
      var features = reader.read(sites);
      var StyleSitios = new OpenLayers.StyleMap(OpenLayers.Util.applyDefaults(
        {fillColor: "green", fillOpacity: 1, strokeColor: "black"},
        OpenLayers.Feature.Vector.style["default"]));

      var SitiosLayer = new OpenLayers.Layer.Vector("Sitios", { styleMap: StyleSitios});
        
      SitiosLayer.addFeatures(features);
      map.addLayer(SitiosLayer);
      map.zoomToExtent(SitiosLayer.getDataExtent());
};
   
    
var activateMarkers = function() {
   var markers = new OpenLayers.Layer.Markers( "Markers" );
   markers.id = "Markers";
   map.addLayer(markers);
   var arrayMarkers = []

   map.events.register("click", map, function(e) {
             var position = this.events.getMousePosition(e);
             var position = map.getLonLatFromPixel(e.xy);
             var size = new OpenLayers.Size(21,25);
             var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
             var icon = new OpenLayers.Icon('/static/img/bike-marker.png', size, offset);
             var markerslayer = map.getLayer('Markers');
             var marker = new OpenLayers.Marker(position,icon);
             if (arrayMarkers.length < 2)
             {
                 arrayMarkers.push(marker);
                 markerslayer.addMarker(marker);
             }
             else
             {
                 markertoRemove = arrayMarkers.shift();
                 markerslayer.removeMarker(markertoRemove);
                 arrayMarkers.push(marker);
                 markerslayer.addMarker(marker);
             }
        });
}
