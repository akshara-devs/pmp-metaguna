# Run Project PMP

For Windows 10 version 1809, build 17763.3469, follow [Run on Windows with free Laravel Herd and XAMPP MySQL](WINDOWS.md).

The Docker instructions below are a separate setup option.

The application uses Laravel 13, Filament 5, React 19 with Inertia 3, TypeScript, Tailwind CSS 4, shadcn/ui, and MySQL. Vite+ runs frontend development, production builds, formatting, linting, and type checks.

The React frontend uses the light and dark [Shark Theme from tweakcn](https://tweakcn.com/themes/cmqfccy22000504l8fld0fkop). Its original tokens are saved in `../docs/design-system/`, and the active theme is in `resources/css/app.css`. Fonts are bundled locally. Filament uses its own theme at `/admin`.

## Install Docker on Windows

Use [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) with the WSL 2 backend and Linux containers.

1. Open PowerShell as administrator and install WSL if it is not already installed:

    ```powershell
    wsl --install
    ```

2. Restart Windows if prompted, then update WSL:

    ```powershell
    wsl --update
    wsl --version
    ```

3. Install Docker Desktop using the linked Windows instructions, then start it and wait for the engine to be ready. Enable **Use the WSL 2 based engine** in Docker Desktop settings. If you run commands inside a WSL distribution, enable that distribution under **Resources > WSL Integration**.
4. Open a new terminal and verify Docker:

    ```powershell
    docker version
    docker compose version
    docker run --rm hello-world
    ```

Continue with the app commands below in PowerShell or your integrated WSL terminal.

## Install Docker on Linux

For Ubuntu and Ubuntu-based Linux Mint, follow [Docker's Ubuntu installation guide](https://docs.docker.com/engine/install/ubuntu/). Mint is an Ubuntu derivative and is not officially supported by Docker, though the Ubuntu packages may work. For Linux Mint Debian Edition, use the [Debian guide](https://docs.docker.com/engine/install/debian/) instead. For other distributions, use the matching [Docker Engine installation guide](https://docs.docker.com/engine/install/).

If Docker is already installed, check `docker version` and `docker compose version` first. For a fresh Ubuntu or Ubuntu-based Mint installation, remove conflicting packages as described in the linked guide, then add Docker's package repository:

```sh
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker run --rm hello-world
```

To run the app's Docker commands without `sudo`, add your user to the Docker group:

```sh
sudo usermod -aG docker "$USER"
```

Sign out and back in, then verify access:

```sh
docker version
docker compose version
docker run --rm hello-world
```

Membership in the Docker group grants root-level privileges. If you keep using `sudo`, prefix the app's Docker commands with `sudo` too.

## Run with Docker Compose

Start Docker, open a terminal in `code`, then run:

```sh
docker compose up --build -d --wait
docker compose exec app php artisan make:filament-user
```

Open <http://localhost:8000> for the React frontend or <http://localhost:8000/admin> for Filament. Docker installs PHP and npm dependencies and builds the frontend with Vite+. Docker provides PHP, Composer, Node.js, and MySQL.

The `setup` service waits for MySQL, creates a persistent application key on the first run, and applies migrations. The `app` and `queue` services start after setup succeeds. The MySQL database is `project_pmp`, with user `root` and an empty password, inside the Compose network. MySQL has no published host port. This configuration is for local development only.

Compose reads the application and MySQL settings from `code/.env`. The host `.env` and dependencies are not copied into the image, and the application key is stored separately in a named volume. Database data and Laravel storage persist in named volumes across `docker compose down` and rebuilds.

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
