# Version: 1.8.0
# Date: 2026-08-12
# Author: Serhii Dralo <dralo@ditis.group>
# Changelog: Build and verify the portable Windows x86-64 release.

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$version = (& python -c "from core.metadata import APP_VERSION; print(APP_VERSION)").Trim()
if (-not $version) {
    throw "Unable to determine NetCheck version."
}

$buildDirectory = Join-Path $projectRoot "build"
$distributionDirectory = Join-Path $projectRoot "dist"
New-Item -ItemType Directory -Force -Path $buildDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $distributionDirectory | Out-Null

& python -c @"
from pathlib import Path
from PIL import Image
source = Image.open(Path('icons/netcheck-1024.png')).convert('RGBA')
source.save(Path('build/netcheck.ico'), sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
"@

$versionParts = $version.Split('.')
while ($versionParts.Count -lt 4) {
    $versionParts += "0"
}
$numericVersion = ($versionParts[0..3] -join ', ')
$versionInfo = @"
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=($numericVersion),
    prodvers=($numericVersion),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'DITIS Group'),
        StringStruct('FileDescription', 'NetCheck network diagnostic tool'),
        StringStruct('FileVersion', '$version'),
        StringStruct('InternalName', 'NetCheck'),
        StringStruct('LegalCopyright', 'Copyright 2026 Serhii Dralo'),
        StringStruct('OriginalFilename', 'NetCheck.exe'),
        StringStruct('ProductName', 'NetCheck'),
        StringStruct('ProductVersion', '$version')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"@
$versionInfo | Set-Content -Encoding UTF8 (Join-Path $buildDirectory "windows-version-info.txt")

& python -m PyInstaller --noconfirm --clean "NetCheck-Windows.spec"

$application = Join-Path $distributionDirectory "NetCheck\NetCheck.exe"
if (-not (Test-Path $application)) {
    throw "Windows application was not created."
}
& $application --version
if ($LASTEXITCODE -ne 0) {
    throw "Packaged NetCheck version check failed."
}
$env:QT_QPA_PLATFORM = "offscreen"
& $application --smoke-test
if ($LASTEXITCODE -ne 0) {
    throw "Packaged NetCheck UI smoke test failed."
}

$archiveName = "NetCheck-$version-windows-x86_64.zip"
$archivePath = Join-Path $distributionDirectory $archiveName
if (Test-Path $archivePath) {
    Remove-Item -Force $archivePath
}
Compress-Archive -Path (Join-Path $distributionDirectory "NetCheck\*") -DestinationPath $archivePath
$checksum = (Get-FileHash -Algorithm SHA256 $archivePath).Hash.ToLowerInvariant()
"$checksum  $archiveName" | Set-Content -Encoding ASCII "$archivePath.sha256"

Write-Host "Created $archivePath"
Write-Host "SHA-256 $checksum"
