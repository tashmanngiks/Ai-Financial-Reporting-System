param(
    [switch]$Reinstall
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $projectRoot "venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "Creating backend virtual environment in $venvPath ..."
    py -m venv $venvPath
}

if ($Reinstall) {
    Write-Host "Reinstalling backend dependencies ..."
    & $pipExe install --upgrade pip
    & $pipExe install --force-reinstall -r (Join-Path $projectRoot "requirements.txt")
}
else {
    Write-Host "Installing backend dependencies ..."
    & $pipExe install -r (Join-Path $projectRoot "requirements.txt")
}

Write-Host ""
Write-Host "Virtual environment is ready."
Write-Host "Activate it with:"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Run Django with:"
Write-Host "  .\venv\Scripts\python.exe manage.py runserver"
