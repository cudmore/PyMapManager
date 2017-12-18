// 20171216

angular.module('mmserver_app', [])
.controller('mmserver_controller', function($scope, $http, $location, $interval, $sce, $timeout, $log) {

serverurl = 'http://127.0.0.1:5010'

$scope.username = 'public'

$scope.maps = ''
$scope.selectedMap = ''

$scope.sessions = null;
$scope.selectedSession = 0; //corresponds to all

$scope.mapsegments = null
$scope.selectedMapSegment = 0 // corresponds to all

var xydata = null;

$scope.statList = {
	'1': 'session',
	'2': 'x',
	'3': 'y',
	'4': 'z',
	'5': 'pDist',
	'6': 'ubssSum_int1',
	'7': 'ubsdSum_int1',
}
$scope.xStatSelection = 'ubsdSum_int1'
$scope.yStatSelection = 'ubssSum_int1'

$scope.setSelecetedMap = function(map) {
	console.log('setSelecetedMap():' + map)
	$scope.selectedMap = map
}

$scope.setSelectedStat = function(xy, stat){
	//console.log('setSelectedStat()' + xy + stat)
	if (xy == 'x') {
		$scope.xStatSelection = stat;
		console.log('$scope.xStatSelection:' + $scope.xStatSelection)
	} else {
		$scope.yStatSelection = stat;
		console.log('$scope.yStatSelection:' + $scope.yStatSelection)
	}
	if (xydata != null) {
		myplot()
	}
}

$scope.setSelectedSession = function(index){  //function that sets the value of selectedSession to current index
	console.log('setSelectedSession()')
	// index==0 is 'All', others are index-1 for 0 based session
	$scope.selectedSession = index;
	//console.log('$scope.selectedSession:' + $scope.selectedSession)
	if (xydata != null) {
		myplot()
	}
}

$scope.setSelectedMapSegment = function(index){  //function that sets the value of selectedSession to current index
	//console.log('setSelectedMapSegment()')
	// index==0 is 'All', others are index-1 for 0 based session
	$scope.selectedMapSegment = index;
	//console.log('$scope.selectedMapSegment:' + $scope.selectedMapSegment)
	if (xydata != null) {
		myplot()
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
//	myplot()
//});

function myplot() {
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
			console.log($scope.maps)
		})
		.catch(function(data, status) {
			$log.info(data)
		})
}

// load a map
// http://127.0.0.1:5010/loadmap/public/rr30a
function loadMap(map) {
	url = serverurl + '/loadmap/public/' + map
	d3.json(url, function(error, data) {
	  if (error) {
	  	console.log('error: loadMap()')
	  }
	  getSessions()
	  getMapSegments()
	  myplot()
	  console.log(data);
	});
}

// get sessions (the stack names)
// /v2/<username>/<mapname>/<item>
function getSessions() {
	// for some reason d3.json() did not work here?
	url = serverurl + '/v2/public/rr30a/sessions'
	$http.get(serverurl + '/v2/public/rr30a/sessions')
		.then(function(response) {
			$scope.sessions = response.data;
			$scope.sessions.splice(0, 0, 'All'); //insert 'All' sessions at beginning
			console.log($scope.sessions)
		})
		.catch(function(data, status) {
			$log.info(data)
		})
}

// get map segments
// /v2/<username>/<mapname>/<item>
function getMapSegments() {
	// for some reason d3.json() did not work here?
	url = serverurl + '/v2/public/rr30a/mapsegments'
	$http.get(url)
		.then(function(response) {
			$scope.mapsegments = response.data;
			$scope.mapsegments.splice(0, 0, 'All'); //insert 'All' sessions at beginning
			console.log($scope.mapsegments)
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
	  console.log(xydata);
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

	var layout = {
		//scene: {
		//	camera: {
		//		eye: {x: 0.001, y: -2, z: 1},
		//		center: {x: 0, y: 0, z: 0}
		//	}
		//},
		xaxis: {
			title: xydata.xstat
		},
		yaxis: {
			title: xydata.ystat
		},
		//margin: {
		//	l: 0,
		//	r: 0,
		//	t: 0,
		//	b: 0,
		//	pad: 0
		//}
	};

	//layout.scene.xaxis = {title: xydata.xstat} //, range: [0, 255]};
	//layout.scene.yaxis = {title: xydata.ystat} //, range: [0, 255]};
	//layout.scene.zaxis = {title: xydata.zstat} //, range: [0, 255]};

	Plotly.purge('scatterPlot');
	Plotly.newPlot('scatterPlot', data, layout, {
		displayModeBar: false
	});
	scatterPlot.on('plotly_click', function(data){
	    //alert('You clicked this Plotly chart!');
	    console.log('plotly_click data:')
	    console.log(data)
	});
} //updateScatterPlot

// getMapValues(1, 'x', 'y', 'z')
// updateScatterPlot(xydata)
getMapList($scope.username)

}); //controller
