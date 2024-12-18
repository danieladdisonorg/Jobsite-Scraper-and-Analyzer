#!/usr/bin/env bash
c
# Wait for database to be ready
./scripts/wait_for_db.sh db:3306

echo "Running App using Gunicorn"
gunicorn -b 0.0.0.0:5000 --timeout 1000 run:app
echo "App is running successfully!!!"
