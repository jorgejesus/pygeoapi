# =================================================================
#
# Authors: Jorge S. Mendes de Jesus <jorge.jesus@gmail.com>
#
# Copyright (c) 2018 Tom Kralidis
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

# Based on gunicorn generic documentation

import click

import multiprocessing
import gunicorn.app.base
from gunicorn.six import iteritems


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class ApplicationServer(gunicorn.app.base.BaseApplication):
    """ Generic Gunicorn server class"""
    def __init__(self, app, options=None):
        """
        Initialize object

        :param app: WSGI compliant object
        :param options: options to be passed to gunicorn BaseApplication

        """

        self.options = options or {}
        self.application = app
        super(ApplicationServer, self).__init__()

    def load_config(self):
        """Load configuration from options dictionary into gunicorn"""

        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """Load app into gunicorn"""
        return self.application


@click.command()
@click.option('--workers', '-w', default=None, type=click.INT,
              help='Number of workers if not defined: (2*CPU)+1')
def run(workers):
    """Serve pygeoapi via gunicorn. Using the default
    sync worker, 1 thread per worker and keep-alive of 2s

    Gunicorn is not intended to be run on debug mode
    """

    from pygeoapi.flask_app import APP, api_

    if not workers:
        workers = number_of_workers()

    options = {
        'bind': '%s:%s' % (api_.config['server']['bind']['host'],
                           api_.config['server']['bind']['port']),
        'workers': workers
        }

    if api_.config.get('logging', None) and \
       api_.config['logging'].get("level", None):

        log_level = api_.config["logging"]["level"]
        options["loglevel"] = log_level

        options["accesslog"] = "-"

        if log_level == "ERROR" or "CRITICAL":
            options["errorlog"] = "-"

    else:
        log_level = None

    ApplicationServer(APP, options).run()


if __name__ == '__main__':
    run()
