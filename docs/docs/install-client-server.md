## Web based browsing

Once the PyMapManager `mmclient` and `mmserver` are running, there is a point and click web interface to browse Map Manager annotations and images.

### Browsing annotations

<IMG SRC="../img/mmserver_purejs.png">

### Browsing images

<IMG SRC="../img/mmserver_leaflet.png">
<IMG SRC="../img/mmserver_leaflet2.png">


## Overview

PyMapManager can serve Map Manager annotations and images using a client/server model. We use two different servers to acheive this

 1. `mmserver/mmserver.py` : Python Flask server to provide a REST interface so a web browser can retrieve Map Manager annotations and images.
 2. `mmclient/index.html` : A front end point-and-click web-browser interface allowing Map Manager annotations and images to be visualized.
 

## 1) Installing software to run the servers

This will work well if you only want to check out the servers. This is not designed for final production which should use Apache or nginx (as opposed to manually running gunicorn and http-server). For final production servers, nginx serves the mmclient Javascript and forwards the REST requests to mmserver using uwsgi.

Running the servers requires some additional software

 - `mmserver`: Requires redis and gunicorn
 - `mmclient`: Requires node npm and http-server

### Make sure you have redis

	sudo apt-get redis
	
	redis-cli ping
	# should respond
	PONG

### Make sure you have gunicorn

Wrapping the `mmserver` to run inside of gunicorn provides a **synchronous** web server. This should handle fast interaction with the web interface much better than the **asynchronous** version provided by `python mmserver.py`. This is most noticeable when viewing linked sliding z-projections.

	pip install gunicorn
	
### Make sure you have Node npm and http-server

Node install changes based on your flavor of linux, see [node install instruction](https://nodejs.org/en/download/package-manager/).

	# on debian jessie
	curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -
	sudo apt-get install -y nodejs
	
	# install http-server
	sudo npm install http-server -g
	
## 2) Install PyMapManager

### Clone the repository

This makes a `PyMapManager` folder

	git clone https://github.com/cudmore/PyMapManager.git
	
### Make a virtual environment `mm_env` and activate it

	virtualenv mm_env
	source mm_env/bin/activate

### Install PyMapManager

	# install PyMapManager
	pip install -e PyMapManager/
	

### Install dependencies for `mmserver`

	pip install -r PyMapManager/mmserver/requirements.txt
		
## 3) Either, run the servers with a script

Start both unicorn and http-server with our [`PyMapManager/serve_local.sh`][serve_local] script.

### Start the servers with

```
cd PyMapManager
./serve_local.sh start
```
	
### Stop the servers with

```
cd PyMapManager
./serve_local.sh stop
```

### Access local servers

The front-end client can be accessed at

```
http://localhost:8080
```

The back-end REST server can be accessed at

```
http://localhost:5010/help
```

## 4) Or, run the servers manually

### Run the REST server

On OSX, use `sudo`, on linux **do not**.

	#osx
	cd PyMapManager/mmserver
	sudo gunicorn -w 4 -b 0.0.0.0:5010 mmserver:app
	
	#linux
	gunicorn -w 4 -b 0.0.0.0:5010 mmserver:app

#### Check the rest server

Here `server_ip` is the IP address of your server

	http://server_ip:5010

### Run the mmclient Javascript client

	cd PyMapManager/mmclient
	http-server

The output should look like this

```
Starting up http-server, serving ./
Available on:
  http://127.0.0.1:8080
  http://192.168.1.10:8080
Hit CTRL-C to stop the server
```
	
#### View the mmclient at

Here `server_ip` is the IP address of your server

	http://server_ip:8080

## [REWRITE THIS TO USE PROPER FORWARDING IN nginx USING uwsgi] Running the client/server on a Linux system with a pre-existing web-server

This requires a pre-existing web server to serve both the client server `mmclient/index.html` and the Python Flask REST server `mmserver/mmserver.py`.

We have used `nginx` with success.

 - Get a debian system
 - Install nginx
 
```
sudo apt-get install nginx
```
 	
 - Copy the `mmclient/` folder into `/var/www/html/mmclient`

```
sudo cp PyMapManager/mmclient /var/www/html/
```

 - You can now access the mmclient as http://nginx_server_ip/mmclient

 - Make sure the client in `mmclient/static/mmserver.js` is pointing to the REST server (we will run that next).

```
sudo pico /var/www/html/mmclient/static/mmserver.js
   
# make sure the file has
serverurl = 'http://nginx_server_ip:5010/'
```
   
 - Run the Flask server with

```
cd mmserver
screen
gunicorn -b 0.0.0.0:5010 mmserver:app
# exit screen with ctrl+a then d 
```
   
This runs the Flask app `app` in the python file `mmserver.py` at the address `http://nginx_server_ip:5010`. We have used `screen` so that when you logout of the terminal, the server continues to run. If you need to stop the server, you can use `PyMapManager/serve_local.sh stop` or return to the `screen` session with `screen -r` and hit ctrl+c.

Check the REST server manually by browsing to

```
http://nginx_server_ip:5010/help
```

If that all works, you can browse some maps at

```
http://nginx_server_ip/mmclient
```
 
This will serve the `mmclient/index.html` and use the `mmclient/static/mmserver.js` file. The `mmclient/static/mmserver.js` file will grab annotations and images from the `mmserver/mmserver.py` REST server via `http://nginx_server_ip:5010`.

[serve_local]: https://github.com/cudmore/PyMapManager/blob/master/serve_local.sh

