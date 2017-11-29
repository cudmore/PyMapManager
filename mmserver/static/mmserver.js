
angular.module('mmserver_app', ['nvd3'])
.controller('mmserver_controller', function($scope, $http, $location, $interval, $sce, $timeout, $log) {

	$scope.myUrl = $location.absUrl(); //url of page we loaded with port :5000
	console.log("$scope.myUrl:", $scope.myUrl)

    //todo: make 2x functions from getmapvalues(), one for image and another for x/y plot
    //todo: enclose these in $scope.myInterface. struct
    //todo: add sperate session and chanel, one for each of (image plot and x/y plot)
    $scope.user = 'public'
    $scope.map = 'rr30a'
    $scope.session = ''
    $scope.channel = 2
    $scope.ystat = 'y'
    $scope.xstat = 'x'

    $scope.maps = ''
    $scope.sessions = ''
    $scope.channels = ''
    $scope.stats = ''

    $scope.currSlice = 0

    //hide and show interface
    $scope.myInterface = {}
    $scope.myInterface.showImage = 1
    $scope.myInterface.showPlot = 1
    $scope.myInterface.showOld = 0
    $scope.myInterface.showTable = 0

    $scope.getMaps = function (user) {
		$http.get($scope.myUrl + 'api/' + user + '/maps').
        	then(function(response) {
        	    $scope.maps = response.data;
        	    console.log($scope.maps)
        	});
	};

    $scope.getSessions = function (user, map) {
		$http.get($scope.myUrl + 'v2/' + user + '/' + map + '/sessions').
        	then(function(response) {
        	    $scope.sessions = response.data;
        	    //console.log($scope.sessions)
        	});
	};

    $scope.getChannels = function (user, map) {
        $scope.channels = [1,2]
    }

    $scope.getStats = function (user, map) {
        $scope.stats = ['x', 'y', 'z', 'ubssSum_int2', 'ubsdSum_int2', 'pDist', 'session']
    }

    //on selecting a session from list in table
    $scope.setSelectedSession = function(session, idx) {
        console.log('setSelectedSession() session:', session, 'idx:', idx);
        $scope.selectedSession = session;
        $scope.selectedSessionIdx = idx
    };

	$scope.getMaps($scope.user)
	$scope.getSessions($scope.user, $scope.map)
    $scope.getChannels($scope.user, $scope.map)
    $scope.getStats($scope.user, $scope.map)

    //load map on server, does not change js data
    function loadmap(user, map) {
		$http.get($scope.myUrl + 'loadmap' + '/' + user + '/' + map).
        	then(function(response) {
        	    //$scope.mapvalues = response.data;
        	    //console.log('$scope.mapvalues:',$scope.mapvalues)
        	    //console.log('length:',$scope.mapvalues.x.length)
        	});
	}

    //get x/y/z to display on the map
    function getmapvalues0(user, map) {
		xstat = 'x'
		ystat = 'y'
		zstat = 'z' //'ubsdSum_int2' //'pDist'
		//session = $scope.session //$scope.selectedSessionIdx
		session = 0;
		console.log('getmapvalues0()', xstat, ystat, zstat, session)
		//console.log('   $scope.selectedSessionIdx:', $scope.selectedSessionIdx)
		//loads from loaded map
		//extend this to take (map, session)
		$http.get($scope.myUrl + 'getmapvalues' + '?session=' + session + '&xstat=' + xstat + '&ystat=' + ystat + '&zstat=' + zstat)
            .then(function(response) {
        	    //xIsSession = 0
        	    //if ($scope.xStat = 'session') {
        	    //    $scope.xStat = ''
        	    //    xIsSession = 1
        	   // }
        	    //
        	    $scope.mapvalues0 = response.data;
        	    //
        	    // this won't work because $scope.mapvalues is asynch, values have not arrived yet
        	    //if (xIsSession) {
        	    //    $scope.mapvalues.xVal = $scope.mapvalues.ySess
        	    //}
        	    //console.log('getmapvalues() response.data:',response.data)
            })
            .catch(function(data, status) {
                $log.info(data)
            })
 	}

    //image, load data from server into $scope.mapvalues
    //todo: add new function to transform thisx/y/z dict into a leaflet cpoint collection
    function getmapvalues(user, map) {
		console.log('getmapvalues()', '$scope.xstat:', $scope.xstat)
		xstat = $scope.xstat; //'x' //'ubssSum_int2' //'mapsess'
		ystat = $scope.ystat; //'y' //'ubsdSum_int2' //'pDist'
		zstat = 'z' //'ubsdSum_int2' //'pDist'
		session = [] //0
		//loads from loaded map
		//extend this to take (map, session)
		$http.get($scope.myUrl + 'getmapvalues' + '?session=' + session + '&xstat=' + xstat + '&ystat=' + ystat + '&zstat=' + zstat)
            .then(function(response) {
        	    //xIsSession = 0
        	    //if ($scope.xStat = 'session') {
        	    //    $scope.xStat = ''
        	    //    xIsSession = 1
        	   // }
        	    //
        	    $scope.mapvalues = response.data;
        	    //
        	    // this won't work because $scope.mapvalues is asynch, values have not arrived yet
        	    //if (xIsSession) {
        	    //    $scope.mapvalues.xVal = $scope.mapvalues.ySess
        	    //}
        	    //console.log('getmapvalues() response.data:',response.data)
            })
            .catch(function(data, status) {
                $log.info(data)
            })
 	}



///
/// d3
///
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

    //options for d3 x/y plot
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

        //convert mmMap data loaded into $scope.mapvalues to d3 structure
        function generateData2() {
            console.log('generateData2()')
            var data = [],
                shapes = ['circle'],
                random = 2 //d3.random.normal();

            //$scope.mapvalues.mapsegment
            maxMapSegment = Math.max.apply(null, $scope.mapvalues.mapsegment)
            console.log('   generateData2() maxMapSegment:', maxMapSegment)
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

	//
	// buttons
	//

	//load a map
	$scope.loadbutton = function () {
        console.log('loadbutton')
        loadmap($scope.user,$scope.map)
    }

	//display leaflet image
	$scope.displaybutton = function () {
        console.log('displaybutton')
        getLeafletData(-1)
        myLayer.addData($scope.bicycleRental);
    }

	//load d3 stat
	//load x/y/z data for image
	$scope.loadvaluesbutton0 = function () {
        console.log('loadvaluesbutton0')
        getmapvalues0('','')
        console.log('loadvaluesbutton0() $scope.mapvalues:', $scope.mapvalues)
    }

	//load x/y data for plot
	$scope.loadvaluesbutton = function () {
        console.log('loadvaluesbutton')
        getmapvalues('','')
        console.log('loadvaluesbutton() $scope.mapvalues:', $scope.mapvalues)
    }


	//plot d3 stat
	$scope.plotbutton = function () {
        console.log('plotbutton()')

        //d3.selectAll("svg > *").remove();

        $scope.data2 = generateData2();

        $scope.options.chart.yAxis.axisLabel = $scope.ystat
        $scope.options.chart.xAxis.axisLabel = $scope.xstat

        $scope.api.refresh(); //$scope.api appears when i include it in <nvd3> html tag, what the fuck?
        //$scope.api.updateWithData($scope.data2);
        //console.log($scope.ystat)

        //console.log('   plotbutton() $scope.data2:', $scope.data2)
    }

    $scope.setslicebutton = function (plusminus) {
        console.log('setslicebutton()')
        $scope.currSlice += plusminus
        setSlice($scope.currSlice)
    }

//
// Leaflet
//
	function setSlice(sliceNum) {
	    // /getimage/<username>/<mapname>/<int:timepoint>/<int:channel>/<int:slice>
	    console.log('setSlice() sliceNum:', sliceNum)
	    tp = 0
	    channel = 1
	    imageUrl = $scope.myUrl + 'getimage/public/rr30a/0/1/' + sliceNum
	    console.log('imageUrl:', imageUrl)
	    $scope.image.setUrl(imageUrl)
	    //update point masking
	    getLeafletData(sliceNum)

	    //
	    //geoJSON is a one-way controller of data, once set, changing the data will NOT update
	    myLayer.clearLayers()
	    myLayer.addData($scope.bicycleRental);
	}

	var myMap = L.map('mymapid', {
    	crs: L.CRS.Simple
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
		popup2
			.setLatLng(e.latlng)
			//.setContent("You clicked the map at " + e.latlng.toString())
			.setContent("You clicked the map at x:" + userclick.lat + " y:" + userclick.lng)
			.openOn(myMap);
	}
	myMap.on('click', onMapClick);

   //myLayer = L.geoJSON().addTo(myMap); //add bycicle data later with myLayer.addData(geojsonFeature);
        //L.geoJSON([$scope.bicycleRental], {
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
        //console.log('bbb')

    //
    // fill in leaflet data from $scope.mapvalues
    function getLeafletData(theSlice) {
        console.log('getLeafletData() theSlice:', theSlice)

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

        for (var i=0; i<$scope.mapvalues0.x.length; i++) {
            $scope.bicycleRental.features.push(
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            ($scope.mapvalues0.x[i] / myScale) / pixels_1024_512,
                            webDisplaySize - ($scope.mapvalues0.y[i] / myScale) / pixels_1024_512 //flipped
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "popupContent": "spine " + i,
                        "show_on_map": ( theSlice==-1 ? true : ($scope.mapvalues0.z[i] > upperBound && $scope.mapvalues0.z[i] < lowerBound) )
                    },
                    "id": i
                },
            )
        }
        //console.log('$scope.bicycleRental:', $scope.bicycleRental)

        //myLayer = L.geoJSON().addTo(myMap);
        //myLayer.addData($scope.bicycleRental);

////
        ///
        // not sure where to put this code ???
        //
        //handles clicks in map
        //console.log('aaa')
        //bicycleRental is defined in getLeafletData()


 /*
        //L.geoJSON([$scope.bicycleRental], {
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
        //console.log('bbb')
*/
////

        ///
    } // getLeafletData


///
// end leaflet
//

}); //controller
