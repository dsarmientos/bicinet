// Start with the map page
window.location.replace(window.location.href.split("#")[0] + "#mappage");

var selectedFeature = null;

// fix height of content
function fixContentHeight() {
    var footer = $("div[data-role='footer']:visible"),
        content = $("div[data-role='content']:visible:visible"),
        viewHeight = $(window).height(),
        contentHeight = viewHeight - footer.outerHeight();

    if ((content.outerHeight() + footer.outerHeight()) !== viewHeight) {
        contentHeight -= (content.outerHeight() - content.height() + 1);
        content.height(contentHeight);
    }

    if (window.map && window.map instanceof OpenLayers.Map) {
        map.updateSize();
    } else {
        // initialize map
        init(function(feature) { 
            selectedFeature = feature; 
            $.mobile.changePage("#popup", "pop"); 
        });
        initLayerList();
    }
}

// one-time initialisation of button handlers 

$("#plus").live('click', function(){
    $.mobile.changePage('#layerspage');
});


$("#locate").live('click',function(){
    
    var control = map.getControlsBy("id", "locate-control")[0];
    if (control.active) {
        control.getCurrentLocation();
    } else {
        control.activate();
    }
});

$('#rutaspage').live('pageshow',function(event, ui){
  $('#calcular_ruta_dir').bind('click', function() {
    var origen = $('#direccion_origen').val()+', bogota';
    var destino = $('#direccion_destino').val()+', bogota';
    var preferencia = $('input[name=preferencia-ruta]:checked', '#preferencias_ruta').val();

    $.mobile.showPageLoadingMsg();
    $.post('/api/rutas/calcular_por_dir/',
	    {'origen': origen, 'destino': destino, 'preferencia': preferencia},
	    function(data) {
	      console.log(data);
	      addRoute(data); 
    $.mobile.hidePageLoadingMsg();
	      $.mobile.changePage('#mappage');}
    );
  });
  $('#rutaspage').die('pageshow', arguments.callee);
});


$('#sitiospage').live('pageshow',function(event, ui){
  $('#buscar_sitios').bind('click', function() {

    var tipo_sitio = "parking";
    var marcador;
    var markerslayer = map.getLayer('Markers');
    if (markerslayer.markers.length > 0) {
        
        marcador = markerslayer.markers[0];
        var lotlang = marcador.lonlat;
        var lotlangWs84 = new OpenLayers.LonLat(lotlang.lon, lotlang.lat).transform (
    		                    new OpenLayers.Projection("EPSG:900913"), // transform from WGS 1984
    	                            new OpenLayers.Projection("EPSG:4326") // to Spherical Mercator Projection
                         );

        var longfloat = lotlangWs84.lon;
        longitud = longfloat.toString();
        var latfloat = lotlangWs84.lat;
        latitud =latfloat.toString();
        
	var preferencia = $("#parqueadero").attr("checked");

	if (( preferencia == "checked") || (preferencia == true)) {
	   tipo_sitio = "parking";
	}
	else {
	   var preferencia = $("#supermercado").attr("checked");       
	   if (( preferencia == "checked") || (preferencia == true)) {
	      tipo_sitio = "marketplace";       
	   }
	   else {
	      tipo_sitio = "hardware_store";       
	   }       
	}

	$.mobile.showPageLoadingMsg();
	$.post('/api/sitios/buscar_por_ubi/',
		    {'latitud': latitud, 'longitud': longitud, 'tipo_sitio': tipo_sitio},
		    function(data) {
		      console.log(data);
		      addPlaces(data); 
	$.mobile.hidePageLoadingMsg();
	$.mobile.changePage('#mappage');}
	    );
     }
     else{
         alert("Debe definir un marcador en la mapa");
     }
  });
  $('#sitiospage').die('pageshow', arguments.callee);
});


$('#sitiospage2').live('pageshow',function(event, ui){
  $('#buscar_sitios2').bind('click', function() {

    var tipo_sitio = "parking";

    var direccion = $('#direccion_sitios').val()+', bogota';
    var preferencia = $("#parqueadero").attr("checked");
    if (( preferencia == "checked") || (preferencia == true)) {
	   tipo_sitio = "parking";
    }
    else {
	var preferencia = $("#supermercado").attr("checked");       
	if (( preferencia == "checked") || (preferencia == true)) {
	    tipo_sitio = "marketplace";       
	}
	else {
	      tipo_sitio = "hardware_store";       
	}       
    }

    $.mobile.showPageLoadingMsg();
    $.post('/api/sitios/buscar_por_dir/',
		    {'direccion': direccion, 'tipo_sitio': tipo_sitio},
		    function(data) {
		      console.log(data);
		      addPlaces(data); 
	$.mobile.hidePageLoadingMsg();
	$.mobile.changePage('#mappage');}
	    );
  });
  $('#sitiospage2').die('pageshow', arguments.callee);
});


//fix the content height AFTER jQuery Mobile has rendered the map page
$('#mappage').live('pageshow',function (){
    fixContentHeight();
});
    
$(window).bind("orientationchange resize pageshow", fixContentHeight);



$('#popup').live('pageshow',function(event, ui){
    var li = "";
    for(var attr in selectedFeature.attributes){
        li += "<li><div style='width:25%;float:left'>" + attr + "</div><div style='width:75%;float:right'>" 
        + selectedFeature.attributes[attr] + "</div></li>";
    }
    $("ul#details-list").empty().append(li).listview("refresh");
});

$('#searchpage').live('pageshow',function(event, ui){
    $('#query').bind('change', function(e){
        $('#search_results').empty();
        if ($('#query')[0].value === '') {
            return;
        }
        $.mobile.showPageLoadingMsg();

        // Prevent form send
        e.preventDefault();

        var searchUrl = 'http://ws.geonames.org/searchJSON?featureClass=P&maxRows=10';
        searchUrl += '&name_startsWith=' + $('#query')[0].value;
        $.getJSON(searchUrl, function(data) {
            $.each(data.geonames, function() {
                var place = this;
                $('<li>')
                    .hide()
                    .append($('<h2 />', {
                        text: place.name
                    }))
                    .append($('<p />', {
                        html: '<b>' + place.countryName + '</b> ' + place.fcodeName
                    }))
                    .appendTo('#search_results')
                    .click(function() {
                        $.mobile.changePage('#mappage');
                        var lonlat = new OpenLayers.LonLat(place.lng, place.lat);
                        map.setCenter(lonlat.transform(gg, sm), 10);
                    })
                    .show();
            });
            $('#search_results').listview('refresh');
            $.mobile.hidePageLoadingMsg();
        });
    });
    // only listen to the first event triggered
    $('#searchpage').die('pageshow', arguments.callee);
});


function initLayerList() {
    $('#layerspage').page();
    $('<li>', {
            "data-role": "list-divider",
            text: "Mapa Base"
        })
        .appendTo('#layerslist');
    var baseLayers = map.getLayersBy("isBaseLayer", true);
    $.each(baseLayers, function() {
        addLayerToList(this);
    });

    $('<li>', {
            "data-role": "list-divider",
            text: "Rutas y Sitios"
        })
        .appendTo('#layerslist');
    var re = /Sitio.*/;
    var overlayLayers = map.getLayersByName(re);
    $.each(overlayLayers, function() {
        addLayerToList(this);
    });
    $('#layerslist').listview('refresh');
    
    map.events.register("addlayer", this, function(e) {
        addLayerToList(e.layer);
    });
}

function addLayerToList(layer) {
    var item = $('<li>', {
            "data-icon": "check",
            "class": layer.visibility ? "checked" : ""
        })
        .append($('<a />', {
            text: layer.name
        })
            .click(function() {
                $.mobile.changePage('#mappage');
                if (layer.isBaseLayer) {
                    layer.map.setBaseLayer(layer);
                } else {
                    layer.setVisibility(!layer.getVisibility());
                }
            })
        )
        .appendTo('#layerslist');
    layer.events.on({
        'visibilitychanged': function() {
            $(item).toggleClass('checked');
        }
    });
}
