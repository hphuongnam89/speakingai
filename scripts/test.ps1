$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $root 'backend')
try {
  $py = if (Test-Path '.venv\Scripts\python.exe') { '.venv\Scripts\python.exe' } elseif (Test-Path 'venv\Scripts\python.exe') { 'venv\Scripts\python.exe' } else { 'python.exe' }
  & $py -m pytest tests -q
} finally { Pop-Location }
