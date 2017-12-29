
## Install pyMapManager Python package

### Download the repo

	git clone https://github.com/cudmore/PyMapManager.git
	
### Install PyMapManager

	pip install -e PyMapManager
	
From within Python, include the libraries like:

	from pymapmanager import mmMap
	
## Install `mmserver.py`

The `mmserver.py` Flask server requires the following libraries

	pip install flask
	pip install flask-cors
	pip install scikit-image

### Starting the server for local use

This will work well if you are only going to be browsing the server from the same machine.

	python mmserver.py

Point your browser to

	http://127/0/0/1:5010

### Starting the server for wider use

 - Get a debian system
 - Install nginx
 - put into /var/www/html/mmclient
   - index.html
   - /static/ folder
 - You can now access mmclient as http://nginx_server_ip/mmclient
 - run the Flask server with
   gunicorn -b 0.0.0.0:5010 mmserver:app
   
 - modify mmserver.js to point to the Flask server (this is now just a rest server)
   - something like http://nginx_server_ip:5010
   
 - browse to http://nginx_server_ip/mmclient and browse some maps
 
This will serve the index.html using the mmserver.js file. The .js file will talk to the mmserver REST server via http://nginx_server_ip:5010

todo:

1) I can put mmserver.py plus /data/ into /var/www/html/mmserver.

2) Then point mmserver.js to http://cudmore.duckdns.org/mmserver

3) I need to configure nginx to take http://nginx_server_ip/mmRest and point it to the gunicorn process?

Starting the server with `python mmserver.py` will run Flask as a single **asynchronous** process. Problems will arise when multiple requests are made rapidly and the Flask server is still processing the last request. This mostly happens when using sliding z-projection images. To solve this, Flask needs to be run inside a **synchronous** web server such as gunicorn.

If needed, install gunicorn

	pip install gunicorn

Start the Flask server inside gunicorn

	# on osx (requires sudo)
	sudo gunicorn -bind 0.0.0.0:5010 mmserver:app

	# on debian
	gunicorn -b 0.0.0.0:5010 mmserver:app
		
On another machine, point a browser to the ip address of the machine running the server

	http://ip:5010
	
## Install the Qt desktop app

	Not done yet	
	