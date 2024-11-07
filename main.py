from gevent.pywsgi import WSGIServer
from app import app

addr = '127.0.0.1'
port = 8080

print(f'Starting application, open url: http://{addr}:{port}')
http_server = WSGIServer((addr, port), app)
http_server.serve_forever()