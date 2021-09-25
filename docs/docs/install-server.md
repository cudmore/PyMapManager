## Web based browsing

The PyMapManager server allows Map Manager annotations and time-series images to be browsed with a web interface. It is really easy to run the server on your local machine. For a production level server we provide a Docker container.

### Browsing annotations

<IMG SRC="../img/mmserver_purejs.png">

### Browsing images

<IMG SRC="../img/mmserver_leaflet.png">
<IMG SRC="../img/mmserver_leaflet2.png">


## Download

To run the server locally, you need some data! Example data can be downloaded from the PyMapManager-Data repository. The first thing to do is to clone both the [PyMapManager][pymapmanager] and the [PyMapManager-Data][pymapmanager-data] repositories.

	git clone  --depth=1 https://github.com/cudmore/PyMapManager.git
	git clone  --depth=1 https://github.com/mapmanager/PyMapManager-Data.git

## Running the server.

## 1) Using Python

Simplest case is to use `python mmserver.py` and you should be up in no time. Please note, while this method is easy, it runs the server as a single thread/worker and the interface will be slower than it should be.

	# work from PyMapManager folder
	cd PyMapManager

	# create a virtual environment in folder `mm_env`
	python -m venv mm_env

	# activate virtual environment
	source mm_env/bin/activate

	# install pymapmanager (-e will allow you to change source code)
	pip install -e .

	# install required server libraries
	pip install -r mmserver/requirements.txt

	# run the server
	cd mmserver
	python mmserver.py

Point your browser to `http://localhost:5000` and have fun browsing.

## 2) Using the Docker container

Running the server from within a Docker container has lots of benefits. First off, the Docker container spins up a proper [nginx][nginx] web server and runs multiple copies of the python code in mmserver.py. With this system, the server is really responsive even when multiple requests are coming in fast as happens when images are scrolled.

To get started, download and install [Docker Community Edition (CE)][docker ce].

## 2.1) Using docker-compose

If you want to run the server inside a [Docker][docker] container, the easiest option is to use `docker-compose`. Using this technique makes a very efficient production level server and is exactly the same code-base we use to make world accessible PyMapManager site.

### Build

	cd PyMapManager
	docker-compose build # this will take a few minutes the first time it is run

### Run

	docker-compose up

Point your browser to `http://localhost` and have fun browsing.

### Stop

	docker-compose down

	# stop all docker containers
	docker stop $(docker ps -aq)

## 2.2) Using docker

If you prefer to run the docker services separately and specify paths on the command line.

### Build

	cd PyMapManager
	docker build -t myimage . # the dot is important

### Redis

	docker run -d --name redis -p 6379:6379 redis

### Nginx server

In the following docker command, `/Users/cudmore/Dropbox/PyMapManager-Data` has to be changed to point to the full path of your local copy of `PyMapManager-Data`.

	cd PyMapManager
	docker run --name mycontainer -p 80:80 -v /Users/cudmore/Dropbox/PyMapManager-Data:/PyMapManager-Data --link redis myimage

Point your browser to `http://localhost` and have fun browsing.

### Stop

	docker stop mycontainer
	docker rm mycontainer

	docker stop redis
	docker rm redis

[duckdns]: http://cudmore.duckdns.org
[pymapmanager]: https://github.com/cudmore/PyMapManager
[pymapmanager-data]: https://github.com/mapmanager/PyMapManager-Data
[nginx]: https://www.nginx.com/
[uwsgi]: https://uwsgi-docs.readthedocs.io/en/latest/
[redis]: https://redis.io/
[docker]: https://www.docker.com/community-edition
[docker ce]: https://docs.docker.com/install/
