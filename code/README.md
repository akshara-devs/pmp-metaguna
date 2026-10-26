# Run Project PMP locally

The application uses Laravel 13, Filament 5, React 19 with Inertia 3, TypeScript, Tailwind CSS 4, shadcn/ui, and MySQL. Vite+ runs frontend development, production builds, formatting, linting, and type checks.

The React frontend uses the light and dark [Shark Theme from tweakcn](https://tweakcn.com/themes/cmqfccy22000504l8fld0fkop). Its original tokens are saved in `../docs/design-system/`, and the active theme is in `resources/css/app.css`. Fonts are bundled locally. Filament uses its own theme at `/admin`.

## Install prerequisites on Windows

Use PowerShell and install these tools:

1. Install [Git for Windows](https://git-scm.com/download/win).
2. Install PHP 8.5 and Composer using the Windows instructions in [Laravel installation](https://laravel.com/docs/13.x/installation), or install [PHP for Windows](https://windows.php.net/download/) and [Composer](https://getcomposer.org/download/) separately. Add their executables to `PATH`.
3. Install [Node.js 24 LTS](https://nodejs.org/en/download), version 24.11 or newer, with npm.
4. Install [MySQL Community Server 8.4 LTS](https://dev.mysql.com/doc/refman/8.4/en/windows-installation.html). Configure it as a Windows service on port 3306 and set a local root password. Add the MySQL `bin` directory to `PATH`.

Enable these extensions in the CLI PHP configuration returned by `php --ini`: `curl`, `fileinfo`, `gd`, `intl`, `mbstring`, `openssl`, `pdo_mysql`, `pdo_sqlite`, and `zip`. PHP must also provide DOM, XML, session, and tokenizer support. SQLite is used only by the isolated PHP test suite.

Open a new PowerShell window, then check the tools:

```powershell
php --version
composer --version
node --version
npm --version
mysql --version
```

## Install prerequisites on Linux Mint

Install Git, MySQL, and download utilities:

```sh
sudo apt update
sudo apt install git curl unzip ca-certificates mysql-server
sudo systemctl enable --now mysql
```

Install PHP 8.5 and Composer using Laravel's Linux installer:

```sh
/bin/bash -c "$(curl -fsSL https://php.new/install/linux/8.5)"
```

Open a new terminal so the installed tools are on `PATH`. Install [Node.js 24 LTS](https://nodejs.org/en/download), version 24.11 or newer, using its Linux instructions.

```sh
php --version
php --ini
php -m
composer --version
node --version
npm --version
mysql --version
```

PHP needs the extensions listed in the Windows section. Both platforms use PHP 8.5 to match the committed Composer lockfile. Run `composer check-platform-reqs` after installing project dependencies to detect missing extensions.

On a fresh Mint installation, MySQL root may use socket authentication. To enable password login for local development, open MySQL:

```sh
sudo mysql
```

Set a password you choose, replacing the placeholder below, then exit:

```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'REPLACE_WITH_YOUR_LOCAL_PASSWORD';
EXIT;
```

If password authentication already works, keep the existing password and skip this step.

## Create the database

On either platform, connect using your local MySQL root password:

```sh
mysql -h 127.0.0.1 -P 3306 -u root -p
```

Create the project database, then exit:

```sql
CREATE DATABASE IF NOT EXISTS project_pmp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

## Configure the application

Clone the repository and open its `code` directory. Run the remaining commands from that directory.

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

On Linux Mint:

```sh
cp .env.example .env
```

Copy the example only on the first setup. Keep an existing `.env` file.

Edit `.env` and set your local password directly in the file:

```dotenv
APP_URL=http://localhost:8000
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=project_pmp
DB_USERNAME=root
DB_PASSWORD="REPLACE_WITH_YOUR_LOCAL_PASSWORD"
```

The root account is the selected local development account. Keep `.env` out of Git and use a separate database account for deployed environments.

Install the locked dependencies, generate the application key, run the MySQL migrations, and build frontend assets:

```sh
composer run setup
composer check-platform-reqs
```

Run `composer run setup` during initial setup only; it generates a new application key. Vite+ is installed locally by npm, so no global `vp` installation is required.

Create your Filament admin account interactively:

```sh
php artisan make:filament-user
```

## Start development

Run this command on Windows or Linux Mint:

```sh
composer run dev
```

This starts Laravel, the queue listener, and Vite+ through the frontend `dev` script. Laravel also starts Pail logs when the platform supports `pcntl`.

Open the frontend at <http://localhost:8000> or the admin panel at <http://localhost:8000/admin>. The frontend's Dark theme button switches the Shark Theme palette and remembers the selection.

To run the web servers separately, use two terminals:

```sh
php artisan serve
```

```sh
npm run dev
```

Run `php artisan queue:work` in another terminal if you need background jobs. Stop development processes with Ctrl+C.

## Verify changes

```sh
composer test
npm run typecheck
npm run check
npm run build
```

The PHP test suite uses an in-memory SQLite database and does not change your MySQL database. To verify the configured MySQL connection and migrations, run:

```sh
php artisan migrate:status
```

Format frontend files with `npm run format`. Format PHP files with `php vendor/bin/pint` on either platform.

## Resolve setup errors

If MySQL reports access denied, check the username and password in `.env`, then run `php artisan config:clear`. If the connection is refused, start the MySQL service and check port 3306. If the database is unknown, create `project_pmp` using the SQL above.

For missing PHP extensions, check `php --ini` to confirm you edited the CLI configuration, then run `composer check-platform-reqs` again. Do not bypass Composer's platform checks.

For missing frontend assets, run `npm ci` and `npm run build`, or keep `npm run dev` running. If PowerShell blocks `npm.ps1`, use `npm.cmd` instead of `npm`.
