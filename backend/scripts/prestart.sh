#! /usr/bin/env bash

set -e
set -x

# Let the DB start
python app/db-scripts/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python app/db-scripts/initial_data.py
