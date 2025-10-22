# setup.ps1 - creates venv, installs deps, and optionally runs the honeypot
$VenvDir = "venv"
$ReqFile = "requirements.txt"

Write-Host "== FTP Honeypot setup (PowerShell) =="

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtualenv..."
    python -m venv $VenvDir
} else {
    Write-Host "Virtualenv exists at .\$VenvDir"
}

Write-Host "Activating venv..."
. "$VenvDir\Scripts\Activate.ps1" 

Write-Host "Upgrading pip..."
pip install --upgrade pip

Write-Host "Installing requirements..."
pip install -r $ReqFile

Write-Host "Install complete."
$run = Read-Host "Run the honeypot now? (y/N)"
if ($run -match '^[Yy]') {
    python main.py
} else {
    Write-Host "Done. Activate with: .\$VenvDir\Scripts\Activate.ps1"
}
