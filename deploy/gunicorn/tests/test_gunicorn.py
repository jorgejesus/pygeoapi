from gunicorn_server import run_server
from pygeoapi.api import API
import yaml
import time
import socket
import sys
import requests
import multiprocessing

p = multiprocessing.Process(target=run_server)

with open('../../tests/pygeoapi-test-config.yml') as fh:
    CONFIG = yaml.load(fh, Loader=yaml.FullLoader)

api_ = API(CONFIG)

host = api_.config["server"]["bind"]["host"]
port = api_.config["server"]["bind"]["port"]
url =  api_.config["server"]["url"]
cors = api_.config["server"]["cors"]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2) 
result = sock.connect_ex((host,port))

if result == 0:
        sys.stdout.write("Port to test gunicorn is taken - stopping \n")
        sys.exit(1)

p.start()
time.sleep(2)
#Check if url is responsive
r = requests.get(url)
assert r.status_code==200

assert r.headers.get("Access-Control-Allow-Origin") is not None

p.terminate()
p.join()
