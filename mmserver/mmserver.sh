# 20171229
# run this script from its home folder PyMapManager/

function usage(){
    echo "mmserver - Illegal parameters"
    echo "Usage:"
    echo "   mmserver start"
    echo "   mmserver stop"
}

# see: https://stackoverflow.com/questions/13322485/how-to-get-the-primary-ip-address-of-the-local-machine-on-linux-and-os-x
getMyIP() {
    local _ip _line
    while IFS=$': \t' read -a _line ;do
        [ -z "${_line%inet}" ] &&
           _ip=${_line[${#_line[1]}>4?1:2]} &&
           [ "${_ip#127.0.0.1}" ] && echo $_ip && return 0
      done< <(LANG=C /sbin/ifconfig)
}

getNumberOfCores() {
	if [[ "$OSTYPE" == "linux-gnu" ]]; then
		#linux
		ncore=$(grep -c processor /proc/cpuinfo)
	elif [[ "$OSTYPE" == "darwin"* ]]; then
		# osx
		ncore=$(sysctl -n hw.physicalcpu)
	fi
	echo "$ncore"
}

getNumberOfWorkers() {
	numWorkers=$(($(getNumberOfCores)*2+1))
	echo "$numWorkers"
}

function serverStart(){
	# check that redis-server is running (used by mmserver:app)
	redisPID=`pgrep -f redis-server`
	if [ -n "$redisPID" ]; then
		echo "=== redis-server already running"
	else
		echo "=== starting redis-server"
		redis-server &
		echo "   sleeping 2 seconds"
		sleep 2
	fi
	
	# 1) unicorn
	unicornPID=`pgrep -f unicorn`
	if [ -n "$unicornPID" ]; then
		echo "unicorn is running, use 'serve_local stop' to stop."
		# exit 1
	else
		echo "=== starting gunicorn rest server with $(getNumberOfWorkers) workers..."
		cd mmserver
		if [[ "$OSTYPE" == "linux-gnu" ]]; then
			# linux
			gunicorn -w $(getNumberOfWorkers) -b 0.0.0.0:5010 mmserver:app &
		elif [[ "$OSTYPE" == "darwin"* ]]; then
		    # Mac OSX
			sudo gunicorn -w $(getNumberOfWorkers) -b 0.0.0.0:5010 mmserver:app &
		fi
		
		cd ..
	fi
	
	# 2) http-server
	#echo '=== starting client side http-server'
	#httpserverPID=`pgrep -f http-server`
	#if [ -n "$httpserverPID" ]; then
	#	echo "http-server is running, use 'serve_local stop' to stop."
	#	exit 1
	#else
	#	echo '=== starting mmclient...'
	#	cd mmclient
	#	http-server &
	#	cd ..
	#fi

	sleep 1
	#echo '=== unicorn and http-server servers running'
	echo '   unicorn rest server is at:'
	echo "      http://$(getMyIP):5010"
	#echo '   http-server client interface is at:'
	#echo "      http://$(getMyIP):8080"
	
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

	#httpserverPID=`pgrep -f http-server`
	#if [ -n "$httpserverPID" ]; then
	#	# we never get here
	#	echo "stopping http-server ..."
	#	sudo kill -9 $httpserverPID
	#	echo "done"
	#else
	#	echo "http-server is not running, use 'serve_local start' to start."
	#	# exit 1
	#fi
	
	#echo 'stopped unicorn and http-server servers'
	echo 'stopped unicorn server'
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

