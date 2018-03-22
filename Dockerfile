FROM tiangolo/uwsgi-nginx-flask:python3.6

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
ENV STATIC_INDEX 1

ENV NGINX_WORKER_PROCESSES auto

COPY ./mmserver /app

# install PyMapManager from this repo
RUN mkdir /PyMapManager
COPY ./requirements.txt /PyMapManager/requirements.txt
RUN pip install -r /PyMapManager/requirements.txt

COPY ./setup.py /PyMapManager
COPY ./pymapmanager /PyMapManager/pymapmanager
WORKDIR /PyMapManager
RUN python /PyMapManager/setup.py install

# install python libraries for /mmserver (e.g. /app)
COPY ./mmserver/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# volume must be mounted from command line with
# docker run --name mycontainer -p 80:80 -v /Users/cudmore/Dropbox/PyMapManager-Data:/PyMapManager-Data --link redis myimage
VOLUME /PyMapManager-Data

# swap in my nginx .conf file so we can load /images and /static directly from nginx
COPY ./mmserver/my_nginx.conf /etc/nginx/conf.d/

# required, in order to find ../PyMapManager-Data
WORKDIR /app
