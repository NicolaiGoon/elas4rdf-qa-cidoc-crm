#!/bin/bash

PORT=5000

if [ "$1" == "start" ]; then
    echo "Starting CIDOC-QA"
    gunicorn --bind 0.0.0.0:$PORT --workers 3 app:app -t 180 --worker-class=gevent >>.log 2>&1 &
    
elif [ "$1" == "stop" ]; then
    
    pkill -f "gunicorn --bind 0.0.0.0:$PORT --workers 3 app:app"
    echo "CIDOC-QA has stopped"
else
    echo "Usage: $0 [start|stop]"
    exit 1
fi