// 20171216

angular.module('mmserver_app', [])
.controller('mmserver_controller', function($scope, $http, $location, $interval, $sce, $timeout, $log) {

//serverurl = 'http://127.0.0.1:5010'
//serverurl = $location.absUrl(); //with port
serverurl = 'http://' + $location.host() + ':5010'
console.log('serverurl:' + serverurl)

$scope.username = 'public'

$scope.maps = ''
$scope.selectedMap = ''

$scope.loadedMap = ''

$scope.sessions = null;
$scope.selectedSession = 0; //corresponds to all

$scope.mapsegments = null
$scope.selectedMapSegment = 0 // corresponds to all

var xydata = null;

$scope.userClickStackIndex = null
$scope.userClickSessionIndex = null
$scope.userClickMapSegment = null

$scope.statList = {
	'1': 'session',
	'2': 'x',
	'3': 'y',
	'4': 'z',
	'5': 'pDist',
	'6': 'ubssSum_int2',
	'7': 'ubsdSum_int2',
}
$scope.xStatSelection = 'ubsdSum_int2'
$scope.yStatSelection = 'ubssSum_int2'

$scope.setSelecetedMap = function(map) {
	//console.log('setSelecetedMap():' + map)
	$scope.selectedMap = map
}

$scope.setSelectedStat = function(xy, stat){
	//console.log('setSelectedStat()' + xy + stat)
	if (xy == 'x') {
		$scope.xStatSelection = stat;
		//console.log('$scope.xStatSelection:' + $scope.xStatSelection)
	} else {
		$scope.yStatSelection = stat;
		//console.log('$scope.yStatSelection:' + $scope.yStatSelection)
	}
	if (xydata != null) {
		myplot0()
	}
}

$scope.setSelectedSession = function(index){  //function that sets the value of selectedSession to current index
	//console.log('setSelectedSession()')
	// index==0 is 'All', others are index-1 for 0 based session
	$scope.selectedSession = index;
	//console.log('$scope.selectedSession:' + $scope.selectedSession)
	if (xydata != null) {
		myplot0()
	}
}

$scope.setSelectedMapSegment = function(index){  //function that sets the value of selectedSession to current index
	//console.log('setSelectedMapSegment()')
	// index==0 is 'All', others are index-1 for 0 based session
	$scope.selectedMapSegment = index;
	//console.log('$scope.selectedMapSegment:' + $scope.selectedMapSegment)
	if (xydata != null) {
		myplot0()
	}
}

//var selectMapDropdown = document.getElementById('selectMapDropdownID');
var loadMapButton = document.getElementById('loadMapButtonID');
//var plotButton = document.getElementById('plotButtonID');
var dotSize = document.getElementById('dotSize');

//var sessionList = document.getElementById('sessionListID');

loadMapButton.addEventListener('click', function() {
	loadMap($scope.selectedMap);
});

//plotButton.addEventListener('click', function() {
//	myplot0()
//});

function myplot0() {
	if ($scope.selectedMapSegment == 0) {
		theMapSegment = null // all map segments
	} else {
		theMapSegment = $scope.selectedMapSegment - 1
	}
	if ($scope.selectedSession == 0) {
		theSession = null // all sessions
	} else {
		theSession = $scope.selectedSession - 1
	}
	getMapValues(theMapSegment, theSession, $scope.xStatSelection, $scope.yStatSelection, 'z')
}

// Add handling for marker size selection
dotSize.addEventListener('input', function() {
	Plotly.restyle('scatterPlot', {
		'marker.size': dotSize.value
	});
});

// get map list
function getMapList(username) {
	// /api/<username>/maps
	url = serverurl + '/api/' + username + '/maps'
	$http.get(url)
		.then(function(response) {
			$scope.maps = response.data;
			// select the first map
			$scope.selectedMap = $scope.maps[0]
			//console.log($scope.maps)
		})
		.catch(function(data, status) {
			$log.info(data)
		})
}

// load a map
// http://127.0.0.1:5010/loadmap/public/rr30a
function loadMap(map) {
	url = serverurl + '/loadmap/' + $scope.username + '/' + map
	d3.json(url, function(error, data) {
	  if (error) {
	  	console.log('error: loadMap()', map)
	  }
	  $scope.loadedMap = map
	  getSessions()
	  getMapSegments()

		$scope.selectedSession = 0; //corresponds to all
		$scope.selectedMapSegment = 0 // corresponds to all

	  myplot0()
	  //console.log(data);
	});
}

// get sessions (the stack names)
// /v2/<username>/<mapname>/<item>
function getSessions() {
	// for some reason d3.json() did not work here?
	url = serverurl + '/v2/' + $scope.username + '/' + $scope.loadedMap + '/sessions'
	$http.get(url)
		.then(function(response) {
			$scope.sessions = response.data;
			$scope.sessions.splice(0, 0, 'All'); //insert 'All' sessions at beginning
			//console.log($scope.sessions)
		})
		.catch(function(data, status) {
			$log.info(data)
		})
}

// get map segments
// /v2/<username>/<mapname>/<item>
function getMapSegments() {
	// for some reason d3.json() did not work here?
	url = serverurl + '/v2/' + $scope.username + '/' + $scope.loadedMap + '/mapsegments'
	$http.get(url)
		.then(function(response) {
			$scope.mapsegments = response.data;
			$scope.mapsegments.splice(0, 0, 'All'); //insert 'All' sessions at beginning
			//console.log($scope.mapsegments)
		})
		.catch(function(data, status) {
			$log.info(data)
		})
}

// get map values
// http://127.0.0.1:5010/getmapvalues?session=1&xstat=x&ystat=y&zstat=z
function getMapValues(mapsegment, session, xstat, ystat, zstat) {
	if (mapsegment == null) {
		mapsegment = ''
	}
	if (session == null) {
		session = ''
	}
	url = serverurl + '/getmapvalues'
	url += '?mapsegment=' + mapsegment
	url += '&session=' + session
	url += '&xstat=' + xstat
	url += '&ystat=' + ystat
	url += '&zstat=' + zstat
	//console.log(url)
	d3.json(url, function(data) {
	  xydata = data
	  xydata.xstat = xstat
	  xydata.ystat = ystat
	  xydata.zstat = zstat
	  updateScatterPlot(xydata)
	  //console.log('xydata:');
	  //console.log(xydata);
	});
}

// Scatterplot drawing code
function updateScatterPlot(xydata) {
	// Create markers for points
	var x = [];
	var y = [];
	var z = [];
	var colors = [];

	for (var i = 0; i < xydata.x.length; i += 1) {
		x.push(xydata.x[i]);
		y.push(xydata.y[i]);
		z.push(xydata.z[i]);
		colors.push(xydata.mapsegment[i]);
	}

	//console.log(xydata)
	
   // Display scatter plot
	var trace = {
		x: x,
		y: y,
		//z: z,
		mode: 'markers',
		//type: 'scatter3d',
		type: 'scatter',
		name: 'Name of trace 1',
		marker: {
			size: dotSize.value,
			color: colors
		}
	};

	var data = [trace];

	myMargin = 80 //default is 80-100
	
	var layout = {
		//scene: {
		//	camera: {
		//		eye: {x: 0.001, y: -2, z: 1},
		//		center: {x: 0, y: 0, z: 0}
		//	}
		//},
		xaxis: {
			title: xydata.xstat,
			titlefont: { size: 20 },
			tickfont: { size: 16 }
		},
		yaxis: {
			title: xydata.ystat,
			titlefont: { size: 20 },
			tickfont: { size: 16 }
		},
		margin: {
			l: myMargin,
			r: 0,
			t: 10,
			b: myMargin,
			pad: 0
		}
	};

	//layout.scene.xaxis = {title: xydata.xstat} //, range: [0, 255]};
	//layout.scene.yaxis = {title: xydata.ystat} //, range: [0, 255]};
	//layout.scene.zaxis = {title: xydata.zstat} //, range: [0, 255]};

	Plotly.purge('scatterPlot');
	
	scatterPlot = Plotly.newPlot('scatterPlot', data, layout, {
		displayModeBar: true
	});
	
	/*
	Plotly.restyle('scatterPlot', 'x', [x])
	Plotly.restyle('scatterPlot', 'y', [y])
	//Plotly.restyle('scatterPlot', 'mode', 'markers')
	//Plotly.restyle('scatterPlot', 'type', 'scatter')
	Plotly.restyle('scatterPlot', 'colors', colors)
	*/
	
	var scatterPlotDiv = document.getElementById('scatterPlot');
	
	scatterPlotDiv.on('plotly_click', function(data){
	    //alert('You clicked this Plotly chart!');
	    pnt = data.points[0].pointNumber
	    if (pnt>=0) {
	    	userClick(pnt)
	    }
	});
	
} //updateScatterPlot

/*
var trace1 = {
  x: [],
  y: [],
  mode: 'markers',
  type: 'scatter'
};
var emptyData = [trace1];

	var emptyLayout = {
		//scene: {
		//	camera: {
		//		eye: {x: 0.001, y: -2, z: 1},
		//		center: {x: 0, y: 0, z: 0}
		//	}
		//},
		xaxis: {
			title: '', //xydata.xstat,
			titlefont: { size: 20 },
			tickfont: { size: 16 }
		},
		yaxis: {
			title: '', //xydata.ystat,
			titlefont: { size: 20 },
			tickfont: { size: 16 }
		},
		margin: {
			l: 80,
			r: 80,
			t: 20,
			b: 80,
			pad: 0
		}
	};

var myplot = Plotly.newPlot('scatterPlot', emptyData, emptyLayout, {
		displayModeBar: true
	});

var scatterPlotDiv = document.getElementById('scatterPlot');

scatterPlotDiv.on('plotly_click', function(data){
	//alert('You clicked this Plotly chart!');
	//console.log('plotly_click data:')
	//console.log(data)
	//console.log(data.points[0].pointNumber)
	pnt = data.points[0].pointNumber
	if (pnt>=0) {
		userClick(pnt)
	}
});
*/

function userClick(pnt) {
	//console.log('old:', $scope.userClickStackIndex)

	$scope.userClickStackIndex = xydata.stackidx[pnt]
	$scope.userClickSessionIndex = xydata.mapsess[pnt]
	$scope.userClickMapSegment = xydata.mapsegment[pnt]
	$scope.$apply();
	//console.log('userClickStackIndex:' + $scope.userClickStackIndex)
	//console.log('userClickSessionIndex:' + $scope.userClickSessionIndex)
}

	//
	//
	// Leaflet
	//
	//
	xyzLeaflet = null
	$scope.currSlice = 0
	$scope.image = null
	
	var showStackButton = document.getElementById('showStackButtonID');
	showStackButtonID.addEventListener('click', function() {
		getLeafletMapValues('', '')
	});

    $scope.setslicebutton = function (plusminus) {
        //console.log('setslicebutton()')
        $scope.currSlice += plusminus
        if ($scope.currSlice < 0) {
        	$scope.currSlice = 0
        }
        setSlice($scope.currSlice)
    }

	function setSlice(sliceNum) {
	    // /getimage/<username>/<mapname>/<int:timepoint>/<int:channel>/<int:slice>
	    //console.log('setSlice() sliceNum:', sliceNum)
	    tp = 0
	    channel = 1
	    imageUrl = serverurl + '/getimage/public/rr30a/0/1/' + sliceNum
	    //console.log('imageUrl:', imageUrl)
	    $scope.image.setUrl(imageUrl)
	    //update point masking
	    getLeafletData(sliceNum)

	    //
	    //geoJSON is a one-way controller of data, once set, changing the data will NOT update
	    myLayer.clearLayers()
	    myLayer.addData($scope.bicycleRental);
	}

	var myMap = L.map('myLeafletID', {
    	crs: L.CRS.Simple,
		fullscreenControl: true,
	    fullscreenControlOptions: {
		    position: 'topleft'
		}
  	});
	var bounds = [[0,0], [512,512]];
	$scope.image = L.imageOverlay('static/MAX_rr30a_s0_ch2.png', bounds).addTo(myMap);
	console.log('$scope.image:', $scope.image)
	myMap.fitBounds(bounds);

    //scale bar
    //L.control.scale().addTo(myMap);

	//utility function to convert x/y to y/x
	var yx = L.latLng;
	var xy = function(x, y) {
	    if (L.Util.isArray(x)) {    // When doing xy([x, y]);
	        return yx(x[1], x[0]);
	    }
	    return yx(y, x);  // When doing xy(x, y);
	};

	//
	//show popup on click
	var popup2 = L.popup();

	function onMapClick(e) {
		var userclick = xy(e.latlng.lat, e.latlng.lng)
		console.log('onMapClick:', userclick)
		userclick.lat = Math.round(userclick.lat) // * 100)/100
		userclick.lng = Math.round(userclick.lng) // * 100)/100
		console.log('userclick:', userclick)
		/*
		popup2
			.setLatLng(e.latlng)
			//.setContent("You clicked the map at " + e.latlng.toString())
			.setContent("You clicked the map at x:" + userclick.lat + " y:" + userclick.lng)
			.openOn(myMap);
		*/
	}
	
	myMap.on('click', onMapClick);

	myLayer = L.geoJSON([], {
	
		filter: function(feature, layer) {
			return feature.properties.show_on_map;
		},

		style: function (feature) {
			return feature.properties && feature.properties.style;
		},

		onEachFeature: function onEachFeature(feature, layer) {
			var popupContent = "Show spine index. ";
			if (feature.properties && feature.properties.popupContent) {
				popupContent += feature.properties.popupContent;
			}
			layer.bindPopup(popupContent);
		},

		pointToLayer: function (feature, latlng) {
			return L.circleMarker(latlng, {
				radius: 2,
				fillColor: "#ffff00",
				color: "#ffff00",
				weight: 1,
				opacity: 1,
				fillOpacity: 0.8
			});
		}
	}).addTo(myMap);

	// same as getmapvalues but for leaflet is always x/y/z
	//get this once
	function getLeafletMapValues(mapsegment, session) {
		console.log('getLeafletMapValues()')
		if (mapsegment == null) {
			mapsegment = ''
		}
		if (session == null) {
			session = ''
		}
		url = serverurl + '/getmapvalues'
		url += '?mapsegment=' + ''
		url += '&session=' + '0'
		url += '&xstat=' + 'x'
		url += '&ystat=' + 'y'
		url += '&zstat=' + 'z'
		console.log('url:', url)
		d3.json(url, function(data) {
		  xyzLeaflet = data
		  xyzLeaflet.xstat = 'x'
		  xyzLeaflet.ystat = 'y'
		  xyzLeaflet.zstat = 'z'
		  console.log(xyzLeaflet)
		});
	}

    //
    // fill in leaflet data from $scope.mapvalues
    function getLeafletData(theSlice) {
        //console.log('getLeafletData() theSlice:', theSlice)

        var myScale = 0.12
        var originalPixelsPerLine = 1024
        var webDisplaySize = 512
        var pixels_1024_512 = originalPixelsPerLine/ webDisplaySize //1024 is original, 512 is what we are using to display on webpage
        var zRange = 5 //slices
        var upperBound = theSlice - zRange
        var lowerBound = theSlice + zRange

        $scope.bicycleRental = {
            "type": "FeatureCollection",
            "features": [],
        }

        for (var i=0; i<xyzLeaflet.x.length; i++) {
            $scope.bicycleRental.features.push(
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            (xyzLeaflet.x[i] / myScale) / pixels_1024_512,
                            webDisplaySize - (xyzLeaflet.y[i] / myScale) / pixels_1024_512 //flipped
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "popupContent": "spine " + i,
                        "show_on_map": ( theSlice==-1 ? true : (xyzLeaflet.z[i] > upperBound && xyzLeaflet.z[i] < lowerBound) )
                    },
                    "id": i
                },
            )
        }
    } // getLeafletData

	//
	// append icons to leaflet map
	//
	var helloPopup = L.popup().setContent('Hello World!');

	//L.easyButton('fa-globe', function(btn, map){
	//    helloPopup.setLatLng(map.getCenter()).openOn(map);
	//}).addTo( myMap );

	L.easyButton( '<span class="star">&uarr;</span>', function(){
	  $scope.setslicebutton(-1)
	}).addTo( myMap );
	L.easyButton( '<span class="star">&darr;</span>', function(){
	  $scope.setslicebutton(+1)
	}).addTo( myMap );

///
// end leaflet
//

//
//
getMapList($scope.username)

}); //controller
