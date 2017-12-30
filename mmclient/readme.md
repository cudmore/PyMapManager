This is html/javascript code that can be served using a web-server and then accessed as a user-friendly web-page.

The dynamic content is generated using a combination of [Javascript][javascript], [Angular JS][angular], and [Plotly JS][plotly].

For this to work, the back-end Python Flask REST server must also be running. See the [mmserver][mmserver] documentation.

## Files

- `mmclient/index.html` : html and Angular code.
- `mmclient/static` : Folder that contains javascript libraries that are imported into `index.html`.
- `mmclient/static/mmclient.js` : Angular Javascript code that communicates with the back-end server to retrive data and then plot annotations and display images.


## Configure `mmclient/static/mmserver.js`

By default, `mmclient/static/mmserver.js` will try to retrieve data from a publicly available `mmserver` at `http://cudmore.duckdns.org:5010`.

If you want to run the `mmserver` on localhost, you need to modify the `mmclient/static/mmserver.js` file.

```
serverurl = 'http://127.0.0.1:5010/'
```

## Running the code (local)

This will use node npm to create a local server.

To install the http-server (assuming you have node and npm)

```
npm install http-server -g
```

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

THis is very simple, just drop the `mmclient/` folder into a web accessible locations. Something like `/var/www/html/`. We have tested this on a Debian server using `nginx` as well as a commercial provider `bluehost` and it all works fine.

[javascript]: https://www.javascript.com/
[angular]: https://angularjs.org/
[plotly]: https://plot.ly/javascript/
[mmserver]: https://github.com/cudmore/PyMapManager/tree/master/mmserver
[node]: https://nodejs.org/
[npm]: https://www.npmjs.com/
