/*
Spatial Facet App (c) 2021 M. Werner 
MIT License

*/


var U= 0;



function createPolygonFromBounds(latLngBounds) {
       var center = latLngBounds.getCenter()
       latlngs = [];
       latlngs.push(latLngBounds.getSouthWest());//bottom left
       latlngs.push(latLngBounds.getSouthEast());//bottom right
       latlngs.push(latLngBounds.getNorthEast());//top right
       latlngs.push(latLngBounds.getNorthWest());//top left
       return L.polygon(latlngs);
}

function setFacetToView()
{
    zoom = map.getZoom();
    map.setView(map.getCenter(), zoom+1, {
	"animate": false,
	"pan": {
	    "duration": 0
	}}
    );
    
     if(typeof poly !== "undefined")
     {
	   poly.remove()
     }
     poly = createPolygonFromBounds(map.getBounds()).addTo(map)
     poly.enableEdit();
    poly.on('dblclick', L.DomEvent.stop).on('dblclick', poly.toggleEdit);
        map.setView(map.getCenter(), zoom, {
	"animate": false,
	"pan": {
	    "duration": 0
	}}
    );

}


const query = function(){
       $.ajax({
	   url:"/query",
	   type:"POST",
	   data:JSON.stringify({"query":$("#query").val()}),
	   contentType:"application/json; charset=utf-8",
	   dataType:"json",
	   success: function(data){
	       console.log(data)
	       message =`Estimated Matches: ${data["result"]["num_matches"]}<br/><ul>`
	       rd = data["result"]["data"];  // rd ^= result data
	       for (i=0; i < rd.length; i++){
		   d = JSON.parse(rd[i]);
		   message +=`<li>${d["text"]}</li>`
	       }
	       
	       message +="<ul>" 
	       $("#proposed_keywords").html(message)
	       
	       
	   }});
}


const supervised_facet = function(){
       $.ajax({
	   url:"/supervised_facet",
	   type:"POST",
	   data:JSON.stringify({"query":$("#query").val(), "poly": poly.toGeoJSON()}),
	   contentType:"application/json; charset=utf-8",
	   dataType:"json",
	   success: function(data){
	       console.log(data["aug_keywords"])
	       var the_text ="Facet Proposals:<br/><ul>"
              data["aug_keywords"].forEach( function(element)
                                            {
                                                weight = element[1].toFixed(2);
                                                kw = element[0]
                                                the_text += `<li>${weight}: ${element[0]}</li>`
                                            })
              the_text += "</ul>"

              $("#proposed_keywords").html(the_text) //("lala" + data["aug_keywords"]);
          }
       })
       console.log('planning')
}

var map=undefined;

/// INIT FUNCTIONALITY MAIN
$(function() {
  // This is the recommended form of .ready() handling.
    var startPoint = [52.1249, 11.5];
    var startLine = [[48.142838,11.527362],[48.140833,11.55427]];
    map = L.map('map', {editable: true}).setView(startPoint, 6),
    tilelayer = L.tileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {maxZoom: 20, attribution: 'Data \u00a9 <a href="http://www.openstreetmap.org/copyright"> OpenStreetMap Contributors </a> Tiles \u00a9 HOT'}).addTo(map);
});

