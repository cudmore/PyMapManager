var app = angular.module('plunker', ['nvd3']);

app.controller('MainCtrl', function($scope, $location, $http) {

 	$scope.myUrl = $location.absUrl(); //with port :5000
    console.log('myUrl:' + $scope.myUrl)

   //todo: make the length of this follow max mapsegments
   var colorArray = ['#000000', '#660000', '#CC0000', '#FF6666', '#FF3333', '#FF6666', '#FFE6E6'];
   $scope.colorFunction = function() {
	    return function(d, i) {
    	    //console.log('this should be broken down by mapsegment, colorFunction:', i)
    	    return colorArray[i] //'#00aa00'
        };
    }

    $scope.shapeCrossFunction = function() {
        return function(d) {
            return 'square';
        };
    }

    $scope.options = {
            chart: {
                type: 'scatterChart',
                height: 450,
                width: 450,
                color: $scope.colorFunction(),
                scatter: {
                    onlyCircles: false,
                    shape: $scope.shapeCrossFunction()
                },
                showDistX: true,
                showDistY: true,
                tooltipContent: function(key) {
                    return '<h3>' + key + '</h3>';
                },
                duration: 350,
                useInteractiveGuideLine: true,
                xAxis: {
                    axisLabel: 'X Axis',
                    tickFormat: function(d){
                        return d3.format('.02f')(d);
                    }
                },
                yAxis: {
                    axisLabel: 'Y Axis',
                    tickFormat: function(d){
                        return d3.format('.02f')(d);
                    },
                    axisLabelDistance: -5
                },
                zoom: {
                    //NOTE: All attributes below are optional
                    enabled: true,
                    scaleExtent: [1, 10],
                    useFixedDomain: false,
                    useNiceScale: false,
                    horizontalOff: false,
                    verticalOff: false,
                    unzoomEventType: 'dblclick.zoom'
                }
            }
    };

       /* Random Data Generator (took from nvd3.org) */
        function generateData2(groups, points) {
            var data = [],
                shapes = ['circle'],
                random = 2 //d3.random.normal();

            getmapvalues('','')

            //$scope.mapvalues.mapsegment
            maxMapSegment = Math.max.apply(null, $scope.mapvalues.mapsegment)
            console.log('maxMapSegment:', maxMapSegment)
            for (var i=0; i<=maxMapSegment; i++) {
                data.push({
                    key: 'Segment ' + i,
                    values: []
                })
            }

            // get x/y pairs from mmMap.getMapValue() and push EACH x/y pair
            myLength = $scope.mapvalues.x.length
            for (var i=0; i<myLength; i++) {
                    // use mapvalues.mapsegment[i] to push into different data[mapsegment]
                    mapsegment = $scope.mapvalues.mapsegment[i]
                    //console.log('b- mapsegment:', mapsegment)
                    data[mapsegment].values.push({
                        x: $scope.mapvalues.x[i]
                        , y: $scope.mapvalues.y[i]
                        , size: 2 //Math.random()
                        //, color: '#00AA00'
                        //, shape: 'square'
                    });
            }
            return data;
        }
    //add new function to transform thisx/y/z dict into a leaflet cpoint collection
    function getmapvalues(user, map) {
		xstat = 'x' //'ubssSum_int2' //'mapsess'
		ystat = 'y' //'ubsdSum_int2' //'pDist'
		zstat = 'z' //'ubsdSum_int2' //'pDist'
		//loads from loaded map
		//extend this to take (map, session)
		$http.get('http://127.0.0.1:5010/getmapvalues' + '?xstat=' + xstat + '&ystat=' + ystat + '&zstat=' + zstat).
        	then(function(response) {
        	    $scope.mapvalues = response.data;
        	    console.log('$scope.mapvalues:',$scope.mapvalues)
        	    makeLeaflet()
        	});
	}

    function loadmap(user, map) {
		$http.get('http://127.0.0.1:5010/loadmap' + '/' + user + '/' + map).
        	then(function(response) {
        	    //$scope.mapvalues = response.data;
        	    //console.log('$scope.mapvalues:',$scope.mapvalues)
        	    //console.log('length:',$scope.mapvalues.x.length)
        	});
	}

	$scope.plotbutton = function () {
        console.log('plotbutton')
        getmapvalues('','')
        $scope.data2 = generateData2(4,40);
        //$scope.data = generateData(4,40);
    }

//
//
//todo: having problems sharing global 'var' between .js files ???
//todo: having problems sharing funcitons between .js files
function makeLeaflet() {
console.log('mapvalues:',$scope.mapvalues)

//myData = {}
//myData.x = [100,200,300,400,500]
//myData.y = [100,200,300,400,500]
//myData.z = [1,2,3,4,5]

$scope.bicycleRental = {
    "type": "FeatureCollection",
    "features": []
}

for (var i=0; i<$scope.mapvalues.x.length; i++) {
    $scope.bicycleRental.features.push(
        {
            "geometry": {
                "type": "Point",
                "coordinates": [
                    $scope.mapvalues.x[i],
                    $scope.mapvalues.y[i]
                ]
            },
            "type": "Feature",
            "properties": {
                "popupContent": "spine " + i
            },
            "id": i
        },
    )
}
console.log('$scope.bicycleRental:', $scope.bicycleRental)
}

//
//

    user = 'public'
    map = 'rr30a'
    loadmap(user,map)
});
