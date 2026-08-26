#!/bin/sh
set -eu

if [ -n "${API_KEY_FILE:-}" ] && [ -f "$API_KEY_FILE" ]; then
  API_KEY="$(tr -d '\r\n' < "$API_KEY_FILE")"
  export API_KEY
fi

exec "$@"
