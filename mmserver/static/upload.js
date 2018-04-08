//20180310

var myApp = angular.module('mmclient_app2', [])
  
myApp.controller('mmclient_controller2', function($scope, $http, $location, $interval, $sce, $timeout, $log) {

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

 $scope.uploadFile = function(files) {
            console.log('uploadFile()')
            $scope.file = new FormData();
            $scope.file.append("file", files[0]);
        };
 $scope.submitGuideDetailsForm= function() {
     console.log('submitGuideDetailsForm()', $scope.file)

	if ($scope.file) {
		fileName = $scope.file.get('file').name
		if (fileName.endsWith('.zip')) {
			//ok
		} else {
			//error
			console.log('please select a zip file')
			return ''
		}
	} else {
		console.log('ERROR XXX')
	}
	
     $scope.uploading = true;
     
     var uploadUrl = '/api/v1/uploadzip/public'
     $http.post(uploadUrl, $scope.file, {
           headers: {'Content-Type': undefined },
           transformRequest: angular.identity,
           
            //see: https://stackoverflow.com/questions/36622826/angular-1-5-4-http-progress-event
            uploadEventHandlers: {
        		progress: function (e) {
                  		if (e.lengthComputable) {
                   			$scope.progressBar = (e.loaded / e.total) * 100;
                    		$scope.progressCounter = $scope.progressBar;
                    		$scope.progressCounter = Math.floor($scope.progressCounter * 100) / 100;
            		    }
    		    }
    		}
    
          }).then(function(results) 
           {   
              $scope.uploading = false;
              $console.log('submitGuideDetailsForm() success load file')
              $console.log('result:', result)
           }).catch(function(error) 
           {
              $scope.uploading = false;
              $console.log('submitGuideDetailsForm() error load file!!!!!')
              $console.log(error);
           });
       };

		$scope.longtask = function() {
			console.log('longtask')
			var longtaskUrl = '/longtask'
			$http.post(longtaskUrl, '')
			.then(function(results)
			{
				console.log('longtask returned');
				console.log('results:', results);
			})
			.catch(function(error)
			{
				console.log('longtask error');
				console.log(error);
			})			
		}
/*
        $.ajax({
            type: 'POST',
            url: '/longtask',
            success: function(data, status, request) {
                status_url = request.getResponseHeader('Location');
                update_progress(status_url, nanobar, div[0]);
            },
            error: function() {
                alert('Unexpected error');
            }
        });
*/
       
//server side events (sse)

	  var source = new EventSource('/event_stream');

      console.log('eventSource.readyState:', source.readyState)
      console.log('eventSource.readyState:', source.url)

      source.onerror = function(eventdata) {
        // relisten if fail to connect to eventsource
        console.log('EventSource source.onerror')
        //this.close();
        //listen();
      }
      source.onopen = function(event){
        console.log('EventSource source.onopen')
      };
      source.onmessage = function(event){
        var tmp = JSON.parse(event.data)
	    
	    $scope.serverstatus = []
	    for (var task in tmp) {
	    	$scope.serverstatus.push(JSON.parse(tmp[task]))
	    }
	    
	    $scope.$apply()
	    
	    console.log('$scope.serverstatus:', $scope.serverstatus)
	    
	   // $scope.serverstatus = tmp
	                
       //     $scope.$apply(function () {
       //         $scope.serverstatus = JSON.parse(event.data)
       //     });

	  };

//get map info for each map
///api/v1/loadmap/<username>/<mapname>
//loadmap(username, mapname)

//build download link for each map
// /api/v1/downloadmap/<username>/<mapname>

$scope.username = 'public'
getMapList($scope.username)

//$scope.longtask()
}) //controller
