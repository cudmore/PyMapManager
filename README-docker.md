## Purpose

This will run a **local** web server creating a user-interface to browse Map Manager time-series annotations and images.

## Important

To run the server locally, you need some data! Example data can be downloaded from the PyMapManager-Data repository. The first thing to do is to clone the main `PyMapManager` and the `PyMapManager-Data` repositories.

	git clone https://github.com/cudmore/PyMapManager.git
	git clone https://github.com/cudmore/PyMapManager-Data.git
		
This should put both PyMapManager and PyMapManager-Data in the same directory, for example:

	/User/me/PyMapManager
	/User/me/PyMapManager-Data

## Running the server.

Simplest case is to use `python mmserver.py` and you should be up in no time. This does have limitations in that the server is run as a single thread/worker. Repeated requests, as occur when scrolling linked images, will cause the server to choke. Don't worry, you won't break anything, it will just be slow. This is why running behind a proper [nginx][nginx]+[uwsgi][uwsgi] web-sever is way better.

## 1) Using `python mmserver.py`

### Start redis-server

You need a redis-server running. Install it on OSX with `brew install redis-server` or on most variants of Linux with `sudo apt-get install redis-server`. See [redis][redis] homepage for more info.

	redis-server
	
### Start mmserver

	cd PyMapManager/app
	python mmserver.py

Point your browser to `http://localhost:5000` and have fun browsing.

### Stop redis-server

	redis-cli shutdown
	
## 2.1) Using docker-compose

If you want to run the server inside a [Docker][docker] container, the easiest option is to use `docker-compose`. Using this technique makes a very efficient server and is exactly what we are using at [http://cudmore.duckdns.org][http://cudmore.duckdns.org].

### Setup

In `docker-compose.yml`, change the path `/Users/cudmore/Dropbox/PyMapManager-Data` to the full path to your local copy of `PyMapManager-Data`. This little hoop is due to a bug in Docker and will be fixed.

    volumes:
      - /Users/cudmore/Dropbox/PyMapManager-Data:/PyMapManager-Data

### Build

	docker-compose build

### Run

	docker-compose up

Point your browser to `http://localhost` and have fun browsing.
	
### Stop

	docker-compose down	
	
### Troubleshoot

	docker-compose run web bash

## 2.2) Using docker

If you prefer to run the docker services separately and specify paths on the command line.

### Build

	cd PyMapManager
	docker build -t myimage .

### Redis

	docker run -d --name redis -p 6379:6379 redis

### Run and mount a local volume in docker

You need to change `/Users/cudmore/Dropbox/PyMapManager-Data` to point to the full path of your local copy of `PyMapManager-Data`. Remember, both `PyMapManager` and `PyMapManager-Data` need to be in the same folder.

	cd PyMapManager
	docker run --name mycontainer -p 80:80 -v /Users/cudmore/Dropbox/PyMapManager-Data:/PyMapManager-Data --link redis myimage

Point your browser to `http://localhost` and have fun browsing.

### Stop

	docker stop mycontainer
	docker rm mycontainer

## Open source

Made possible by open-source software to the nth degree.

- Docker - containers are the future
- nginx - web server
- uwsgi - web standard for nginx to talk to python

- Python (back-end)
 - flask
 - numpy
 - pandas
 - scipy
 - matplotlib
 - tifffile
 
- Javascript (front-end)
 - Angular
 - JQuery
 - d3
 - Leaflet
 - Plotly
 - Bootstrap

- [tiangolo/uwsgi-nginx-flask:python3.6](https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/)

[nginx]: https://www.nginx.com/
[uwsgi]: https://uwsgi-docs.readthedocs.io/en/latest/
[redis]: https://redis.io/
[docker]: https://www.docker.com/community-edition