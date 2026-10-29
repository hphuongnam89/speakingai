$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root 'backend'
$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $python) { throw 'Python 3.12+ is required.' }
Push-Location $backend
try {
  if (-not (Test-Path '.venv')) { & $python.Source -3.13 -m venv .venv 2>$null; if ($LASTEXITCODE -ne 0) { & $python.Source -m venv .venv } }
  & .venv\Scripts\python.exe -m pip install --upgrade pip
  & .venv\Scripts\python.exe -m pip install -r requirements.txt
} finally { Pop-Location }
