#!/bin/bash

gunicorn --bind 0.0.0.0:5000 --workers 3 app:app -t 60 --worker-class=gevent
