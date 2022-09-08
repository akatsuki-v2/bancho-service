#!/usr/bin/env bash
set -euo pipefail

execDBStatement() {
  mysql \
  --host=$WRITE_DB_HOST \
  --port=$WRITE_DB_PORT \
  --user=$WRITE_DB_USER \
  --password=$WRITE_DB_PASS \
  --execute="$1"
}

FULL_DB_NAME="${WRITE_DB_NAME}"

if [[ "$APP_COMPONENT" == "tests" ]]; then
  FULL_DB_NAME="${WRITE_DB_NAME}_test"
fi

execDBStatement "CREATE DATABASE IF NOT EXISTS ${FULL_DB_NAME};"