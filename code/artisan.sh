#!/usr/bin/env bash
set -e

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

exec docker compose exec --user root app php artisan "$@"
