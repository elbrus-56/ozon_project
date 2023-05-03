#!/bin/bash
exec gunicorn  -c "/app/ozondrf/gunicorn_config.py" ozondrf.wsgi