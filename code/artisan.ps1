$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot

try {
    & docker compose exec --user root app php artisan @args
    $artisanExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}

exit $artisanExitCode
