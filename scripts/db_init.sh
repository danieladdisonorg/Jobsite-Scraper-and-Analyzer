#!/bin/bash

HOST=$1
PORT=$2

# wait for DataBase connection
until nc -z -v -w30 $HOST $PORT
do
  echo "Waiting for DataBase at $HOST:$PORT ...."
done

echo "DataBase is up and running at $HOST:$PORT"

echo "Running Alembic migrations files"
alembic --config migrations/alembic.ini upgrade head
echo "Migration completed successfully!!!"
