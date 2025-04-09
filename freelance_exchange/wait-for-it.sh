#!/bin/sh

HOST=$1
PORT=$2
TIMEOUT=$3

TIMEOUT=${TIMEOUT:-60}

echo "Waiting for $HOST:$PORT to be ready..."

for i in $(seq 1 $TIMEOUT); do
    nc -z $HOST $PORT && echo "$HOST:$PORT is available!" && exit 0
    echo "Waiting for $HOST:$PORT... ($i/$TIMEOUT)"
    sleep 1
done

echo "Timeout reached. $HOST:$PORT is not available."
exit 1
