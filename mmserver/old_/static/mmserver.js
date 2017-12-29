// 20171216

//angular.module('mmserver_app', ['angularjs-dropdown-multiselect'])
//20171226 list [] was empty
angular.module('mmserver_app', [])

.controller('mmserver_controller', function($scope, $http, $location, $interval, $sce, $timeout, $log) {

//disable console.log
//see: https://stackoverflow.com/questions/1215392/how-to-quickly-and-conveniently-disable-all-console-log-statements-in-my-code
//console.log = function() {}

absUrl = $location.absUrl(); // http://127.0.0.1:8000/
console.log('absUrl:', absUrl)
serverurl = 'http://' + $location.host() + ':5010'

// ip of mmserver rest interface
serverurl = 'http://127.0.0.1:8000/'

console.log('serverurl:' + serverurl)

serverurl = absUrl

$scope.username = 'public'

$scope.maps = ''
$scope.selectedMap = ''

$scope.loadedMap = ''
$scope.mapInfo = ''

$scope.sessions = null;
$scope.selectedSession = 0; //corresponds to all

$scope.mapsegments = null
$scope.selectedMapSegment = 0 // corresponds to all

$scope.showPlotLines = true

var xydata = null;

$scope.userRowSelection = null //reassign on changing stats, set null on changing maps

$scope.userClickStackIndex = null
$scope.userClickSessionIndex = null
$scope.userClickMapSegment = null

//$scope.mapSizePixels = 512

$scope.statList = {
	'1': 'session',
	'2': 'days',
	'3': 'x',
	'4': 'y',
	'5': 'z',
	'6': 'pDist',
	'7': 'sLen3d_int1',
	'8': 'ubssSum_int2',
	'9': 'ubsdSum_int2',
	'10': 'ubssSum_int1',
	'11': 'ubsdSum_int1',
}
$scope.xStatSelection = 'days'
$scope.yStatSelection = 'pDist'

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
	//getMapDynamics(theMapSegment, theSession)
}

// handle marker size slider
dotSize.addEventListener('input', function() {
	console.log('dotSize.value:', dotSize.value)
	Plotly.restyle('scatterPlot', {
		'marker.size': dotSize.value
	}, [0]); // [0] is first trace
});

//handle plot lines checkbox
$scope.userTogglePlotLines = function () {
	console.log('userTogglePlotLines()', $scope.showPlotLines)
	if ($scope.showPlotLines) {
		Plotly.restyle('scatterPlot', {
			'mode': 'lines+markers'
		}, [0]); // [0] is first trace
	} else {
		Plotly.restyle('scatterPlot', {
			'mode': 'markers'
		}, [0]); // [0] is first trace
	}
}

// get map list
function getMapList(username) {
	// /api/<username>/maps
	var url = serverurl + 'api/' + username + '/maps'
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
function loadMap(map) {
	// http://127.0.0.1:5010/loadmap/public/rr30a
	var url = serverurl + 'loadmap/' + $scope.username + '/' + map
	$http.get(url)
		.then(function(response) {
			$scope.mapInfo = response.data // should contain all we need to know abou the map
			//console.log('$scope.mapInfo:')
			//console.log($scope.mapInfo)

			$scope.sessions = $scope.mapInfo.stackNames;
			$scope.sessions.splice(0, 0, 'All'); //insert 'All' sessions at beginning

			$scope.loadedMap = map

			//getSessions()
			//getMapSegments()

			$scope.selectedSession = 0; //corresponds to all
			$scope.selectedMapSegment = 1 // corresponds to FIRST session, session 0

			$scope.mapsegments = []
			var i
			for (i=0; i<$scope.mapInfo.numMapSegments; i+=1) {
				$scope.mapsegments[i] = i;
			}
			$scope.mapsegments.splice(0, 0, 'All'); //insert 'All' sessions at beginning

			$scope.userRowSelection = null
			
			myplot0()
			
			//
			// leaflet
			getLeafletMapData()
			
		})
		.catch(function(data, status) {
			$log.info(data)
		})
}

// call parseFloat on a multidimensional array (of string)
//rows are runs, columns are sessions
//see: https://stackoverflow.com/questions/35325767/map-an-array-of-arrays
function nested_to_float(a) {
	return a.map(function (nested) {
		return nested.map(function (element) {
			return parseFloat(element);
		});
	});
}

// get map values
// http://127.0.0.1:5010/v2/<username>/<mapname>/getmapvalues?session=1&xstat=x&ystat=y&zstat=z
//http://127.0.0.1:5010/v2/public/rr30a/getmapvalues?mapsegment=&session=0&xstat=x&ystat=y&zstat=z
function getMapValues(mapsegment, session, xstat, ystat, zstat) {
	if (mapsegment == null) {
		mapsegment = ''
	}
	if (session == null) {
		session = ''
	}
	
	var startTime = Date.now()
	
	var url = serverurl + 'v2/' + $scope.username + '/' + $scope.loadedMap + '/getmapvalues'
	url += '?mapsegment=' + mapsegment
	url += '&session=' + session
	url += '&xstat=' + xstat
	url += '&ystat=' + ystat
	url += '&zstat=' + zstat

	console.log('getMapValues() url:', url)
	
	$http.get(url)
		.then(function(response) {
		  //console.log('getMapValues() response.data:')
		  //console.log(response.data)
		  
		  xydata = {}
		  //xydata.x = parseFloat(response.data.x)
		  //console.log('response.data.length:', response.data.length)

			xydata.x = nested_to_float(response.data.x)
			xydata.y = nested_to_float(response.data.y)
			xydata.z = nested_to_float(response.data.z)
			xydata.mapsegment = nested_to_float(response.data.mapsegment)
			xydata.stackidx = nested_to_float(response.data.stackidx)
			xydata.mapsess = nested_to_float(response.data.mapsess)
			xydata.dynamics = nested_to_float(response.data.dynamics)
			
		  //20171220, this was working but was not handing UN flattened 2d response form rest
		  /*
		  xydata.x = response.data.x.map(parseFloat)
		  xydata.y = response.data.y.map(parseFloat)
		  xydata.z = response.data.z.map(parseFloat)
		  xydata.mapsegment = response.data.mapsegment.map(parseFloat)
		  xydata.stackidx = response.data.stackidx.map(parseFloat)
		  xydata.mapsess = response.data.mapsess.map(parseFloat)
		  */
		  //
		  xydata.xstat = xstat
		  xydata.ystat = ystat
		  xydata.zstat = zstat
		  
		  console.log('getMapValues() xydata:');
		  console.log(xydata);

			var stopTime = Date.now()
			var elapsedTime = (stopTime-startTime) / 1000
			console.log('getMapValues() REST took:', elapsedTime, 'seconds')

		  //
		  updateScatterPlot(xydata)
		  //
		})
		.catch(function(data, status) {
			$log.info(data)
		})

}

// Scatterplot drawing code
function updateScatterPlot(xydata) {
	var startTime = Date.now()
	
	// Create markers for points
	var x = [];
	var y = [];
	var z = [];
	var colors = [];
	var runRow = []
	var runCol = []
	
	console.log('updateScatterPlot() xydata:')
	console.log(xydata)
	
	/*
	I need some way to draw lines but not between runs (rows) and between first/last element
		- Here, I am pushing a nan element to break up each row
		- Flattened array is # rows elements longer than expected -> use click pnt then spineidx[pnt]
	*/
	
	//length of x is number of runs!
	/*
	for (var i = 0; i < xydata.x.length; i += 1) {
		x.push(xydata.x[i]);
			x.push([NaN])
		y.push(xydata.y[i]);
			y.push([NaN])
		z.push(xydata.z[i]);
			z.push([NaN])
		colors.push(xydata.mapsegment[i]);
			colors.push([])
		// book-keeping
		runRow.push(Array(numCol).fill(i));
			runRow.push([NaN]);
		runCol.push(xydata.mapsess[i]);
			runCol.push([NaN]);
	}
	*/
		
	// 20171224, thought this would be faster than looping? Does not seem to be?
	// construct x/y/z as flat array
	x = xydata.x.reduce(
	  function(a, b) {
	    return a.concat(b, NaN);
	  },
	  []
	);
	y = xydata.y.reduce(
	  function(a, b) {
	    return a.concat(b, NaN);
	  },
	  []
	);
	z = xydata.z.reduce(
	  function(a, b) {
	    return a.concat(b, NaN);
	  },
	  []
	);
	colors = xydata.dynamics.reduce(
	  function(a, b) {
	    return a.concat(b, NaN);
	  },
	  []
	);
	/*
	colors = xydata.mapsegment.reduce(
	  function(a, b) {
	    return a.concat(b, NaN);
	  },
	  []
	);
	*/
	runCol = xydata.mapsess.reduce(
	  function(a, b) {
	    return a.concat(b, NaN);
	  },
	  []
	);

	var numRows = xydata.x.length
	var numCol = xydata.x[0].length
	runRow = Array(numRows)
	for (var i = 0; i < numRows; i += 1) {
		runRow.push(Array(numCol).fill(i))
		//runRow.push([NaN])
	}
	runRow = runRow.reduce(
	  function(a, b) {
	    return a.concat(b, NaN);
	  },
	  []
	);
	
	//20171220, flatten for plotting
	//there must be some way for plotly to plot an array of array?
	if (true) {
		/*
		x = [].concat.apply([], x)
		y = [].concat.apply([], y)
		z = [].concat.apply([], z)
		colors = [].concat.apply([], colors)
		//
		runRow = [].concat.apply([], runRow)
		runCol = [].concat.apply([], runCol)
		*/
	}
	
	//console.log('updateScatterPlot() x:')
	//console.log(x)
	//console.log(y)
	
	// map color index onto rgb
	colors = colors.map(function(obj) {
		var rObj = 'rgb(0,0,0)'
		if (obj==1) {
			rObj = 'rgb(0,255,0)'
		} else if (obj==2) {
			rObj = 'rgb(255,0,0)'
		} else if (obj==3) {
			rObj = 'rgb(0, 0, 255)'
		} else if (obj==4) {
			rObj = 'rgb(0,0,0)'
		}
		return rObj
	});
	
   // Display scatter plot
	var trace = {
		x: x,
		y: y,
		//z: z,
		mode: ($scope.showPlotLines) ? 'lines+markers' : 'markers',
		type: 'scatter', //type: 'scatter3d',
		name: 'Name of trace 1',
		marker: {
			size: dotSize.value,
			opacity: 1,
			color: colors
		},
		line : {
			color: 'aaaaaa',
			width: 1
		},
		hoverinfo: '',
		//inject for book-keeping
		myRunRow: runRow,
		myRunCol: runCol,
		//xstat: xydata.xstat,
		//ystat: xydata.ystat,
	};

	var runSelection = {
		x: $scope.userRowSelection ? xydata.x[$scope.userRowSelection] : [],
		y: $scope.userRowSelection ? xydata.y[$scope.userRowSelection] : [],
		mode: 'lines+markers',
		type: 'scatter',
		name: 'runSelection',
		marker: {
			size: 5,
			opacity: 1,
			color: 'cccc00'
		},
		line: {
			color: 'cccc00',
			width: 4,
		}
	}
	
	var data = [trace, runSelection];

	
	var layout = {
		//scene: {
		//	camera: {
		//		eye: {x: 0.001, y: -2, z: 1},
		//		center: {x: 0, y: 0, z: 0}
		//	}
		//},
		hovermode: 'closest',
		showlegend: false,
		xaxis: {
			title: xydata.xstat,
			titlefont: { size: 20 },
			tickfont: { size: 16 },
			zeroline: false,
	        showline : true,
	        autotick: true,
		},
		yaxis: {
			title: xydata.ystat,
			titlefont: { size: 20 },
			tickfont: { size: 16 },
			zeroline: false,
	        showline : true,
	        autotick: true,
	        ticks: '',
       		showticklabels: true,
		},
		margin: {
			l: 80, //default i s80
			r: 0,
			t: 10,
			b: 50, //default is 80
			pad: 0
		}
	};

	Plotly.purge('scatterPlot');
	
	scatterPlot = Plotly.newPlot('scatterPlot', data, layout, {
		displayModeBar: true,
		scrollZoom: true,
	});
	
	var scatterPlotDiv = document.getElementById('scatterPlot');
	
	// make a <div id="hoverinfo"> and this updates on hover
	//hoverInfo = document.getElementById('hoverinfo')
	scatterPlotDiv.on('plotly_hover', function(data){
    	// this turns off tooltips on hover
    	Plotly.Fx.hover(scatterPlotDiv, []);
    	//hoverInfo.innerHTML = '';
	});

	//scatterPlotDiv.on('plotly_beforehover',function(){
	//    return false;
	//});

	scatterPlotDiv.on('plotly_click', function(data){
	    pointNumber = data.points[0].pointNumber
	    curveNumber = data.points[0].curveNumber
	    console.log('pointNumber:', pointNumber)
	    console.log('curveNumber:', curveNumber)
	    if (pointNumber>=0) {
	    	userClick(pointNumber, data)
	    }
	});

	var stopTime = Date.now()
	console.log('updateScatterPlot() took', (stopTime-startTime) / 1000, 'seconds')
} //updateScatterPlot


function userClick(pnt, data) {
	console.log('=== userClick()', pnt)
	//console.log('xydata:')
	//console.log(xydata)
	//console.log('data:')
	//console.log(data)
	
	//console.log('data.points[0].data.myRunRow:')
	//console.log(data.points[0].data.myRunRow)
	
	var selRunRow = data.points[0].data.myRunRow[pnt]
	var selRunCol = data.points[0].data.myRunCol[pnt]

	//$scope.userRowSelection = selRunRow
	
	console.log('selRunRow:', selRunRow, 'selRunCol:', selRunCol)
	
	//need to call $scope.$apply() for these to become visible in html
	$scope.userClickStackIndex = xydata.stackidx[selRunRow][selRunCol]
	$scope.userClickSessionIndex = xydata.mapsess[selRunRow][selRunCol]
	$scope.userClickMapSegment = xydata.mapsegment[selRunRow][selRunCol]
	//$scope.$apply();
	
	selectInPlotly(selRunRow, selRunCol)
	
  	$scope.$apply(); // to update html showing userClickStackIndex, etc. etc.

	//
	// leaflet
	// if map is rr30a, segment is NOT all, sessions is all
	// to do this I need plotly to get ALL so row is in sync with leaflet
	console.log('todo: link with leaflet !!!')
	if ($scope.selectedSession==0 && $scope.selectedMapSegment==0) {
		selectRun(selRunCol, selRunRow)
	}
  }

function selectInPlotly(runRow, runCol) {
	//todo: we are only selecting run, NOT point
	xNew = xydata.x[runRow]
	yNew = xydata.y[runRow]

	console.log('selectInPlotly() row:', runRow, 'col:', runCol) //, 'xNew:', xNew, 'yNew:', yNew)
	
	$scope.userRowSelection = runRow

	Plotly.restyle('scatterPlot', {
    	x: xNew,
    	y: yNew,
  	}, [1])

  	updateScatterPlot(xydata)

}

	/////////////////////////////////////////////////
	//
	// Leaflet
	//
	/////////////////////////////////////////////////
	mapLeafletData = null // holds x/y/z for ENTIRE map
	xyzLeaflet = [] // holds x/y/z for ONE session, need numSession of these (an array ?)
	//xyzTracingLeaflet = [] // holds x/y/z of tracing for (map,session)
	xyzTracingLeaflet2 = [] // todo: this is more classic dit for .find todo: merge these two !!!!
	
	$scope.leafletUser = 'public'
	$scope.leafletMap = 'rr30a'
	$scope.leafletTimepoint = 0
	$scope.leafletChannel = 2

	$scope.showAnnotations = true
	$scope.showTracing = true
	$scope.showTimepointNumber = true
	
	$scope.showMaxProject = false
	$scope.maskPoints = true
	
	$scope.linkTimepoints = false
	$scope.showSlidingZ = false
	$scope.showImageControls = false
	
	//
	//create leaflet map
	var bounds = [[0,0], [512,512]];

	var tmpNumTimepoint = 6

	$scope.currSlice = []
	//$scope.image = []

	myLayer = Array(tmpNumTimepoint)
	myTracingLayer = Array(tmpNumTimepoint)
	layerGroup = Array(tmpNumTimepoint)

	upEasyButton = Array(tmpNumTimepoint)
	downEasyButton = Array(tmpNumTimepoint)
	
	bicycleRental = Array(tmpNumTimepoint)
	bicycleRental2 = Array(tmpNumTimepoint)
	
    var myScale = 0.12
    var originalPixelsPerLine = 1024
    var webDisplaySize = 512
    var pixels_1024_512 = originalPixelsPerLine/ webDisplaySize //1024 is original, 512 is what we are using to display on webpage


	leafletRun = Array(tmpNumTimepoint)
	$scope.image = Array(tmpNumTimepoint)

	$scope.showTimepoints = Array(tmpNumTimepoint)
	$scope.showTimepoints.fill(true)
	
	//$scope.$apply();
	
	function buildMapInterface() {
		for (var thisTP=0; thisTP<tmpNumTimepoint; thisTP+=1) {

			if (! $scope.showTimepoints[thisTP]) {
				// this should cause memory problems !!!
				//leafletRun[thisTP] = null
				continue
			}
		
			var thisDIV = 'myLeafletID' + thisTP

			console.log('building thisTP:', thisTP, 'thisDIV:', thisDIV)
		
			//if (leafletRun[thisTP]) {
			//	//console.log('   removing tp:', thisTP)
			//	//leafletRun[thisTP].remove()
			//	//$scope.image[thisTP].remove()
			//}
			
			var madeMap = false
			if ( ! leafletRun[thisTP]) {
				madeMap = true
				leafletRun[thisTP] = L.map(thisDIV, {
						crs: L.CRS.Simple,
						scrollWheelZoom: false,
						attributionControl: false,
						//center: [100,100],
						//zoomControl: $scope.showImageControls ? true : false,
						//fullscreenControl: true,
						//fullscreenControlOptions: {
						//	position: 'topleft'
						//}
				}) //.fitBounds(bounds);
			}
			
			/*
			leafletRun[thisTP].on('load', function (e) {
				var id = e.target._container.id
				var tp = id.replace('myLeafletID','')
				var tp = parseInt(tp)
				console.log('*** load: id:', id)
				//$scope.image[tp] = L.imageOverlay('', bounds).addTo(leafletRun[thisTP]);
				//setMaxProject(tp)
				
				//leafletRun[tp].fitBounds(bounds);
				//leafletRun[tp].setView([100,100],0)
				
				//addLayers(tp)
			});
			*/
			
			// remove controls if neccessary
			if (! $scope.showImageControls) {
				leafletRun[thisTP].removeControl(leafletRun[thisTP].zoomControl);
			}

			// this should work with small tweeks
			// see: https://gis.stackexchange.com/questions/200865/leaflet-crs-simple-custom-scale
			//L.control.scale({
			//  imperial: false
			//}).addTo(leafletRun[thisTP]);

			if (madeMap ) {
				$scope.currSlice[thisTP] = 0
			}
			
			//if ($scope.image[thisTP]) {
			//	console.log('removing image overlay tp:', thisTP)
			//	$scope.image[thisTP].remove()
			//}
			
			//was this
			if (madeMap ) {
				$scope.image[thisTP] = L.imageOverlay('', bounds).addTo(leafletRun[thisTP]);
			}
			//now this
			//overlay = L.imageOverlay('', bounds)
			//overlay.addTo(leafletRun[thisTP]);
			//$scope.image[thisTP] = overlay
			
			if (madeMap ) {
				setMaxProject(thisTP)
				leafletRun[thisTP].fitBounds(bounds);
			}
						
			// remove this 
			//leafletRun[thisTP].setView([100,100],0)
			
			leafletRun[thisTP].on('click', onMapClick);

			addLayers(thisTP)

			document.getElementById(thisDIV).addEventListener("keydown", myKeyDown);
			document.getElementById(thisDIV).addEventListener("keyup", myKeyUp);
			document.getElementById(thisDIV).addEventListener("wheel", myWheel);
			
			leafletRun[thisTP].on('move', function (e) {
				//console.log('      move');
				//console.log(e);
				//this.getLatLng()
			});

			leafletRun[thisTP].on('drag', function (e) {
				if ($scope.linkTimepoints) {
					//console.log('      drag');
					//console.log(e);
					//console.log(e.target.getCenter())
					//console.log(e.target.getContainer())
				
					var id = e.target._container.id
					var tp = id.replace('myLeafletID','')
					var tp = parseInt(tp)

					var thisCenter = e.target.getCenter() //the posiiton we are dragging to
					//console.log('thisCenter:', thisCenter)
				
				
					var latDiff = thisCenter.lat - linkedCenter[tp].lat
					var lngDiff = thisCenter.lng - linkedCenter[tp].lng
				
					for (var i=0; i<tmpNumTimepoint; i+=1){
						if (! $scope.showTimepoints[i]) {
							continue
						}
						if (i==tp) {
							continue
						}
					
						//console.log('linkedCenter:', i, linkedCenter[i])
					
						//var newLat = thisCenter.lat - linkedCenter[i].lat
						//var newLng = thisCenter.lng - linkedCenter[i].lng
						var newLat = latDiff + linkedCenter[i].lat
						var newLng = lngDiff + linkedCenter[i].lng
					
						var thisZoom = leafletRun[i].getZoom()
						//leafletRun[i].setView(thisCenter,thisZoom)
						leafletRun[i].setView([newLat,newLng],thisZoom)
					}
				}
			});

			leafletRun[thisTP].on('zoom', function (e) {
				if ($scope.linkTimepoints) {
					//console.log('      zoom');
					//console.log(e);
					//console.log(e.target.getCenter())
					//console.log(e.target.getContainer())
					var thisCenter = e.target.getCenter()
					var thisZoom = e.target.getZoom()
					for (var i=0; i<tmpNumTimepoint; i+=1){	
						if (! $scope.showTimepoints[i]) {
							continue
						}
						leafletRun[i].setView(thisCenter,thisZoom)
					}
				}
			});
		
			$scope.resetTimepoints = function () {
				console.log('resetTimepoints()')
				for (var i=0; i<tmpNumTimepoint; i+=1) {
					if (! $scope.showTimepoints[i]) {
						continue
					}
					leafletRun[i].setView([256,256],0)
				}
			}

		}
	} //buildMapInterface
	
	// when true, mouse wheel sets slice, when false (on keyboard contorl) wheel will zoom
	wheelControlsSlice = true

	//
	//keyboard
	function myKeyDown (event) {
		const keyName = event.key;
		console.log(event)
		if (keyName === 'Control') {
			var tp = event.srcElement.id.replace('myLeafletID','')
			var tp = parseInt(tp)
			console.log('myKeyDown() Control', event.srcElement.id, 'tp:', tp)

			leafletRun[tp].scrollWheelZoom.enable()
			wheelControlsSlice = false
			//return;
		}
	}
	function myKeyUp (event) {
		const keyName = event.key;
		if (keyName === 'Control') {
			var tp = event.srcElement.id.replace('myLeafletID','')
			var tp = parseInt(tp)
			console.log('myKeyUp() Control', event.srcElement.id, 'tp:', tp)

			leafletRun[tp].scrollWheelZoom.disable()
			//leafletRun[tp].redraw()
			wheelControlsSlice = true
			//return;
		}
	}

	//
	//mouse
	function myWheel(event) {
		//this.style.fontSize = "35px";
		//console.log('wheel:')
		//console.log(e)
		//console.log(e.deltaY, e.deltaMode)
		if (wheelControlsSlice && ! $scope.showMaxProject) {
			//console.log('myWheel() wheelControlsSlice:', wheelControlsSlice, event.deltaY)

			var plusminus = 1
			if (event.deltaY > 0) {
				plusminus = 1
			} else {
				plusminus = -1
			}

			if ($scope.linkTimepoints) {
				for (var i=0; i<tmpNumTimepoint; i+=1) {
					if (! $scope.showTimepoints[i]) {
						continue
					}
					$scope.setslicebutton(i, plusminus)
					event.preventDefault()
				}
			} else {
			
				var tp = event.srcElement.id.replace('myLeafletID','')
				var tp = parseInt(tp)

				//$scope.currSlice[tp] += 1
				$scope.setslicebutton(tp, plusminus)
				//setSlice(tp, $scope.currSlice[tp])

				event.preventDefault()
			}
		}
		//return false;
		//return true
	}

	//
	// select a run in leaflet map
	function selectRun0(e) {
		console.log('=== selectRun0()')
		//console.log(e)
		
		var myRunRow = e.target.feature.myRunRow //this should be run row in *this leaflet timepoint
		var myTimepoint = e.target.feature.myTimepoint
		
		//console.log('myRunRow:', myRunRow)
		//console.log('tp:', myTimepoint)
		
		selectRun(myTimepoint, myRunRow)
	}
	
	var gFindThis_mapSegment = null // todo: i need to really use map segments, assuming stack segments are same !!!
	var gFindThis_sDist = null
	
	function selectRun(seedTP, seedRunRow) {
		// seedRunRow is row run in plotted leaflet x/y/z data
		// step through leaflet id(s)
		// on missing values, snap to image position using (seedTP, seedRunRow)
		for (var currTP = 0; currTP<tmpNumTimepoint; currTP+=1) {
			var thisPnt = 1

			if (! $scope.showTimepoints[currTP]) {
				continue
			}

			// mapLeafletData is the original (this is getting confusing)
			var stackidx = mapLeafletData.stackidx[seedRunRow][currTP]
			
			if (stackidx >= 0) {
				var x = xyzLeaflet[currTP].x[seedRunRow]
				var y = xyzLeaflet[currTP].y[seedRunRow]
				var z = xyzLeaflet[currTP].z[seedRunRow]
				//console.log('tp:', currTP, 'x:', x , 'y:', y, 'z:', z)
			
				setMapPosition(currTP, x, y, z)
			
				// make a marker
				var ll = L.latLng;
				ll = um2leaflet(x, y)
				//console.log('marker at:', ll)
				layerGroup[currTP].clearLayers()
				L.marker(ll).addTo(layerGroup[currTP]);
			} else {
				// snap using image coordinates from seed tp/runRow
				//console.log('=== missing pnt at currTP:', currTP, 'seedRunRow:', seedRunRow)
				
				//console.log('mapLeafletData:')
				//console.log(mapLeafletData)
				//console.log('xyzTracingLeaflet2:')
				//console.log(xyzTracingLeaflet2)
				
				//get sDist along line for seed
				var seedSegmentID = mapLeafletData.mapsegment[seedRunRow][seedTP]
				var seed_cPnt = mapLeafletData.cPnt[seedRunRow][seedTP]
				
				//look into tracing to get seed tp sDist
				var seed_sDist = xyzTracingLeaflet2[seedTP][seed_cPnt].sDist //this seems wrong?
				//console.log('seedSegmentID:', seedSegmentID, 'seed_cPnt:', seed_cPnt, 'seed_sDist:', seed_sDist)

				//look in currTP tracing for corresponding sDist ~= seed_sDist
				gFindThis_mapSegment = seedSegmentID
				gFindThis_sDist = seed_sDist
				var foundIdx = xyzTracingLeaflet2[currTP].find(find_sDist_)
				//console.log('foundIdx:', foundIdx)
				
				//
				//snap to the x/y/z of the tracing
				var xSnap = xyzTracingLeaflet2[currTP][foundIdx.idx].x
				var ySnap = xyzTracingLeaflet2[currTP][foundIdx.idx].y
				var zSnap = xyzTracingLeaflet2[currTP][foundIdx.idx].z
				setMapPosition(currTP, xSnap, ySnap, zSnap)
				
				//and make a marker
				//var ll = L.latLng;
				//ll = um2leaflet(xSnap, ySnap)	
				//layerGroup[currTP].clearLayers()
				//L.marker(ll).addTo(layerGroup[currTP]);
			}
		}
		
		//select in plotly scatterplot (assuming it has same shape)
		// segments NEED to be all
		selectInPlotly(seedRunRow, seedTP)
	}
	
	// tracing is an array of xyzTracingLeaflet[currTP].sDist
	function find_sDist_(tracing) {
		if (tracing.ID == gFindThis_mapSegment) {
			if (tracing.sDist > gFindThis_sDist) {
				return true
			}
		}
		return false
		//console.log(tracing)
	}
	
	//
	// leflet button callbacks
	$scope.loadStackDataButton = function () {
		console.log('loadStackDataButton')
		getLeafletMapData()
	}
	
/*
	$scope.plotRunButton = function () {
		//getLeafletData()
		for (var tp=0; tp<tmpNumTimepoint; tp+=1) {
			//convert mapLeafletData into a new copy (xyzLeaflet[tp]) just for the leaflet timepoint
			getLeafletMapValues(tp, '')
		}
		
	}
*/
	
$scope.imageBrightness = 100
$scope.$watch("imageBrightness", function(){
    // do whatever you need with the just-changed $scope.value
    for (var thisTP=0; thisTP<tmpNumTimepoint; thisTP+=1) {
		if (! $scope.showTimepoints[thisTP]) {
			continue
		}

    	if ($scope.image[thisTP]) {
    		$scope.image[thisTP].getElement().style.filter = "brightness(" + $scope.imageBrightness + "%)";    
    	}
    	//$scope.image[i].getElement().style.filter = "invert(" + $scope.imageBrightness + "%)";    
    	//$scope.image[i].getElement().style.filter = "blur(" + $scope.imageBrightness + "px)";    
    	//$scope.image[i].getElement().style.filter = "hue-rotate(" + $scope.imageBrightness + "deg)";    
	}
});

    $scope.setslicebutton0 = function (tp, plusminus) {
		if ($scope.linkTimepoints) {
			for (var i=0; i<tmpNumTimepoint; i+=1) {
				if (! $scope.showTimepoints[i]) {
					continue
				}
				$scope.setslicebutton(i, plusminus)
				event.preventDefault()
			}
		} else {
			$scope.setslicebutton(tp, plusminus)
			event.preventDefault()
		}
	}
	
    $scope.setslicebutton = function (tp, plusminus) {
        //console.log('setslicebutton() tp:', tp, 'plusminus:', plusminus)
        $scope.currSlice[tp] += plusminus
        if ($scope.currSlice[tp] < 0) {
        	$scope.currSlice[tp] = 0
        }
        if ($scope.currSlice[tp] >= $scope.mapInfo.numSlices[tp]) {
        	$scope.currSlice[tp] = $scope.mapInfo.numSlices[tp]-1
        }
        setSlice(tp, $scope.currSlice[tp])
    }

	function setSlice(tp, sliceNum) {
	    // /getimage/<username>/<mapname>/<int:timepoint>/<int:channel>/<int:slice>
	    //console.log('setSlice() sliceNum:', sliceNum)
	    //var imageUrl = serverurl + 'getimage/' + $scope.leafletUser + '/' + $scope.leafletMap + '/' + $scope.leafletTimepoint + '/' + $scope.leafletChannel + '/' + sliceNum
	    
	    // one image
	    var imageUrl = serverurl + 'getimage/' + $scope.leafletUser + '/' + $scope.leafletMap + '/' + tp + '/' + $scope.leafletChannel + '/' + sliceNum
	    
	    // sliding z
	    var imageUrl = ''
	    if ($scope.showSlidingZ) {
	    	imageUrl = serverurl + 'getslidingz/' + $scope.leafletUser + '/' + $scope.leafletMap + '/' + tp + '/' + $scope.leafletChannel + '/' + sliceNum
			$http.get(url)
				.then(function(response) {
					//console.log('getLeafletMapData) response.data:')
					//console.log(response.data)
					$scope.image[tp].setUrl(imageUrl)

				})
				.catch(function(data, status) {
					$log.info(data)
				})
	    	$scope.image[tp].setUrl(imageUrl)
	    } else {
	    	imageUrl = serverurl + 'getimage/' + $scope.leafletUser + '/' + $scope.leafletMap + '/' + tp + '/' + $scope.leafletChannel + '/' + sliceNum
	    	$scope.image[tp].setUrl(imageUrl)
	    }
	    

	    getLeafletData(tp, sliceNum)

	    //
	    redrawLayers(tp)
	    
	}

	function setMaxProject(tp) {
		//var maxImageUrl = serverurl + 'getmaximage/' + $scope.leafletUser + '/' + $scope.leafletMap + '/' + $scope.leafletTimepoint + '/' + $scope.leafletChannel
		var maxImageUrl = serverurl + 'getmaximage/' + $scope.leafletUser + '/' + $scope.leafletMap + '/' + tp + '/' + $scope.leafletChannel
	    $scope.image[tp].setUrl(maxImageUrl)
	}
	
	// split this to redraw one or other: xyz or tracing
	function redrawLayers(tp) {
	    //console.log('redrawLayers() tp:', tp)
	    //geoJSON is a one-way controller of data, once set, changing the data will NOT update
	    myLayer[tp].clearLayers()
	    if ( $scope.showAnnotations) {
		    myLayer[tp].addData(bicycleRental[tp]);
	    }
	    
	   	myTracingLayer[tp].clearLayers()
	    if ( $scope.showTracing) {
	    	myTracingLayer[tp].addData(bicycleRental2[tp]);
		}
	}
	
	// set the position/pan of leaflet image
	// x,y is in um
	function setMapPosition(tp, x,y,slice) {
		//zoom = leafletRun[0].getZoom()
		var zoom = 2
		var ll = L.latLng;
		var ll = um2leaflet(x,y)
		//ll = xy(ll)
		//console.log('setMapPosition()', ll)
		leafletRun[tp].setView(ll, zoom);
		
		if (slice != null) {
			$scope.currSlice[tp] = slice
			setSlice(tp, slice)
		}
		//var marker = L.marker(ll).addTo(leafletRun[tp]);
	}

    //
    // convert um to leaflet coordinates
    function um2leaflet(x,y) {
    	var x = (x / myScale) / pixels_1024_512
    	var y = webDisplaySize - (y / myScale) / pixels_1024_512 //reversed
     	var ll = xy([x,y]) //swap
     	return ll
    }
	

	//
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
		
		//cancel existing marker on spine
		for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
			if (! $scope.showTimepoints[currTP]) {
				continue
			}

			layerGroup[currTP].clearLayers()
		}
				
		/*
		popup2
			.setLatLng(e.latlng)
			//.setContent("You clicked the map at " + e.latlng.toString())
			.setContent("You clicked the map at x:" + userclick.lat + " y:" + userclick.lng)
			.openOn(leafletRun[tp]);
		*/
	}
	
	function addLayers(tp) {
		// xyz layer
		//if (myLayer[tp]) {
		//
		//} else {
			if (myLayer[tp]) {
				myLayer[tp].remove()
			}
			
			myLayer[tp] = L.geoJSON([], {
	
				filter: function(feature, layer) {
					return feature.properties.show_on_map;
				},

				style: function (feature) {
					//20171225, should be able to color each pnt here?
					return feature.properties && feature.properties.style;
				},

				onEachFeature: function onEachFeature(feature, layer) {
					var popupContent = "Show spine index: ";
					if (feature.properties && feature.properties.popupContent) {
						popupContent += feature.properties.popupContent;
					}
					layer.bindPopup(popupContent);
					// 20171225, install an on click callback for EACH point !!!
					layer.on({
						click: selectRun0
					});
				},

				pointToLayer: function (feature, latlng) {
					//console.log('XXXXXX feature')
					//console.log(feature)
					return L.circleMarker(latlng, {
						radius: 2,
						fillColor: feature.properties.myColor, //"#ffff00",
						color: feature.properties.myColor, //"#ffff00",
						weight: 1,
						opacity: 1,
						fillOpacity: 0.8
					});
				}
			}) //.bindTooltip('Hi There!') //this binds a tooltip to each marker (on hover)
			.addTo(leafletRun[tp]);
		//} // myLayer[tp]
		
		// tracing layer
		if (myTracingLayer[tp]) {
			myTracingLayer[tp].remove()
		}

		myTracingLayer[tp] = L.geoJSON([], {
	
			filter: function(feature, layer) {
				return feature.properties.show_on_map;
			},

			style: function (feature) {
				return feature.properties && feature.properties.style;
			},

			pointToLayer: function (feature, latlng) {
				return L.circleMarker(latlng, {
					radius: 1,
					fillColor: "#ff00ff",
					color: "#ff00ff",
					weight: 1,
					opacity: 1,
					fillOpacity: 0.8
				});
			}
		}).addTo(leafletRun[tp]);

		//L.easyButton('fa-globe', function(btn, map){
		//    helloPopup.setLatLng(map.getCenter()).openOn(map);
		//}).addTo( leafletRun[tp] );

		//
		// up and down arrow for slices
		if ( ! upEasyButton[tp] ) {
			upEasyButton[tp] = L.easyButton( '<span class="star">&uarr;</span>', function(){
			  $scope.setslicebutton0(tp, -1)
			}).addTo( leafletRun[tp] );
		}
		if (! $scope.showImageControls) {
			upEasyButton[tp].remove()
		}
		
		if (! downEasyButton[tp] ) {
			downEasyButton[tp] = L.easyButton( '<span class="star">&darr;</span>', function(){
			  $scope.setslicebutton0(tp, +1)
			}).addTo( leafletRun[tp] );
		}
		if (! $scope.showImageControls) {
			downEasyButton[tp].remove()
		}

		//see: https://gis.stackexchange.com/questions/172508/add-an-event-listener-on-a-marker-in-leaflet
		//
		// single spine selection
		if (! layerGroup[tp]) {
			layerGroup[tp] = L.layerGroup().addTo(leafletRun[tp]); //holds single spine selection
		}
		//layerGroup[tp] = L.featureGroup().addTo(leafletRun[tp]); //holds single spine selection

	} // addLayers
	
	// get leaflet x/y/z for ENTIRE map, ALL sessions, ALL map segments
	//each leaflet map div will pull a column (session) into a copy of a local variable
	function getLeafletMapData() {
		var url = serverurl + 'v2/' + $scope.username + '/' + $scope.loadedMap + '/getmapvalues'
		url += '?mapsegment=' + ''
		url += '&session=' + ''
		url += '&xstat=' + 'x'
		url += '&ystat=' + 'y'
		url += '&zstat=' + 'z'
		console.log('getLeafletMapData() url:', url)

		$http.get(url)
			.then(function(response) {
				//console.log('getLeafletMapData) response.data:')
				//console.log(response.data)

				mapLeafletData = {}

				mapLeafletData.x = nested_to_float(response.data.x)
				mapLeafletData.y = nested_to_float(response.data.y)
				mapLeafletData.z = nested_to_float(response.data.z)
				//
				mapLeafletData.stackidx = nested_to_float(response.data.stackidx)
				mapLeafletData.dynamics = nested_to_float(response.data.dynamics)
				mapLeafletData.cPnt = nested_to_float(response.data.cPnt)
				mapLeafletData.mapsegment = nested_to_float(response.data.mapsegment)

				mapLeafletData.xstat = 'x'
				mapLeafletData.ystat = 'y'
				mapLeafletData.zstat = 'z'

				console.log('=== getLeafletMapData() mapLeafletData:');
				console.log(mapLeafletData);

				//console.log('getLeafletMapData() leafletRunRow:');
				//console.log(leafletRunRow);

				for (var tp=0; tp<tmpNumTimepoint; tp+=1) {
					//convert mapLeafletData into a new copy (xyzLeaflet[tp]) just for the leaflet timepoint
					getLeafletMapValues(tp, '')
				}
			})
			.catch(function(data, status) {
				$log.info(data)
			})
	}
	
	// make a copy of a column of mapLeafletData for ONE session
	function getLeafletMapValues(tp, mapsegment) {
		console.log('getLeafletMapValues() tp:', tp, 'mapsegment:', mapsegment)
		if (mapsegment == null) {
			mapsegment = ''
		}
				
		// these points are flat. The index gives us the run back into raw mapLeafletData
		// read row i of mapLeafletData.stackidx[i][] to get stack centric spine index in run
		// if mapLeafletData.stackidx[i][j] has a spine then we can snap to it
		
		xyzLeaflet[tp] = {}
		xyzLeaflet[tp].x = mapLeafletData.x.map(function(value,index) { return value[tp]; });
		xyzLeaflet[tp].y = mapLeafletData.y.map(function(value,index) { return value[tp]; });
		xyzLeaflet[tp].z = mapLeafletData.z.map(function(value,index) { return value[tp]; });
		
		console.log('getLeafletMapValues() xyzLeaflet:');
		console.log(xyzLeaflet[tp]);
		
		//
		// tracing
		url = serverurl + 'v2/' + $scope.username + '/' + $scope.loadedMap + '/getmaptracing'
		url += '?mapsegment=' + ''
		url += '&session=' + tp
		url += '&xstat=' + 'x'
		url += '&ystat=' + 'y'
		url += '&zstat=' + 'z'
		//console.log('map tracing url:', url)
		d3.json(url, function(data) {
			//todo: have flask return this
			// we need an array with keys for .find in selectRun
			var length = data.x.length
			xyzTracingLeaflet2[tp] = []
			for (var i=0; i<length; i+=1) {
				var item = {
					'idx': i,
					'x': data.x[i],
					'y': data.y[i],
					'z': data.z[i],
					'ID': data.ID[i],
					'sDist': data.sDist[i],
				}
				xyzTracingLeaflet2[tp].push(item)
			}
			
		  //console.log('xyzTracingLeaflet2[tp]:')
		  //console.log(xyzTracingLeaflet2[tp])
		});
		
	}

    //
    // fill in leaflet dict from xyzLeaflet
    function getLeafletData(tp, theSlice) {
        //console.log('=== getLeafletData() tp:', tp, 'theSlice:', theSlice)

        var zRange = 4 //slices
        var upperBound = theSlice - zRange
        var lowerBound = theSlice + zRange
		if (! $scope.maskPoints) {
			upperBound = -1
			lowerBound = 10000
		}
        //
        // map values
        bicycleRental[tp] = {
            "type": "FeatureCollection",
            "features": [],
        }

        for (var i=0; i<xyzLeaflet[tp].x.length; i++) {
            bicycleRental[tp].features.push(
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            (xyzLeaflet[tp].x[i] / myScale) / pixels_1024_512,
                            webDisplaySize - (xyzLeaflet[tp].y[i] / myScale) / pixels_1024_512 //flipped
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                    	//this is bad, i am switching to FULL data in mapLeafletData
                    	"myColor": getDynamicsColor(mapLeafletData.dynamics[i][tp]), //'#00ffff', //mapLeafletData.dynamics
                        "popupContent": i,
                        "show_on_map": ( theSlice==-1 ? true : (xyzLeaflet[tp].z[i] > upperBound && xyzLeaflet[tp].z[i] < lowerBound) ),
                    },
                    "myTimepoint": tp, //used in callback selectRun0
                    "myRunRow": i, //used in callback selectRun0
                    "id": i //
                },
            )
        }
        
        //
        // tracing
        bicycleRental2[tp] = {
            "type": "FeatureCollection",
            "features": [],
        }

        for (var i=0; i<xyzTracingLeaflet2[tp].length; i++) {
            bicycleRental2[tp].features.push(
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            (xyzTracingLeaflet2[tp][i].x / myScale) / pixels_1024_512,
                            webDisplaySize - (xyzTracingLeaflet2[tp][i].y / myScale) / pixels_1024_512 //flipped
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "popupContent": i,
                        "show_on_map": ( theSlice==-1 ? true : (xyzTracingLeaflet2[tp][i].z > upperBound && xyzTracingLeaflet2[tp][i].z < lowerBound) )
                    },
                    "id": i
                },
            )
        }

    } // getLeafletData

	function getDynamicsColor(type) {
		//1:add, 2:sub, 3:transient, 4:pers
		switch (type) {
			case 1:
				theRet = '#00ff00'
				break;
			case 2:
				theRet = '#ff0000'
				break;
			case 3:
				theRet = '#0000ff'
				break;
			case 4:
				theRet = '#dddd00'
				break;
			default:
				theRet = '#ffffff'
		}
		return theRet
	}
	
	//
	// append icons to leaflet map
	//
	var helloPopup = L.popup().setContent('Hello World!');

	//
	// user spine selection
    //
    $scope.example = {
      value: 12
    };

	// NOT WORKING
	$scope.userSpineSelection = function(tp) {
		console.log('userSpineSelection():', $scope.example.value, 'tp:', tp)

		//console.log('$scope.mapInfo.objMap:')
		//console.log($scope.mapInfo.objMap)

		//todo: can't use .objMap here !!! We are usually plotting a subset of the map
		var runIdx = $scope.mapInfo.objMap[$scope.example.value][tp]
		
		//console.log('runIdx:', runIdx)
		
		//console.log('xyzLeaflet[]:')
		//console.log(xyzLeaflet[tp].x)
		var x = xyzLeaflet[tp].x[runIdx]
		var y = xyzLeaflet[tp].y[runIdx]
		var z = xyzLeaflet[tp].z[runIdx]
		//console.log('x:', x , 'y:', y, 'z:', z)
		
		var tp = 0
		setMapPosition(tp, x, y, z)
		
		var ll = L.latLng;
		ll = um2leaflet(x, y)

		//console.log('marker at:', ll)
		layerGroup[tp].clearLayers()
		L.marker(ll).addTo(layerGroup[tp]);
	}
	
	//
	// toggle: annotations, tracing, and max projection
	$scope.userToggleAnnotations = function() {
		console.log('userToggleAnnotations() ', $scope.showAnnotations)
		for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
			if (! $scope.showTimepoints[currTP]) {
				continue
			}
			redrawLayers(currTP)
		}
	}
	
	$scope.userToggleTracing = function() {
		console.log('userToggleTracing() ', $scope.showTracing)
		for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
			if (! $scope.showTimepoints[currTP]) {
				continue
			}
			redrawLayers(currTP)
		}
	}

	$scope.userToggleTimepointNumber = function() {
		console.log('userToggleTimepointNumber() ', $scope.showTimepointNumber)
		//$scope.$apply();
	}

	$scope.userToggleMaxProject = function() {
		console.log('userToggleMaxProject() ', $scope.showMaxProject)
		for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
			if (! $scope.showTimepoints[currTP]) {
				continue
			}
			if ($scope.showMaxProject) {
				setMaxProject(currTP)
				$scope.maskPoints = false
				getLeafletData(currTP, $scope.currSlice[currTP]) // redraw data with no mask, currSlice is not used here
			} else {
				$scope.maskPoints = true
				setSlice(currTP, $scope.currSlice[currTP])
			}
			// regardless, redraw
			redrawLayers(currTP)
		}
	}

	$scope.userToggleLinkTimepoints = function() {
		console.log('userToggleLinkTimepoints() ', $scope.linkTimepoints)
		
		// grab the current lat/lng/slice of each timepoint
		linkedCenter = []
		for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
			if (! $scope.showTimepoints[currTP]) {
				continue
			}
			linkedCenter[currTP] = leafletRun[currTP].getCenter()
		}
	}

	$scope.userToggleShowSlidingZ = function() {
		console.log('userToggleSlidingZ() ', $scope.showSlidingZ)
	}

	$scope.userToggleshowImageControls = function() {
		console.log('userToggleshowImageControls() ', $scope.showImageControls)
		
		for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
			if (! $scope.showTimepoints[currTP]) {
				continue
			}
			if (! $scope.showImageControls) {
				//leafletRun[currTP].zoomControl = false
				leafletRun[currTP].removeControl(leafletRun[currTP].zoomControl);
				upEasyButton[currTP].remove()
				downEasyButton[currTP].remove()
			} else {
				//leafletRun[currTP].zoomControl = true
				leafletRun[currTP].addControl(leafletRun[currTP].zoomControl);
				upEasyButton[currTP].addTo( leafletRun[currTP] );
				downEasyButton[currTP].addTo( leafletRun[currTP] );
			}
		}
	}

	$scope.userToggleTimepoints = function(tp, show) {
		console.log('=== userToggleTimepoints() tp:', tp, 'show:', show)
		$scope.showTimepoints[tp] = show

		buildMapInterface()

		// not sure why i have to rebuild everything?
		if (show) {
			for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
				if (! $scope.showTimepoints[currTP]) {
					continue
				}
				//console.log('userToggleTimepoints()->redrawLayers()')
				//var theSlice = 0
				//getLeafletData(currTP, theSlice)
				//redrawLayers(currTP)
				
				//addLayers(currTP)

				//leafletRun[currTP].fitBounds(bounds);
				
				//leafletRun[currTP].setView([100,100],0)
			}
		}
	}


///
// end leaflet
//

//
//
  $scope.load = function() {
    console.log('LOADED')
    //alert("Window is loaded");
	
	getMapList($scope.username)
	loadMap('rr30a')

	buildMapInterface()
  }


//$scope.$apply();

///
///

}) //controller

