#!/usr/bin/env bash
set -euo pipefail

if [ -z "$APP_COMPONENT" ]; then
  echo "Please set APP_COMPONENT"
  exit 1
fi

cd /srv/root

case $APP_COMPONENT in
  "api")
    /scripts/run-api.sh
    ;;

  "tests")
    /scripts/run-tests.sh
    ;;

  *)
    echo "'$APP_COMPONENT' is not a known value for APP_COMPONENT"
    ;;
esac