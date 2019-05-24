# Gunicorn 

pygeoapi is can run its own HTTP server based on [Gunicorn](https://gunicorn.org/), this is more suitable for production environments and docker deployment

**Following the installation procedure** the production server is activated  by running:

```
python3 gunicorn_server.py
```

Logging level is set on the yaml configuration file, and log information is sent to stdout/stderr
