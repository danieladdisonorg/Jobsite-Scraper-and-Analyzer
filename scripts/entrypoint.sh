#!/usr/bin/env bash

# Wait for database to be ready
scripts/db_init.sh db 3306

echo "Running App using Gunicorn"
gunicorn -b 0.0.0.0:5000 --timeout 180 run:app