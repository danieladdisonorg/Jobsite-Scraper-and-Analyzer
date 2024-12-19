#!/bin/bash

HOST=$1
PORT=$2
RETRIES=30

# wait for DataBase connection
until nc -z -v -w30 $HOST $PORT || [ $RETRIES -eq 0 ]; do

  echo "Waiting for DataBase at $HOST:$PORT ...."
  ((RETRIES--))
  sleep 1
done
if [ $RETRIES -eq 0 ]; then
  echo "DataBase is not reachable, exiting."
  exit 1
fi

echo "DataBase is up and running at $HOST:$PORT"

echo "Running Alembic migrations files"
alembic --config migrations/alembic.ini upgrade head
echo "Migration completed successfully!!!"
