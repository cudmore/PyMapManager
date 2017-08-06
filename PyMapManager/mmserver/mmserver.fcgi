#!/home1/robertcu/python/Python-2.7.7/python

# #!/home1/robertcu/python/Python-2.7.7/python/mmserver/bin/python

# /home1/robertcu/python/Python-2.7.7/python

from flup.server.fcgi import WSGIServer
from mmserver import app as application

WSGIServer(application).run()
