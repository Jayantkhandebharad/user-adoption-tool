#!/bin/sh
# Bring the database schema up to date, then serve. Upgrades happen in place on restart.
set -eu
alembic upgrade head
exec uvicorn app.main:create_app --factory \
  --host 0.0.0.0 --port 8000 \
  --proxy-headers --forwarded-allow-ips "${FORWARDED_ALLOW_IPS:-127.0.0.1}"
