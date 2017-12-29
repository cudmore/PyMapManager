## To run development environment

### 1) run Flask server
	
	sudo gunicorn -b 0.0.0.0:8000 mmserver:app

This will run the Flask EST server on `http://127.0.0.1:8000` by default

### 2) Use node http-server to serve index.html

	cd mmclient
	http-server

This will run a web-server at `http://127.0.0.1:8080` and serve `mmclient/index.html`

Browse the client interface at:

	http://127.0.0.1:8080
		
### Important	

`/static/mmserver.js` **must** point to address of mmserver REST server
	
	serverurl = 'http://127.0.0.1:8000/'


## install node http-server

	sudo npm install -g http-server

## links

original link that has hidden canvas to get pixel data
	https://alexander.engineering/imagescatter/
	
elegant js code using promise
	https://codepen.io/etpinard/pen/GjmWYg