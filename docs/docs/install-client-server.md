## Web based browsing

Once the PyMapManager client/server servers are running, there is a point and click web interface to browse Map Manager annotations and images.

### Browsing annotations

<IMG SRC="../img/mmserver_purejs.png">

### Browsing images

<IMG SRC="../img/mmserver_leaflet.png">
<IMG SRC="../img/mmserver_leaflet2.png">


## Overview

PyMapManager can serve Map Manager annotations and images using a client/server model. We use two different servers to acheive this

 1. `mmserver/mmserver.py` : Python flask server to provide a REST interface so a web browser can retrieve Map Manager annotations and images
 2. `mmclient/index.html` : A front end point-and-click web-browser interface allowing Map Manager annotations and images to be visualized.
 


## 1) Installing software to run the servers

The `mmserver/mmserver.py` Flask REST server requires the following Python libraries

```
pip install flask
pip install flask-cors
pip install scikit-image
```

Running the servers requires `gunicorn` for the mmserver Flask REST server and `http-server` for the mmclient server.

```
pip install gunicorn

# this assumes you have node and npm install
npm install http-server -g
```

This is only one way of running these two servers. If you want to run them a different way you are free to do this.
	
## 2) Starting the client/server for local use (basic)

Start both unicorn and http-server with our `PyMapManager/serve_local.sh` script.

This will work well if you are only going to be browsing the client/server from the same machine. This will work on MacOS (and Linux).

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
	
## 3) Manually start both client and server servers

### Start the `mmserver/mmserver.py` REST server
 
```
cd mmserver
python mmserver.py
```

Test this out by pointing a web browser to

```
http://127.0.0.1:5010/help
```

Alternatively, start the `mmserver.py` REST server with gunicorn

```
cd mmserver
gunicorn -b 127.0.0.1:5010 mmserver:app
```
	
Wrapping the `mmserver` to run inside of gunicorn provides a **synchronous** web server. This should handle fast interaction with the web interface much better than the **asynchronous** version provided by `python mmserver.py`. This is most noticeable when viewing linked sliding z-projections.

### Start the `mmclient/index.html` client server

This is assuming you have node and npm installed. In addition, we are assuming you have used npm to install http-server with `npm install http-server -g`.

Make sure `mmclient/static/mmserver.js` points to the REST interface. This file should have

```
serverurl = 'http://127.0.0.1:5010/'
```
	
Run the mmclient client server

```
cd mmclient
http-server
```

The output should look like this

```
Starting up http-server, serving ./
Available on:
  http://127.0.0.1:8080
  http://192.168.1.10:8080
Hit CTRL-C to stop the server
```

You can then browse the client server at

```
http://127.0.0.1:8080
```
	

## 4) Running the client/server on a Linux system with an existing web-server

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
 
This will serve the `mmclient/index.html` and use the `mmclient/static/mmserver.js` file. The `mmclient/static/mmserver.js` file will grab annotations and images from the `mmserver/mmserver.py` Python Flask REST server via `http://nginx_server_ip:5010`.


