'''
run with
/usr/local/bin/gunicorn test_sse:app --worker-class gevent --bind 127.0.0.1:5000
'''

import time
from datetime import datetime

from flask import Flask, render_template, Response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/test')
def test():
    return "works"

@app.route('/event_stream')
def stream():
    def event_stream():
        while True:
            time.sleep(0.4)
            yield 'data: %s\n\n' % datetime.now()

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
	app.run()