#!/bin/sh
set -e

echo "En attente de PostgreSQL..."
until nc -z db 5432; do
    sleep 1
done
echo "PostgreSQL disponible."

exec "$@"
