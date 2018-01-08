// 20171216

//angular.module('mmclient_app', ['angularjs-dropdown-multiselect'])
//20171226 list [] was empty
angular.module('mmclient_app', [])

.controller('mmclient_controller', function($scope, $http, $location, $interval, $sce, $timeout, $log) {

//disable console.log
//see: https://stackoverflow.com/questions/1215392/how-to-quickly-and-conveniently-disable-all-console-log-statements-in-my-code
//console.log = function() {}

absUrl = $location.absUrl(); // http://127.0.0.1:8000/
host = $location.host()
console.log('absUrl:', absUrl)
console.log('host:', host)

// ip of mmserver rest interface
serverurl = 'http://' + $location.host() + ':5010/'

console.log('serverurl:' + serverurl)

$scope.username = 'public'

$scope.maps = ''
$scope.selectedMap = ''

$scope.loadedMap = ''
$scope.mapInfo = ''

$scope.sessions = null;
$scope.xSelectedSession = 0; //0 corresponds to all
$scope.ySelectedSession = 0; //0 corresponds to all

$scope.mapsegments = null
$scope.selectedMapSegment = 0 // corresponds to all

$scope.showPlotLines = true

// see $scope.toggleInterface('markerColor')
$scope.markerColorList = ["None", "Segment", "Dynamics"]
$scope.selectedMarkerColor = "Dynamics" //have to use double quotes ???

// see $scope.toggleInterface('plotMask')
$scope.plotMaskList = ['All', 'Added', 'Subtracted', 'Transient', 'Always Present']
$scope.selectedPlotMask = "All"

// see $scope.toggleInterface()
$scope.showHistogramx = false
$scope.showHistogramy = false

var xydata = null;

$scope.userRowSelection = null //reassign on changing stats, set null on changing maps

$scope.userClickStackIndex = null
$scope.userClickSessionIndex = null
//$scope.userClickMapSegment = null

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
	'12': 'runIdx',
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

$scope.setSelectedSession = function(xy, index){
	//function that sets the value of selectedSession to current index
	//console.log('setSelectedSession()')
	// index==0 is 'All', others are index-1 for 0 based session
	switch (xy) {
		case 'x':
			$scope.xSelectedSession = index;
			break
		case 'y':
			$scope.ySelectedSession = index;
			break
	}
	if (xydata != null) {
		//myplot0() // this calls rest and then redraws
		updateScatterPlot(xydata)
	}
}

$scope.setSelectedMapSegment = function(index){
	//function that sets the value of selectedMapSegment to current index
	// index==0 is 'All', others are index-1 for 0 based session
	$scope.selectedMapSegment = index;
	console.log('$scope.selectedMapSegment:' + $scope.selectedMapSegment)
	if (xydata != null) {
		//myplot0() // this calls rest and then redraws
		updateScatterPlot(xydata)
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
	var theMapSegment = null
	//if ($scope.selectedMapSegment == 0) {
	//	theMapSegment = null // all map segments
	//} else {
	//	theMapSegment = $scope.selectedMapSegment - 1
	//}
	var theSession = null
	//if ($scope.selectedSession == 0) {
	//	theSession = null // all sessions
	//} else {
	//	theSession = $scope.selectedSession - 1
	//}
	// 20180106, getMapValues() now ignores theMapSegment and theSession
	getMapValues(theMapSegment, theSession, $scope.xStatSelection, $scope.yStatSelection, 'z')
}


// handle marker size slider
dotSize.addEventListener('input', function() {
	console.log('dotSize.value:', dotSize.value)
	Plotly.restyle('scatterPlot', {
		'marker.size': dotSize.value
	}, [0]); // [0] is first trace
});

/*
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
*/

$scope.toggleInterface = function(toggleThis) {
	// variable will already be toggle when we get here
	switch (toggleThis) {
		case 'showHistogramx':
		case 'showHistogramy':
		  	// I want to use restyle for this, how do i restlye layouts 
		  	updateScatterPlot(xydata)
			break;
		case 'showPlotLines':
			if ($scope.showPlotLines) {
				Plotly.restyle('scatterPlot', {
					'mode': 'lines+markers'
				}, [0]); // [0] is first trace
			} else {
				Plotly.restyle('scatterPlot', {
					'mode': 'markers'
				}, [0]); // [0] is first trace
			}
			break
		case 'markerColor':
		  	updateScatterPlot(xydata)
			break
		case 'plotMask':
		  	updateScatterPlot(xydata)
			break
		default:
			console.log('toggleInterface() case not taken:', toggleThis)
			break;
	} //switch
}

// get map list
function getMapList(username) {
	// /api/<username>/maps
	//console.log('getMapList() starting for username:', username)
	var url = serverurl + 'api/' + username + '/maps'
	$http.get(url)
		.then(function(response) {
			$scope.maps = response.data;
			// select the first map
			$scope.selectedMap = $scope.maps[0]
			//console.log('getMapList() finished for username:', username)
			//return $scope.maps
		})
		.catch(function(data, status) {
			console.log('ERROR: getMapList(()')
			$log.info(data)
		})
}

// load a map
function loadMap(map) {
	// http://127.0.0.1:5010/loadmap/public/rr30a
	var url = serverurl + 'loadmap/' + $scope.username + '/' + map
	$scope.loading = true;
	$http.get(url)
		.then(function(response) {
			$scope.mapInfo = response.data // should contain all we need to know abou the map
			
			console.log('=== loadMap()', map, '$scope.mapInfo:')
			console.log($scope.mapInfo)

			$scope.sessions = $scope.mapInfo.importedStackName;
			$scope.sessions.splice(0, 0, 'All'); //insert 'All' sessions at beginning

			$scope.loadedMap = map

			$scope.xSelectedSession = 0; //corresponds to all
			$scope.ySelectedSession = 0; //corresponds to all

			if ($scope.mapInfo.numMapSegments > 0) {
				$scope.selectedMapSegment = 1 // corresponds to FIRST segment, segment 0
			} else {
				$scope.selectedMapSegment = 0 // no map segments, select all
			}
			
			$scope.mapsegments = []
			var i
			for (i=0; i<$scope.mapInfo.numMapSegments; i+=1) {
				$scope.mapsegments[i] = i;
			}
			$scope.mapsegments.splice(0, 0, 'All'); //insert 'All' sessions at beginning

			$scope.userRowSelection = null
			
			//set default x/y stats
			switch ($scope.mapInfo.defaultAnnotation) {
				case 'spineROI':
					$scope.xStatSelection = 'days'
					$scope.yStatSelection = 'pDist'
					break
				case 'otherROI':
					$scope.xStatSelection = 'days'
					$scope.yStatSelection = 'runIdx'
					break;
			}
			
			//globals leaflet
			myScale = $scope.mapInfo.dx[0] // ASSUMING dx==dy AND all sessions are same
			originalPixelsPerLine = $scope.mapInfo.px[0] // ASSUMING
			//var webDisplaySize = 512
			pixels_1024_512 = originalPixelsPerLine/ webDisplaySize
			
			$scope.leafletChannel = $scope.mapInfo.numChannels.toString()

			// plotly scatter plot
			myplot0()
			
			//
			// leaflet
			$scope.leafletMap = $scope.loadedMap //'rr30a'
			buildMapInterface(1)
			getLeafletMapData()
			//redrawLayers0()		
		})
		.catch(function(data, status) {
			$log.info(data)
		})
		.finally(function() {
    	    console.log('This finally block');
    	    $scope.loading = false;
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
	// 20180106, ignore mapsegment and session, always get ALL annotations for given stat
	//if (mapsegment == null) {
	//	mapsegment = ''
	//}
	//if (session == null) {
	//	session = ''
	//}
	mapsegment = ''
	session = ''
	
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
		  
		  console.log('=== getMapValues() xydata:');
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
	//var z = [];
	var colors = [];
	var runRow = []
	var runCol = []

    var scl =['rgb(213,62,79)','rgb(244,109,67)','rgb(253,174,97)','rgb(254,224,139)','rgb(255,255,191)','rgb(230,245,152)','rgb(171,221,164)','rgb(102,194,165)','rgb(50,136,189)'];
	// 1:add, 2:sub, 3:transient, 4:persistent
	var dynamicsColor = ['rgb(0,0,0)', 'rgb(0,255,0)', 'rgb(255,0,0)', 'rgb(0,0,255)', 'rgb(0,0,0)']
	
	console.log('****** updateScatterPlot() xydata:')
	//console.log(xydata)
	
	/*
	I need some way to draw lines but not between runs (rows) and between first/last element
		- Here, I am pushing a nan element to break up each row
		- Flattened array is # rows elements longer than expected -> use click pnt then spineidx[pnt]
	*/
	
	//switching back to this for loop
	// goal is to have if(run has dynamics addiotion) thnen include else don't
		
	numCol = xydata.x[0].length
	var tmpRow = Array(numCol)
	var tmp = []
	//length of x is number of runs!
	for (var i = 0; i < xydata.x.length; i += 1) {
		//only include each run based on current mask (added run, subtracted run, transient run)
		var okGo = 1
		// continue if row does not include map segment
		if ($scope.selectedMapSegment>0) {
			okGo = okGo && xydata.mapsegment[i].includes($scope.selectedMapSegment-1)
			if (! okGo) {
				//console.log('updateScatterPlot() skipping row:', i)
				continue
			}
		}
		//continue if dynamics does not include mask
		switch ($scope.selectedPlotMask) {
			case 'All':
				// all okGo
				break;
			case 'Added':
				okGo = okGo && xydata.dynamics[i].includes(1)
				break;
			case 'Subtracted':
				okGo = okGo && xydata.dynamics[i].includes(2)
				break;
			case 'Transient':
				okGo = okGo && xydata.dynamics[i].includes(3)
				break;
			case 'Always Present':
				// lots of ways to do this, AP is ! added, ! subtracted and ! transient
				okGo = okGo && ! xydata.dynamics[i].includes(1) && ! xydata.dynamics[i].includes(2) && ! xydata.dynamics[i].includes(3)
				break;
			default:
				okGo = 1
				break;
		}
		if (! okGo ) {
			continue
		}
		
		if ($scope.xSelectedSession>0 && $scope.ySelectedSession>0) {
			
			//this is REALLY inefficient, write REST interface to get single session x/y stats
			//
			tmp = Array(numCol).fill(null)
			tmp[$scope.xSelectedSession-1] = xydata.x[i][$scope.xSelectedSession-1] // lhs is x, rhs is x
			x = x.concat(tmp)
			x = x.concat([NaN])
			//
			tmp = Array(numCol).fill(null)
			tmp[$scope.xSelectedSession-1] = xydata.y[i][$scope.ySelectedSession-1] // lhs is x, rhs is y
			y = y.concat(tmp)
			y = y.concat([NaN])
			//
			//tmp = Array(numCol).fill(null)
			//tmp[$scope.xSelectedSession-1] = xydata.z[i][$scope.ySelectedSession-1] // lhs is x, rhs is y
			//z = z.concat(tmp)
			//z = z.concat([NaN])
			//
			tmp = Array(numCol).fill(null)
			switch ($scope.selectedMarkerColor) {
				case 'Dynamics':
					tmp[$scope.xSelectedSession-1] = xydata.dynamics[i][$scope.xSelectedSession-1] // lhs is x, rhs is y
					break
				case 'Segment':
					tmp[$scope.xSelectedSession-1] = xydata.mapsegment[i][$scope.xSelectedSession-1] // lhs is x, rhs is y
					break;
				default:
					tmp[$scope.xSelectedSession-1] = 0
					break;
			}
			colors = y.concat(tmp)
			colors = y.concat([NaN])
			//sloppy here, need to strip down to x/y session
			// book-keeping
			runRow = runRow.concat(Array(numCol).fill(i));
			runRow = runRow.concat([NaN]);
			//
			runCol = runCol.concat(xydata.mapsess[i]); // does not have to be mapsess, just j
			runCol = runCol.concat([NaN]);
		} else {

			//
			x = x.concat(xydata.x[i]);
			x = x.concat([NaN])
			//
			y = y.concat(xydata.y[i]);
			y = y.concat([NaN])
			//
			//z = z.concat(xydata.z[i]);
			//z = z.concat([NaN])
			//
			switch ($scope.selectedMarkerColor) {
				case 'Dynamics':
					colors = colors.concat(xydata.dynamics[i]);
					colors = colors.concat([NaN])
					break;
				case 'Segment':
					colors = colors.concat(xydata.mapsegment[i]);
					colors = colors.concat([NaN])
					break;
				default:
					colors = colors.concat(Array(numCol).fill(0));
					colors = colors.concat([NaN])
					break;
			}
			// book-keeping
			runRow = runRow.concat(Array(numCol).fill(i));
			runRow = runRow.concat([NaN]);
			//
			runCol = runCol.concat(xydata.mapsess[i]); // does not have to be mapsess, just j
			runCol = runCol.concat([NaN]);
		}
	}

	//console.log(' after x:',x)
	//console.log(' after colors:',colors)
	
	// map color index onto rgb
	if ($scope.selectedMarkerColor == 'Dynamics') {
		colors = colors.map(function(obj) {
			var rObj = 'rgb(0,0,0)'
			if (obj >= 1) {
				rObj = dynamicsColor[obj]
			}
			/*
			if (obj==1) {
				rObj = 'rgb(0,255,0)'
			} else if (obj==2) {
				rObj = 'rgb(255,0,0)'
			} else if (obj==3) {
				rObj = 'rgb(0, 0, 255)'
			} else if (obj==4) {
				rObj = 'rgb(0,0,0)'
			}
			*/
			return rObj
		});
		//console.log('***** 2) colors:', colors)
	}
	
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

	var xhist = {
		  x: x,
		  marker: {color: 'rgb(0,0,0)'}, 
		  name: 'x density', 
		  type: 'histogram', 
		  yaxis: 'y2',
		  visible: $scope.showHistogramx
	};
	
	var yhist = {
		  y: y,
		  marker: {color: 'rgb(0,0,0)'}, 
		  name: 'y density', 
		  type: 'histogram', 
		  xaxis: 'x2',
		  visible: $scope.showHistogramy
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
	
	var data = [trace, runSelection, xhist, yhist];

	
	var layout = {
		//scene: {
		//	camera: {
		//		eye: {x: 0.001, y: -2, z: 1},
		//		center: {x: 0, y: 0, z: 0}
		//	}
		//},
		dragmode: 'select',
		hovermode: 'closest',
		showlegend: false,
		xaxis: {
			title: xydata.xstat,
			titlefont: { size: 20 },
			tickfont: { size: 16 },
			zeroline: false,
	        showline : true,
	        autotick: true,
			domain: ($scope.showHistogramy) ? [0, 0.83] : [0,0.99], 
		},
		xaxis2: {
			domain: ($scope.showHistogramy) ? [0.85, 1] : [0.99,1], 
			showgrid: false, 
			zeroline: false,
			visible: $scope.showHistogramy, //thee are swapped
			//layer: 'below traces'
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
			domain: ($scope.showHistogramx) ? [0, 0.83] : [0,0.99], 
		},
		yaxis2: {
			domain: ($scope.showHistogramx) ? [0.85, 1] : [0.99,1], 
			showgrid: false, 
			zeroline: false,
			visible: $scope.showHistogramx //these are swapped
		},
		margin: {
			l: 80, //default i s80
			r: 0,
			t: 40,
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

	//see: https://plot.ly/javascript/lasso-selection/
	/*
	scatterPlotDiv.on('plotly_selected', function(eventData) {
	  console.log('plotly_selected;', eventData)
	  var x = [];
	  var y = [];

	  var colors = [];
	  for(var i = 0; i < N; i++) colors.push(color1Light);

	  console.log(eventData.points)

	  eventData.points.forEach(function(pt) {
		x.push(pt.x);
		y.push(pt.y);
		colors[pt.pointNumber] = color1;
	  });

	  Plotly.restyle(graphDiv, {
		x: [x, y],
		xbins: {}
	  }, [1, 2]);

	  Plotly.restyle(scatterPlotDiv, 'marker.color', [colors], [0]);
	});
	*/

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
	
	//console.log('selRunRow:', selRunRow, 'selRunCol:', selRunCol)
	
	//need to call $scope.$apply() for these to become visible in html
	$scope.userClickStackIndex = xydata.stackidx[selRunRow][selRunCol]
	$scope.userClickSessionIndex = xydata.mapsess[selRunRow][selRunCol]
//todo: check if this exists
//	$scope.userClickMapSegment = xydata.mapsegment[selRunRow][selRunCol]
	//$scope.$apply();
	
	selectInPlotly(selRunRow, selRunCol)
	
  	$scope.$apply(); // to update html showing userClickStackIndex, etc. etc.

	//
	// leaflet
	// if map is rr30a, segment is NOT all, sessions is all
	// to do this I need plotly to get ALL so row is in sync with leaflet
	//console.log('todo: link with leaflet !!!')
	//if ($scope.selectedSession==0 && $scope.selectedMapSegment==0) {
		selectRun(selRunCol, selRunRow)
	//}
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
  	}, [1]) // [1] is user selection trace in plotly layout

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
	$scope.leafletMap = '' //$scope.loadedMap //'rr30a'
	$scope.leafletTimepoint = 0

	$scope.showAnnotations = true
	$scope.showTracing = true
	$scope.showTimepointNumber = true
	
	$scope.showMaxProject = false
	$scope.maskPoints = true
	
	$scope.linkTimepoints = false
	$scope.showSlidingZ = false
	$scope.showImageControls = false
	
	$scope.leafletWidth = 512
	$scope.leafletHeight = 512
	$scope.getLeafletStyle = function () {
		return {
			width: $scope.leafletWidth + 'px',
			height: $scope.leafletHeight + 'px',
		}
	}
	
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
	
    //var myScale = 0.12 //richard
    var myScale = 0.108 // julia
    var originalPixelsPerLine = 1024
    var webDisplaySize = 512
    var pixels_1024_512 = originalPixelsPerLine/ webDisplaySize //1024 is original, 512 is what we are using to display on webpage


	leafletRun = Array(tmpNumTimepoint)
	$scope.image = Array(tmpNumTimepoint)

	$scope.showTimepoints = Array(tmpNumTimepoint)
	$scope.showTimepoints.fill(true)
	
	//$scope.$apply();

	$scope.leafletChannel = "1"
	$scope.channelList = ["1", "2", "3"];
	$scope.setLeafletChannel = function() {
		console.log('=== setLeafletChannel()', $scope.leafletChannel)
		//buildMapInterface(0)
	}

	$scope.leafletMarkerSize = 2
	$scope.setLeafletMarkerSize = function () {
		console.log('setLeafletMarkerSize()')
		for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
			if (! $scope.showTimepoints[currTP]) {
				continue
			}
			redrawLayers(currTP)
		}
	}
	
	$scope.leafletZoom = 2

	function buildMapInterface(forceMaxProject) {
		for (var thisTP=0; thisTP<tmpNumTimepoint; thisTP+=1) {

			if (! $scope.showTimepoints[thisTP]) {
				// this should cause memory problems !!!
				//leafletRun[thisTP] = null
				continue
			}
		
			var thisDIVID = 'myLeafletID' + thisTP
			var thisDIV = document.getElementById(thisDIVID);


			//console.log('building thisTP:', thisTP, 'thisDIV:', thisDIVID)
		
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
			
			//console.log('   madeMap:', madeMap)
			
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

			if (madeMap || forceMaxProject) {
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
			
			if (madeMap || forceMaxProject) {
				setMaxProject(thisTP)
				leafletRun[thisTP].fitBounds(bounds);
			}
						
			// remove this 
			//leafletRun[thisTP].setView([100,100],0)
			
			leafletRun[thisTP].on('click', onMapClick);

			addLayers(thisTP)

			document.getElementById(thisDIVID).addEventListener("keydown", myKeyDown);
			document.getElementById(thisDIVID).addEventListener("keyup", myKeyUp);
			document.getElementById(thisDIVID).addEventListener("wheel", myWheel);
			
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
				redrawLayers()
				//buildMapInterface(1)
				/*
				for (var i=0; i<tmpNumTimepoint; i+=1) {
					if (! $scope.showTimepoints[i]) {
						continue
					}
					leafletRun[i].setView([256,256],0)
				}
				*/
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
				
//
//if no segments, we need to follow global pivot !!!
//
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
	
/*
	//
	// leflet button callbacks
	$scope.loadStackDataButton = function () {
		console.log('loadStackDataButton')
		getLeafletMapData()
	}
*/
	
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
	// need $watch so it updates as it drags (otherwise just updates on mouse up)
	$scope.$watch("imageBrightness", function(){
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
	
/*
	function redrawLayers0() {
		for (var currTP=0; currTP<tmpNumTimepoint; currTP+=1) {
			redrawLayers()
		}
	}
*/
	
//20170108, why did I need to put all this login in here? I did not need it before. What the fuck did I change
	// split this to redraw one or other: xyz or tracing
	function redrawLayers(tp) {
	    //console.log('redrawLayers() tp:', tp)
	    //geoJSON is a one-way controller of data, once set, changing the data will NOT update
		if (myLayer[tp]) {
		    myLayer[tp].clearLayers()
		    if ( $scope.showAnnotations && bicycleRental[tp]) {
			    	myLayer[tp].addData(bicycleRental[tp]);
			}
		}
			    
	   	if (myTracingLayer[tp]) {
	   		myTracingLayer[tp].clearLayers()
	    	if ( $scope.showTracing && bicycleRental2[tp]) {
	    		myTracingLayer[tp].addData(bicycleRental2[tp]);
	    	}
		}
	}
	
	// set the position/pan of leaflet image
	// x,y is in um
	function setMapPosition(tp, x,y,slice) {
		//zoom = leafletRun[0].getZoom()
		var zoom = $scope.leafletZoom
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
					//return L.circleMarker(latlng, geojsonMarkerOptions)
					return L.circleMarker(latlng, {
						radius: $scope.leafletMarkerSize,
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

		mapLeafletData = {}
		mapLeafletData.x = []
		mapLeafletData.y = []
		mapLeafletData.z = []
		//
		mapLeafletData.stackidx = []
		mapLeafletData.dynamics = []
		mapLeafletData.cPnt = []
		mapLeafletData.mapsegment = []

		mapLeafletData.xstat = 'x'
		mapLeafletData.ystat = 'y'
		mapLeafletData.zstat = 'z'

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
		//console.log('getLeafletMapValues() tp:', tp, 'mapsegment:', mapsegment)
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
		
		//console.log('getLeafletMapValues() xyzLeaflet:');
		//console.log(xyzLeaflet[tp]);
		
		//
		// tracing
		url = serverurl + 'v2/' + $scope.username + '/' + $scope.loadedMap + '/getmaptracing'
		url += '?mapsegment=' + ''
		url += '&session=' + tp
		url += '&xstat=' + 'x'
		url += '&ystat=' + 'y'
		url += '&zstat=' + 'z'
		//console.log('map tracing url:', url)
		d3.json(url, function(error, data) {
			//todo: have flask return this
			// we need an array with keys for .find in selectRun
			
			if (error) {
				console.log('getLeafletMapValues() d3.json error')
				xyzTracingLeaflet2[tp] = []
			} else {
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

		buildMapInterface(0)

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
// try this for  sizing map dics
//$timeout(initMap, 0);

  //$scope.load = function() {
	console.log('getMapList() username:', $scope.username)
	getMapList($scope.username)

    //dataPromise.then(function(result) {  
       // this is only run after getMapList() resolves
       //$scope.data = result;
       //console.log("data.name"+$scope.data.name);

		console.log('$scope.maps:', $scope.maps)
	
		console.log('loadMap() rr30a')
		loadMap('rr30a')

		console.log('finished')
    //});
 // }


/*
  $scope.load = function() {
    console.log('LOADED scope.load()')
    //alert("Window is loaded");
	
	getMapList($scope.username)
	loadMap('rr30a')

	// load map is asynchronous, call this from within http response
	//buildMapInterface()
  }
*/

//$scope.$apply();

///
///

}) //controller

