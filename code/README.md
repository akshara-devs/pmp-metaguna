# Project PMP

Laravel 13 with Filament 5. The admin panel is available at `/admin`.

## Run locally

Run these commands from the `code` directory. Use PHP 8.3 or newer, Composer 2, and Node.js compatible with Vite 8.

On a fresh checkout, install dependencies and initialize the SQLite database:

```sh
composer run setup
```

Create your admin account interactively:

```sh
php artisan make:filament-user
```

Start the development server:

```sh
composer run dev
```

Open <http://localhost:8000/admin> and sign in with the account you created.

The local `.env` file and SQLite database are excluded from Git. To use another database, update `.env` before running migrations.

## Verify changes

```sh
composer test
vendor/bin/pint
npm run build
```
