# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2019 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================


import os
import sys

from pygeoapi.api import API

import pytest

import yaml
import time
import socket
import requests
import multiprocessing


parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

from gunicorn_server import run_server  # noqa: E402


@pytest.fixture()
def config():
    with open('./tests/pygeoapi-test-config.yml') as fh:
        return yaml.load(fh, Loader=yaml.FullLoader)


@pytest.fixture()
def api_(config):
    return API(config)


def test_gunicorn(config, api_):

    p = multiprocessing.Process(target=run_server)

    host = api_.config["server"]["bind"]["host"]
    port = api_.config["server"]["bind"]["port"]
    url = api_.config["server"]["url"]
    cors = api_.config["server"]["cors"]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))

    if result == 0:
            sys.stdout.write("Port to test gunicorn is taken - stopping \n")
            sys.exit(1)

    # If the test thread is killed by an assert error,
    # gunicorn will also be killed
    p.daemon = True
    p.start()
    time.sleep(2)

    r = requests.get(os.path.join(url, "?f=html"))
    assert r.status_code == 200

    if cors:
        assert r.headers.get("Access-Control-Allow-Origin") is not None

    p.terminate()
    p.join()
