#!/bin/sh
set -eu

env_file=storage/app/private/docker.env

if [ "${1:-}" = "setup" ]; then
    if [ ! -s "$env_file" ]; then
        umask 077
        app_key=$(php artisan key:generate --show --no-interaction)
        printf 'APP_KEY=%s\n' "$app_key" > "$env_file.tmp"
        mv "$env_file.tmp" "$env_file"
    fi

    php artisan migrate --force --no-interaction
    exit 0
fi

if [ ! -s "$env_file" ]; then
    echo "Application key is missing. Run the Compose setup service first." >&2
    exit 1
fi

exec "$@"
