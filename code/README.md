# Run Project PMP with Docker

The application uses Laravel 13, Filament 5, React 19 with Inertia 3, TypeScript, Tailwind CSS 4, shadcn/ui, and MySQL. Vite+ runs frontend development, production builds, formatting, linting, and type checks.

The React frontend uses the light and dark [Shark Theme from tweakcn](https://tweakcn.com/themes/cmqfccy22000504l8fld0fkop). Its original tokens are saved in `../docs/design-system/`, and the active theme is in `resources/css/app.css`. Fonts are bundled locally. Filament uses its own theme at `/admin`.

## Run with Docker Compose

Install Docker with Compose support and use Linux containers.

Start Docker, open a terminal in `code`, then run:

```sh
docker compose up --build -d --wait
docker compose exec app php artisan make:filament-user
```

Open <http://localhost:8000> for the React frontend or <http://localhost:8000/admin> for Filament. Docker installs PHP and npm dependencies and builds the frontend with Vite+. Docker provides PHP, Composer, Node.js, and MySQL.

The `setup` service waits for MySQL, creates a persistent application key on the first run, and applies migrations. The `app` and `queue` services start after setup succeeds. The MySQL database is `project_pmp`, with user `root` and an empty password, inside the Compose network. MySQL has no published host port. This configuration is for local development only.

The containers use their own database configuration and application key. Your host `.env`, dependencies, and database are not copied into the image. Database data and Laravel storage persist in named volumes across `docker compose down` and rebuilds.

Source files are copied into the image. After changing PHP or frontend code, rebuild with:

```sh
docker compose up --build -d --wait
```

To use another web port, create or update `code/.env` with `APP_PORT=8080` before starting Compose. The container still listens on port 8000 and serves the compiled frontend assets.

Use these commands to inspect the stack or run checks:

```sh
docker compose logs -f app queue
docker compose exec app php artisan migrate:status
docker compose exec app composer test
docker compose down
```

The PHP tests use in-memory SQLite and do not change the MySQL database.

Keep the named volumes to retain your data and application key. `docker compose down --volumes` deletes both permanently.
