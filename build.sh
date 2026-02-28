#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Add current directory to PYTHONPATH so 'app' module can be found
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Run database initialization
python app/db/init_db.py
