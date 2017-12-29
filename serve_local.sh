# 20171229

function usage(){
    echo "serve_local - Illegal parameters"
    echo "Usage:"
    echo "   serve_local start"
    echo "   serve_local stop"
}

function serverStart(){
	# 1) unicorn
	unicornPID=`pgrep -f unicorn`
	if [ -n "$unicornPID" ]; then
		echo "unicorn is running, use 'serve_local stop' to stop."
		# exit 1
	else
		echo '=== starting gunicorn rest server'
		cd mmserver
		sudo gunicorn -b 127.0.0.1:5010 mmserver:app &
		cd ..
	fi
	
	# 2) http-server
	echo '=== starting client side http-server'
	httpserverPID=`pgrep -f http-server`
	if [ -n "$httpserverPID" ]; then
		echo "http-server is running, use 'serve_local stop' to stop."
		exit 1
	else
		echo '=== starting mmclient'
		cd mmclient
		http-server &
		cd ..
	fi

	echo '=== unicorn and http-server servers running'
	echo '   this assumes mmclient.js has:'
	echo "      serverurl = 'http://127.0.0.1:5010/'"
	echo '   unicorn rest server is at:'
	echo '      http://127.0.0.1:5010'
	echo '   http-server client interface is at:'
	echo '      http://127.0.0.1:8080'
	
}

function serverStop(){
	unicornPID=`pgrep -f unicorn`
	if [ -n "$unicornPID" ]; then
		# we never get here
		echo "stopping unicorn ..."
		sudo kill -9 $unicornPID
		echo "done"
	else
		echo "unicorn is not running, use 'serve_local start' to start."
		# exit 1
	fi

	httpserverPID=`pgrep -f http-server`
	if [ -n "$httpserverPID" ]; then
		# we never get here
		echo "stopping http-server ..."
		sudo kill -9 $httpserverPID
		echo "done"
	else
		echo "http-server is not running, use 'serve_local start' to start."
		# exit 1
	fi
	
	echo 'stopped unicorn and http-server servers'
}

if [ "$#" -ne 1 ]; then
    usage
    exit 1
fi

case "$1" in
	start) serverStart
		;;
	stop) serverStop
		;;
	*) usage
		;;
esac

exit 0

