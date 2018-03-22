//20180310

angular.module('mmclient_app2', [])

.controller('mmclient_controller2', function($scope, $http, $location, $interval, $sce, $timeout, $log) {

console.log('download.js')

absUrl = $location.absUrl(); // http://127.0.0.1:8000/
host = $location.host();
console.log('absUrl:', absUrl);
console.log('host:', host);

var port = $location.port();

// ip of mmserver rest interface
serverurl = 'http://' + $location.host() + '/' //':5000/';

if (port != 80) {
	serverurl = 'http://' + host + ':' + port + '/'
}

console.log('serverurl:' + serverurl);

// get map list
function getMapList(username) {
	// /api/<username>/maps
	//console.log('getMapList() starting for username:', username)
	var url = serverurl + 'api/v1/maplist/' + username
	$http.get(url)
		.then(function(response) {
			$scope.maps = response.data;

			console.log('$scope.maps:', $scope.maps)
			
			$scope.mapList = []; // create an empty array

			for (var i in $scope.maps) {
				var tmpStr = serverurl + 'api/v1/downloadmap/' + $scope.username + '/' + $scope.maps[i]
				$scope.mapList.push({
    				name: $scope.maps[i],
    				link: $sce.trustAsHtml('<A HREF="' + tmpStr + '">download</A>')
				});
			}
			console.log($scope.mapList);
		})
		.catch(function(data, status) {
			console.log('ERROR: getMapList(()')
			$log.info(data)
		})
}

//get map info for each map
///api/v1/loadmap/<username>/<mapname>
//loadmap(username, mapname)

//build download link for each map
// /api/v1/downloadmap/<username>/<mapname>

$scope.username = 'public'
getMapList($scope.username)


}) //controller
