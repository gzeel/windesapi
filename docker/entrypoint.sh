#!/bin/sh
set -eu

if [ "${RESET_DB_ON_START:-true}" = "true" ]; then
  python scripts/seed_db.py
else
  python -c 'from app.database import initialize_database; initialize_database()'
fi

exec "$@"
