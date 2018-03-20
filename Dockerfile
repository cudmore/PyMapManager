FROM tiangolo/uwsgi-nginx-flask:python3.6

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
ENV STATIC_INDEX 1

ENV NGINX_WORKER_PROCESSES auto

COPY ./app /app

# install from PyPi
#RUN pip install --no-cache-dir PyMapManager
# install from local
RUN pip install --no-cache-dir pymapmanager

COPY ./app/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# volume must be mounted from command line with
# docker run --name mycontainer -p 80:80 -v /Users/cudmore/Dropbox/PyMapManager-Data:/PyMapManager-Data --link redis myimage
VOLUME /PyMapManager-Data

# swap in my nginx .conf file so we can load /images and /static directly from nginx
COPY ./app/my_nginx.conf /etc/nginx/conf.d/

# critical to find ../PyMapManager-Data
WORKDIR /app
