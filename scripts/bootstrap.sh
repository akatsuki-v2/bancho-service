#!/usr/bin/env bash
set -euo pipefail

# handle int & kill signals as non-errors until final "exec" runs
trap "{ exit 0; }" TERM INT

if [ -z "$APP_COMPONENT" ]; then
  echo "Please set APP_COMPONENT"
  exit 1
fi

cd /srv/root

case $APP_COMPONENT in
  "api")
    exec /scripts/run-api.sh
    ;;

  *)
    echo "'$APP_COMPONENT' is not a known value for APP_COMPONENT"
    ;;
esac
