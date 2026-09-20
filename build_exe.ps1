param(
    [string]$Python = "python",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$buildPython = Join-Path $PSScriptRoot ".venv-build\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $buildPython)) {
    & $Python -m venv .venv-build
    if ($LASTEXITCODE -ne 0) { throw "Could not create the build environment." }
}
if (-not $SkipInstall) {
    & $buildPython -m pip install ".[dev,build]"
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
}

& $buildPython -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
& $buildPython -m PyInstaller --noconfirm --clean AGtest-framework.spec
if ($LASTEXITCODE -ne 0) { throw "EXE build failed." }
& $buildPython scripts/check_built_exe.py
if ($LASTEXITCODE -ne 0) { throw "Standalone EXE verification failed." }

& $buildPython -m pip freeze | Set-Content -Encoding UTF8 build/build-environment.txt
$exeHash = (Get-FileHash -LiteralPath "dist/AGtest-framework.exe" -Algorithm SHA256).Hash.ToLowerInvariant()
"$exeHash  AGtest-framework.exe" | Set-Content -Encoding ASCII dist/SHA256SUMS.txt
Write-Host "Ready: $PSScriptRoot\dist\AGtest-framework.exe"
Write-Host "Release checksum: $PSScriptRoot\dist\SHA256SUMS.txt"
