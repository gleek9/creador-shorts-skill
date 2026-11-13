# Instala la plantilla "Shorts Animados" en Windows DENTRO de esta carpeta (Node portatil, Python con uv y motor de video).
# Uso: powershell -ExecutionPolicy Bypass -File instalar\instalar.ps1
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Raiz = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Raiz
$NodeV = "v24.22.0"
Write-Host "== Shorts Animados: instalacion (Windows) =="

$nodeDir = Join-Path $Raiz "node"
if (-not (Test-Path (Join-Path $nodeDir "node.exe"))) {
  Write-Host "Descargo Node $NodeV ..."
  $zip = Join-Path $Raiz "node.zip"
  Invoke-WebRequest -Uri "https://nodejs.org/dist/$NodeV/node-$NodeV-win-x64.zip" -OutFile $zip -UseBasicParsing
  Expand-Archive $zip -DestinationPath (Join-Path $Raiz "node-tmp") -Force
  Move-Item (Join-Path $Raiz "node-tmp\node-$NodeV-win-x64") $nodeDir
  Remove-Item $zip, (Join-Path $Raiz "node-tmp") -Recurse -Force
}
$env:Path = "$nodeDir;" + $env:Path

Write-Host "Instalo el motor de video (unos minutos la primera vez)..."
& (Join-Path $nodeDir "npm.cmd") ci --no-audit --no-fund --loglevel=error
if ($LASTEXITCODE -ne 0) { throw "no se pudo instalar el motor de video" }
& (Join-Path $nodeDir "npx.cmd") remotion browser ensure | Out-Null

$uvDir = Join-Path $Raiz "uv"
$uv = Join-Path $uvDir "uv.exe"
if (-not (Test-Path $uv)) {
  Write-Host "Descargo uv (gestor de Python)..."
  $zipUv = Join-Path $Raiz "uv.zip"
  Invoke-WebRequest -Uri "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip" -OutFile $zipUv -UseBasicParsing
  Expand-Archive $zipUv -DestinationPath $uvDir -Force
  Remove-Item $zipUv -Force
}
Write-Host "Preparo Python y las librerias..."
if (-not (Test-Path ".venv\Scripts\python.exe")) { & $uv venv .venv --python 3.12 --quiet }
if ($LASTEXITCODE -ne 0) { throw "no se pudo preparar Python" }
& $uv pip install --quiet --python .venv\Scripts\python.exe -r instalar\requirements.txt
if ($LASTEXITCODE -ne 0) { throw "no se pudieron instalar las librerias de Python" }
Write-Host "Descargo el modelo que escucha la voz (~500 MB, solo la primera vez)..."
try { & .venv\Scripts\python.exe -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8')" | Out-Null } catch { Write-Host "  (se descargara con la primera voz)" }

Set-Content -Path (Join-Path $Raiz "shorts.cmd") -Encoding ASCII -Value "@echo off`r`ncd /d `"%~dp0`"`r`nset PATH=%~dp0node;%PATH%`r`n.venv\Scripts\python.exe herramientas\shorts.py %*"
Write-Host ""
& (Join-Path $Raiz "shorts.cmd") comprobar
