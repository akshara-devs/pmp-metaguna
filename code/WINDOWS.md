# Run on Windows with free Laravel Herd and XAMPP MySQL

Use this guide for local development on Windows 10 version 1809, OS build 17763.3469. Run commands in PowerShell.

[Herd requires Windows 10 or newer](https://herd.laravel.com/docs/windows/getting-started/installation). Its documentation does not confirm this exact Windows build, and this guide has not been tested on that build. Verify the installed tools in step 2 before continuing.

This setup uses free Herd and XAMPP together. No Herd Pro license, Docker, or WSL is required.

| Component | Provider |
| --- | --- |
| PHP 8.5, Composer, Node.js, and Nginx | Free Laravel Herd |
| Database server | XAMPP's **MySQL** service, which runs MariaDB |

[Free Herd supports external database servers](https://herd.laravel.com/docs/windows/getting-started/databases). XAMPP provides MariaDB, which works with this project's `mysql` connection.

## 1. Install and start the tools

1. Check **Settings > System > About > System type**. Use the Windows x64 installers on a 64-bit Intel or AMD computer.
2. If XAMPP is already installed, keep that installation. Otherwise, download [XAMPP for Windows](https://www.apachefriends.org/download.html) and install it in `C:\xampp`.
3. Open the XAMPP Control Panel. Start **MySQL** and confirm that it stays green. Keep **Apache** stopped so that Herd can use ports 80 and 443. Stop any automatically started XAMPP Apache service as well.
4. Download [Laravel Herd for Windows](https://herd.laravel.com/windows). Run the installer as administrator and complete onboarding with the free version.
5. In Herd's PHP settings, install PHP **8.5** and select it as the global version.
6. In Herd's JavaScript settings, install and select the latest **Node.js 22** release, at least **22.18.0**.
7. Close existing terminals and open a new PowerShell window.

The project's `composer.json` allows PHP 8.3, but `composer.lock` includes Symfony packages that require PHP **8.4.1 or newer**. PHP 8.5 matches the project's Docker runtime. Always use Herd's PHP for the commands below.

The Node.js requirement comes from `package.json`. You can manage versions through [Herd's Node.js settings](https://herd.laravel.com/docs/windows/technology/node-versions).

## 2. Verify PHP, Composer, and Node.js

Run:

```powershell
herd --version
herd use 8.5
php --version
php --ini
where.exe php
composer --version
node --version
npm.cmd --version
```

Confirm that `php --version` reports 8.5 and `node --version` reports 22.18.0 or newer within the 22.x series. `where.exe php` must list Herd's PHP command before any other PHP installation.

If PowerShell still selects another PHP installation, move Herd's PHP entry before that installation in your Windows **Path** environment variable. Open a new terminal afterward. Do not add `C:\xampp\php` to Path for this setup.

Use `npm.cmd` throughout this guide to avoid PowerShell restrictions on `npm.ps1` without changing your execution policy.

## 3. Open the existing project

Copy or clone this repository to your computer. For the example below, place it at `C:\Projects\project-pmp`.

Open the Laravel application directory:

```powershell
Set-Location C:\Projects\project-pmp\code
```

Replace the example path with your actual location. Run all remaining application commands from `code`, where `artisan` and `composer.json` are located. You do not need to move the project into XAMPP's `htdocs` or create a new Laravel application.

## 4. Create the database

With XAMPP's **MySQL** service running, connect through its command-line client:

```powershell
& 'C:\xampp\mysql\bin\mysql.exe' --host=127.0.0.1 --port=3306 --user=root --password
```

Enter your existing database root password. A fresh XAMPP installation normally has an empty root password, so press Enter if you have not set one.

At the database prompt, run:

```sql
CREATE DATABASE IF NOT EXISTS project_pmp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

If XAMPP is installed elsewhere or uses a different database port, adjust the command. Use that same port in the next step.

This procedure uses the database client directly. XAMPP's phpMyAdmin normally needs Apache, which stays stopped in this setup.

## 5. Configure Laravel

If `code\.env` does not exist, copy the example file:

```powershell
if (!(Test-Path .env)) {
	Copy-Item .env.example .env
}
notepad .env
```

Set these values in `.env`:

```dotenv
APP_NAME="Perpus Merah Putih"
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=project_pmp
DB_USERNAME=root
DB_PASSWORD=

SESSION_DRIVER=database
CACHE_STORE=database
QUEUE_CONNECTION=database
MAIL_MAILER=log
```

If your database root account has a password, put it in `DB_PASSWORD`. Quote the value if it contains spaces or `#`. The root account with an empty password is for local development only.

Change the example's `DB_HOST=mysql` to `127.0.0.1`. The hostname `mysql` belongs to the Docker setup. If an existing `.env` defines `DB_URL` or `DB_SOCKET`, remove those overrides for this TCP connection.

Keep the other settings from `.env.example`. Save the file before continuing.

## 6. Install dependencies and initialize the backend

Run:

```powershell
composer install
composer check-platform-reqs
php artisan config:clear --no-interaction
```

`composer install` uses the committed lockfile. Do not use `composer update` or `--ignore-platform-reqs` to bypass version or extension errors.

For a new `.env` with an empty `APP_KEY`, generate the application key once:

```powershell
php artisan key:generate --no-interaction
```

Keep an existing application key when reusing existing data.

Create the tables and check the migration status:

```powershell
php artisan migrate --no-interaction
php artisan migrate:status --no-interaction
```

The migrations create users, sessions, cache, and queue tables. Use the dedicated local `project_pmp` database. Do not run `migrate:fresh` against a database you want to keep.

Create your administrator account:

```powershell
php artisan make:filament-user
```

Enter your name, email address, and password when prompted. This command is interactive. Use these credentials to sign in to Filament.

## 7. Build the frontend assets

Run once during setup:

```powershell
npm.cmd ci
npm.cmd run build
```

The React home page needs these assets even when your main task is backend development. A successful build creates `public\build\manifest.json`.

If you copied the project from another computer, install dependencies on Windows rather than copying its `vendor` or `node_modules` directories.

## 8. Start the app

For an explicit local port, run Laravel's development server using Herd's PHP:

```powershell
php artisan serve --host=localhost --port=8000 --no-interaction
```

Leave this terminal open. Open <http://localhost:8000> for the React home page and <http://localhost:8000/admin> for the backend. Sign in with the account you created in step 6.

To process queued jobs, open another PowerShell terminal in `code` and run:

```powershell
php artisan queue:work --tries=1 --no-interaction
```

Stop each terminal process with Ctrl+C. Restart the queue worker after changing PHP code that handles jobs. You can browse the current home page and admin dashboard without a queue worker.

For frontend development with automatic refresh, run `npm.cmd run dev` in another terminal. Otherwise, rerun `npm.cmd run build` after changing frontend files.

Use these separate processes on Windows. The project's `composer run dev` also starts Laravel Pail, which requires the PCNTL extension unavailable on native Windows.

## 9. Use Herd's web server instead of port 8000

If you prefer a `.test` domain, stop `php artisan serve` and open Herd's Applications window. Add an existing site and select **`C:\Projects\project-pmp\code`** as the application directory.

Select PHP 8.5 for the site. Open the site using the URL shown by Herd, then set `APP_URL` in `.env` to that exact URL. Run:

```powershell
php artisan config:clear --no-interaction
```

Visit `/admin` on the same domain for the backend. Keep XAMPP MySQL running and Apache stopped. Herd serves the application through Nginx, so no `php artisan serve` process is needed for this option.

## 10. Start again on another day

1. Open Herd.
2. Start **MySQL** in the XAMPP Control Panel. Keep Apache stopped.
3. If you use port 8000, open PowerShell in `code` and run the server command from step 8. If you linked the site in Herd, open its `.test` URL.
4. Start the queue worker if you need queued jobs.

Keep `.env`, the application key, and the database between sessions. Dependency installation, key generation, and account creation are setup tasks, not daily startup tasks.

## Fix startup errors

| Error | Action |
| --- | --- |
| PHP version is too old | Run `herd use 8.5`, reopen PowerShell, and check `where.exe php`. For a linked site, also select PHP 8.5 in Herd. |
| Missing PHP extension or `could not find driver` | Run `php --ini` and `php -m`. Enable the missing extension in Herd's PHP configuration, then restart the relevant processes. The database needs `pdo_mysql`; Filament also needs extensions such as `intl` and `zip`. Rerun `composer check-platform-reqs`. |
| `getaddrinfo for mysql failed` | Set `DB_HOST=127.0.0.1` and run `php artisan config:clear --no-interaction`. |
| Connection refused or error 2002 | Start XAMPP MySQL and check that `DB_PORT` matches its configured port. |
| Access denied or error 1045 | Correct `DB_USERNAME` and `DB_PASSWORD`, then clear Laravel's configuration cache. |
| Unknown database or error 1049 | Create `project_pmp` using step 4. |
| Missing `sessions` or `cache` table | Check the database settings and run `php artisan migrate --no-interaction`. |
| No application encryption key | Generate a key only if `APP_KEY` is empty, as described in step 6. |
| Vite manifest missing | Run `npm.cmd ci` and `npm.cmd run build`. |
| Assets still point to an old Vite server | Stop the Vite process, remove the stale `public\hot` file if present, and run `npm.cmd run build`. |
| Port 8000 is occupied | Stop the conflicting process or use `--port=8001` and set `APP_URL=http://localhost:8001`. |
| Herd cannot start Nginx | Confirm that XAMPP Apache and any other service using ports 80 or 443 are stopped. |
| Login returns 419 | Clear Laravel's configuration cache and browser cookies, then use one hostname consistently. Keep `SESSION_DOMAIN=null` from `.env.example`. |

For other application errors, read the latest entries in `storage\logs\laravel.log`.

## Verify the installation

With the database running, run:

```powershell
composer check-platform-reqs
php artisan migrate:status --no-interaction
php artisan route:list --path=admin --no-interaction
composer test
```

Confirm that every migration reports **Ran**. Open the home page, sign in at `/admin`, and confirm that the dashboard loads. The PHP tests use in-memory SQLite, so Herd's PHP needs `pdo_sqlite` for the test command.
