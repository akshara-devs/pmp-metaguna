#!/bin/sh
set -eu

env_file=storage/app/private/docker.env

if [ "${1:-}" = "setup" ]; then
    if [ ! -s "$env_file" ]; then
        app_key=$(php artisan key:generate --show --no-interaction)
        (umask 077; printf 'APP_KEY=%s\n' "$app_key" > "$env_file.tmp")
        mv "$env_file.tmp" "$env_file"
    fi

    export APP_KEY="$(sed -n 's/^APP_KEY=//p' "$env_file")"

    composer install --no-interaction --prefer-dist --no-progress
    cp -R /opt/frontend-build/. public/build/
    chown -R www-data:www-data vendor public/build bootstrap/cache storage

    php artisan migrate --force --no-interaction
    exit 0
fi

if [ ! -s "$env_file" ]; then
    echo "Application key is missing. Run the Compose setup service first." >&2
    exit 1
fi

export APP_KEY="$(sed -n 's/^APP_KEY=//p' "$env_file")"

exec "$@"
