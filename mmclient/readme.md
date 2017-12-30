This is a Javascript client that can be served using a web-server and then accessed as a user-friendly web-page.

Please see the main [PyMapManager](http://blog.cudmore.io/PyMapManager) documentation website.

The dynamic content is generated using a combination of [Javascript](https://www.javascript.com/), [Angular JS](https://angularjs.org/), [Plotly JS](https://plot.ly/javascript/), and [Leaflet](http://leafletjs.com).

For this to work, the back-end `mmserver` REST server must also be running. See the [mmserver](https://github.com/cudmore/PyMapManager/tree/master/mmserver) documentation.

## Files

- `mmclient/index.html` : html and Angular code.
- `mmclient/static` : Folder that contains Javascript libraries that are imported into `index.html`.
- `mmclient/static/mmclient.js` : Angular Javascript code that communicates with the back-end `mmserver` REST server to retrieve data, plot annotations, and display images.


## Configure `mmclient/static/mmserver.js`

By default, `mmclient/static/mmserver.js` will try to retrieve data from a publicly available `mmserver` at `http://cudmore.duckdns.org:5010`.

If you want to run the `mmserver` on localhost, you need to modify the `mmclient/static/mmserver.js` file.

```
serverurl = 'http://127.0.0.1:5010/'
```

## Running the Javascript server (local)

This will use a [node](https://nodejs.org/) http-server to create a local server.

### Install http-server

Assuming you have [node](https://nodejs.org/) and [npm](https://www.npmjs.com/).

```
npm install http-server -g
```

### Run the server

```
cd mmclient
http-server
```

Response should be

```
Starting up http-server, serving ./
Available on:
  http://127.0.0.1:8081
  http://192.168.1.10:8081
Hit CTRL-C to stop the server
```

The website is then available at

	http://localhost:8000	

## Running the code (on preixisting web-server)

This is very simple, just drop the `mmclient/` folder into a web accessible location. Something like `/var/www/html/`. We have tested this on a Debian server using `nginx` as well as a commercial shared host from `bluehost`.

