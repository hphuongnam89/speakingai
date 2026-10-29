$ErrorActionPreference = 'Stop'
$androidDir = Join-Path $PSScriptRoot '..\android'
if (-not (Test-Path (Join-Path $androidDir 'gradlew.bat'))) {
  Write-Warning 'gradlew.bat is missing; install the Gradle wrapper before building Android.'
  exit 2
}
if (-not $env:ANDROID_KEYSTORE_PATH -or -not $env:ANDROID_KEYSTORE_PASS -or -not $env:ANDROID_KEY_ALIAS -or -not $env:ANDROID_KEY_PASSWORD) {
  Write-Warning 'Release signing env vars are not set; release build must remain unsigned locally.'
}
Push-Location $androidDir
try {
  .\gradlew.bat lintDebug assembleDebug
  if ($env:ANDROID_KEYSTORE_PATH) { .\gradlew.bat assembleRelease }
} finally { Pop-Location }
