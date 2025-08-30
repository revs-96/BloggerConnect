#!/bin/sh
set -e

host="$1"
shift
cmd="$@"

until pg_isready -h "$host" -p 5432 -U "$POSTGRES_USER"; do
  echo "⏳ Waiting for Postgres at $host:5432..."
  sleep 2
done

echo "✅ Postgres is ready, starting app..."
exec $cmd
