# Bootstrap development environment (Windows PowerShell)
# - Creates and activates a Python venv under backend/venv
# - Installs Python and Node dependencies
# - Runs Django makemigrations/migrate
# - Optionally starts Redis via Docker
# - Optionally installs Playwright browsers

param(
    [switch]$StartRedis,
    [switch]$InstallPlaywrightBrowsers
)

$backendDir = Join-Path $PSScriptRoot 'backend'

Write-Host "Bootstrapping dev environment..."

if (-not (Test-Path "$backendDir\venv")) {
    Write-Host "Creating Python virtual environment..."
    python -m venv "$backendDir\venv"
} else {
    Write-Host "Virtual environment already exists."
}

# Activate venv
$activate = "$backendDir\venv\Scripts\Activate.ps1"
if (Test-Path $activate) {
    Write-Host "Activating virtual environment..."
    & $activate
} else {
    Write-Error "Cannot find activation script at $activate"
    exit 1
}

# Install Python requirements
if (Test-Path "$backendDir\requirements.txt") {
    Write-Host "Installing Python requirements..."
    pip install -r "$backendDir\requirements.txt"
} else {
    Write-Warning "requirements.txt not found in backend/. Skipping pip install."
}

# Ensure channels packages are available (idempotent)
Write-Host "Ensuring channels dependencies..."
pip install channels channels_redis --upgrade

# Node deps
Write-Host "Installing frontend npm packages..."
if (Test-Path (Join-Path $PSScriptRoot 'package.json')) {
    Push-Location $PSScriptRoot
    npm install
    Pop-Location
} else {
    Write-Warning "package.json not found at project root. Skipping npm install."
}

# Make and apply migrations
Write-Host "Making and applying Django migrations..."
Push-Location $backendDir
python manage.py makemigrations logbook || Write-Host "makemigrations returned non-zero; continuing"
python manage.py migrate || Write-Error "migrate failed"; Pop-Location

# Start Redis if requested
if ($StartRedis) {
    Write-Host "Starting Redis via Docker..."
    docker run -d --name local-redis -p 6379:6379 redis:7 | Out-Null
    Write-Host "Redis container started (local-redis)."
}

# Optionally install Playwright browsers
if ($InstallPlaywrightBrowsers) {
    if (Test-Path (Join-Path $PSScriptRoot 'package.json')) {
        Push-Location $PSScriptRoot
        npx playwright install
        Pop-Location
    } else {
        Write-Warning "Cannot install Playwright browsers because package.json not found."
    }
}

Write-Host "Bootstrap complete. Next steps: Activate the backend venv and run the server:"
Write-Host "& '$backendDir\venv\Scripts\Activate.ps1'"
Write-Host "python manage.py runserver 0.0.0.0:8000  (from backend directory)"
